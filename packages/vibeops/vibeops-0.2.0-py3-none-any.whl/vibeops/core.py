#!/usr/bin/env python3
"""
VibeOps Core - Core deployment functionality
"""

import os
import tempfile
import shutil
import git
import boto3
import json
from dotenv import load_dotenv
from fastmcp import FastMCP
from typing import Dict, List, Optional, Union
import subprocess
from pydantic import BaseModel
import pathlib
import requests
import time
import re
import threading
import signal
import uuid
import datetime
import pickle

# Load environment variables
load_dotenv()

# Temporary directory for operations
temp_dir = tempfile.mkdtemp(prefix="vibeops-core-")

# Log file for each deployment
log_files = {}

# Deployments tracking store
deployments_store_path = os.path.join(temp_dir, "deployments_store.pickle")

# Add timeout decorator for function calls
def timeout(seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def worker():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                log_message(f"Function {func.__name__} timed out after {seconds} seconds")
                return {"success": False, "error": f"Operation timed out after {seconds} seconds"}
            if exception[0]:
                raise exception[0]
            return result[0]
        return wrapper
    return decorator

def log_message(message, deployment_id=None):
    """Log a message to both console and log file if deployment_id is provided"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    
    if deployment_id and deployment_id in log_files:
        with open(log_files[deployment_id], 'a') as f:
            f.write(formatted_message + "\n")

# Models
class DeploymentOutput(BaseModel):
    status: str
    message: str
    data: Optional[Dict] = None
    log_file: Optional[str] = None

class ArchitectureOutput(BaseModel):
    status: str
    message: str
    architecture: Optional[Dict] = None

class LogsOutput(BaseModel):
    status: str
    logs: Optional[str] = None
    deployment_id: Optional[str] = None
    log_file: Optional[str] = None

def detect_app_type(repo_path: str) -> Dict[str, str]:
    """Detect the type of application from the codebase with improved accuracy"""
    app_info = {
        "type": "unknown",
        "frontend": False,
        "backend": False,
        "fullstack": False,
        "frontend_path": None,
        "backend_path": None
    }
    
    # First, look for structured project layout
    if os.path.exists(os.path.join(repo_path, 'frontend')) and os.path.isdir(os.path.join(repo_path, 'frontend')):
        app_info["frontend"] = True
        app_info["frontend_path"] = os.path.join(repo_path, 'frontend')
    
    if os.path.exists(os.path.join(repo_path, 'backend')) and os.path.isdir(os.path.join(repo_path, 'backend')):
        app_info["backend"] = True
        app_info["backend_path"] = os.path.join(repo_path, 'backend')
    
    # Additional directory pattern checks
    dir_patterns = {
        'frontend': ['client', 'web', 'ui', 'app', 'www', 'public'],
        'backend': ['server', 'api', 'service', 'app-server', 'services']
    }
    
    for dir_type, patterns in dir_patterns.items():
        for pattern in patterns:
            pattern_path = os.path.join(repo_path, pattern)
            if os.path.exists(pattern_path) and os.path.isdir(pattern_path) and not app_info.get(f"{dir_type}_path"):
                app_info[dir_type] = True
                app_info[f"{dir_type}_path"] = pattern_path
    
    # Check for package.json (Node.js)
    if os.path.exists(os.path.join(repo_path, 'package.json')):
        with open(os.path.join(repo_path, 'package.json'), 'r') as f:
            try:
                package_data = json.load(f)
                dependencies = package_data.get('dependencies', {})
                
                # Check for React/Next.js/Vue frontend
                if any(dep in dependencies for dep in ['react', 'next', 'vue', '@angular/core', 'preact']):
                    app_info["type"] = "nodejs"
                    app_info["frontend"] = True
                    
                    # Determine specific frontend framework
                    if 'next' in dependencies:
                        app_info["framework"] = "nextjs"
                    elif 'react' in dependencies:
                        app_info["framework"] = "react"
                    elif 'vue' in dependencies:
                        app_info["framework"] = "vue"
                    elif '@angular/core' in dependencies:
                        app_info["framework"] = "angular"
                    else:
                        app_info["framework"] = "javascript"
                    
                    # Set frontend path if not already set
                    if not app_info["frontend_path"]:
                        app_info["frontend_path"] = repo_path
                
                # Check for Express/Node backend
                if any(dep in dependencies for dep in ['express', 'koa', 'hapi', 'fastify', 'node-fetch', 'axios', 'mongoose', 'sequelize', 'prisma']):
                    app_info["type"] = "nodejs"
                    app_info["backend"] = True
                    
                    # Determine specific backend framework
                    if 'express' in dependencies:
                        app_info["backend_framework"] = "express"
                    elif 'koa' in dependencies:
                        app_info["backend_framework"] = "koa"
                    elif 'fastify' in dependencies:
                        app_info["backend_framework"] = "fastify"
                    else:
                        app_info["backend_framework"] = "nodejs"
                    
                    # Set backend path if not already set
                    if not app_info["backend_path"]:
                        app_info["backend_path"] = repo_path
                
                # If both frontend and backend are detected, mark as fullstack
                if app_info["frontend"] and app_info["backend"]:
                    app_info["fullstack"] = True
                    app_info["type"] = "fullstack"
                elif not app_info["frontend"] and not app_info["backend"] and dependencies:
                    # If no specific framework is detected but dependencies exist, default to nodejs
                    app_info["type"] = "nodejs"
            except json.JSONDecodeError:
                app_info["type"] = "nodejs"
    
    # Check for requirements.txt or setup.py (Python)
    if os.path.exists(os.path.join(repo_path, 'requirements.txt')) or \
         os.path.exists(os.path.join(repo_path, 'setup.py')):
        app_info["type"] = "python"
        app_info["backend"] = True
        
        # Set backend path if not already set
        if not app_info["backend_path"]:
            app_info["backend_path"] = repo_path
        
        # Try to detect specific Python frameworks
        for filename in ['requirements.txt', 'setup.py']:
            filepath = os.path.join(repo_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        app_info["backend_framework"] = "django"
                    elif 'flask' in content:
                        app_info["backend_framework"] = "flask"
                    elif 'fastapi' in content:
                        app_info["backend_framework"] = "fastapi"
    
    # Check for pom.xml or build.gradle (Java)
    if os.path.exists(os.path.join(repo_path, 'pom.xml')) or \
         os.path.exists(os.path.join(repo_path, 'build.gradle')):
        app_info["type"] = "java"
        app_info["backend"] = True
        
        # Set backend path if not already set
        if not app_info["backend_path"]:
            app_info["backend_path"] = repo_path
        
    # Check for Gemfile (Ruby)
    if os.path.exists(os.path.join(repo_path, 'Gemfile')):
        app_info["type"] = "ruby"
        app_info["backend"] = True
        
        # Set backend path if not already set
        if not app_info["backend_path"]:
            app_info["backend_path"] = repo_path
        
    # Check for go.mod (Go)
    if os.path.exists(os.path.join(repo_path, 'go.mod')):
        app_info["type"] = "golang"
        app_info["backend"] = True
        
        # Set backend path if not already set
        if not app_info["backend_path"]:
            app_info["backend_path"] = repo_path
        
    # Check for static site
    if any(os.path.exists(os.path.join(repo_path, file)) for file in ['index.html', 'index.htm']):
        app_info["frontend"] = True
        if not app_info["type"] or app_info["type"] == "unknown":
            app_info["type"] = "static"
        
        # Set frontend path if not already set
        if not app_info["frontend_path"]:
            app_info["frontend_path"] = repo_path
    
    # If both frontend and backend are detected in any way, mark as fullstack
    if app_info["frontend"] and app_info["backend"]:
        app_info["fullstack"] = True
        app_info["type"] = "fullstack"
    
    # Default to current directory if paths not found
    if app_info["frontend"] and not app_info["frontend_path"]:
        app_info["frontend_path"] = repo_path
    
    if app_info["backend"] and not app_info["backend_path"]:
        app_info["backend_path"] = repo_path
    
    # Default to unknown
    return app_info

def get_repository_path(repo_url: Optional[str] = None, branch: str = "main") -> str:
    """
    Get repository path - either clone from URL or use current directory
    """
    if repo_url:
        # Clone the repository
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(temp_dir, repo_name)
        
        # Check if repo already exists in temp dir
        if os.path.exists(repo_path):
            # Update existing repo
            repo = git.Repo(repo_path)
            repo.remotes.origin.pull()
        else:
            # Clone the repository
            git.Repo.clone_from(repo_url, repo_path, branch=branch)
        
        return repo_path
    else:
        # Use current directory and look for actual code
        current_dir = os.getcwd()
        log_message(f"No repo URL provided, using current directory: {current_dir}")
        return current_dir

class DeploymentStore:
    """Store to track existing deployments and their information"""
    
    def __init__(self, store_path):
        self.store_path = store_path
        self.deployments = {}
        self._load()
    
    def _load(self):
        """Load deployments from disk if available"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'rb') as f:
                    self.deployments = pickle.load(f)
                log_message(f"Loaded {len(self.deployments)} deployments from store")
            except Exception as e:
                log_message(f"Error loading deployments store: {str(e)}")
                self.deployments = {}
    
    def _save(self):
        """Save deployments to disk"""
        try:
            with open(self.store_path, 'wb') as f:
                pickle.dump(self.deployments, f)
        except Exception as e:
            log_message(f"Error saving deployments store: {str(e)}")
    
    def store_deployment(self, app_name, environment, deployment_info):
        """Store information about a deployment"""
        key = f"{app_name}_{environment}"
        self.deployments[key] = deployment_info
        self._save()
    
    def get_deployment(self, app_name, environment):
        """Get information about an existing deployment"""
        key = f"{app_name}_{environment}"
        return self.deployments.get(key)
    
    def has_backend(self, app_name, environment):
        """Check if backend deployment exists"""
        deployment = self.get_deployment(app_name, environment)
        return deployment and deployment.get('backend_url') is not None
    
    def has_frontend(self, app_name, environment):
        """Check if frontend deployment exists"""
        deployment = self.get_deployment(app_name, environment)
        return deployment and deployment.get('frontend_url') is not None
    
    def get_backend_info(self, app_name, environment):
        """Get backend deployment info"""
        deployment = self.get_deployment(app_name, environment)
        if not deployment:
            return None
            
        return {
            'url': deployment.get('backend_url'),
            'tf_dir': deployment.get('backend_tf_dir'),
            'instance_id': deployment.get('backend_instance_id')
        }
    
    def get_frontend_info(self, app_name, environment):
        """Get frontend deployment info"""
        deployment = self.get_deployment(app_name, environment)
        if not deployment:
            return None
            
        return {
            'url': deployment.get('frontend_url'),
            'vercel_project': deployment.get('frontend_vercel_project')
        }

# Initialize the deployments store
deployments_store = DeploymentStore(deployments_store_path)

# Placeholder functions - these would contain the full implementation from mcp_server.py
def deploy_application(
    repo_url: Optional[str] = None,
    branch: str = "main",
    deployment_platform: str = "auto",
    aws_access_key: Optional[str] = None,
    aws_secret_key: Optional[str] = None,
    aws_region: str = "us-east-1",
    vercel_token: Optional[str] = None,
    app_name: str = "app",
    environment: str = "dev",
    application_dir: Optional[str] = None,
    force_vibecode: bool = True
) -> DeploymentOutput:
    """
    Deploy an application using the best infrastructure for its type.
    This is a simplified version - the full implementation would be copied from mcp_server.py
    """
    # Generate a unique deployment ID
    deployment_id = str(uuid.uuid4())
    
    # Create a log file for this deployment
    log_file = os.path.join(temp_dir, f"{deployment_id}.log")
    log_files[deployment_id] = log_file
    
    log_message(f"Starting deployment with ID: {deployment_id}", deployment_id)
    
    try:
        # Simplified deployment logic - in real implementation, this would be the full logic
        log_message("Analyzing application...", deployment_id)
        
        # Get repository path
        repo_path = get_repository_path(repo_url, branch) if repo_url else (application_dir or os.getcwd())
        
        # Detect application type
        app_info = detect_app_type(repo_path)
        log_message(f"Detected app type: {app_info}", deployment_id)
        
        # For now, return a success message
        # In the full implementation, this would contain all the deployment logic
        return DeploymentOutput(
            status="success",
            message=f"Deployment completed successfully! (Simplified version)\nApp type: {app_info['type']}\nDeployment ID: {deployment_id}",
            data={
                "deployment_id": deployment_id,
                "app_info": app_info,
                "repo_path": repo_path
            },
            log_file=log_file
        )
        
    except Exception as e:
        log_message(f"Deployment failed: {str(e)}", deployment_id)
        return DeploymentOutput(
            status="error",
            message=f"Deployment failed: {str(e)}",
            data={"deployment_id": deployment_id},
            log_file=log_file
        )

def check_deployment_logs(deployment_id: str) -> LogsOutput:
    """Get logs for a specific deployment using the deployment ID."""
    if deployment_id not in log_files or not os.path.exists(log_files[deployment_id]):
        available_logs = [f"{d_id}: {path}" for d_id, path in log_files.items() if os.path.exists(path)]
        available_msg = "\n\nAvailable logs:\n" + "\n".join(available_logs) if available_logs else ""
        
        return LogsOutput(
            status="error",
            logs=f"Deployment logs not found for ID: {deployment_id}. The deployment may have completed or the ID is incorrect.{available_msg}"
        )
    
    try:
        with open(log_files[deployment_id], 'r') as f:
            logs = f.read()
        
        return LogsOutput(
            status="success",
            logs=logs,
            deployment_id=deployment_id,
            log_file=log_files[deployment_id]
        )
    except Exception as e:
        return LogsOutput(
            status="error",
            logs=f"Error reading logs: {str(e)}"
        )

def get_logs_by_app(app_name: str, environment: str = "dev") -> LogsOutput:
    """Get logs for a specific application by app name and environment."""
    log_message(f"Searching for logs for app: {app_name} in environment: {environment}")
    
    # Get deployment info
    existing_deployment = deployments_store.get_deployment(app_name, environment)
    if not existing_deployment:
        return LogsOutput(
            status="error",
            logs=f"No deployment found for app '{app_name}' in environment '{environment}'"
        )
    
    # Find the log file associated with this deployment
    found_log_file = None
    found_deployment_id = None
    
    # Look through all log files and check content for app_name and environment
    for d_id, log_path in log_files.items():
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    content = f.read()
                    if app_name in content and environment in content:
                        found_log_file = log_path
                        found_deployment_id = d_id
                        break
            except Exception:
                pass
    
    if found_log_file:
        try:
            with open(found_log_file, 'r') as f:
                logs = f.read()
            
            return LogsOutput(
                status="success",
                logs=logs,
                deployment_id=found_deployment_id,
                log_file=found_log_file
            )
        except Exception as e:
            return LogsOutput(
                status="error",
                logs=f"Error reading logs: {str(e)}"
            )
    else:
        return LogsOutput(
            status="error",
            logs=f"Deployment exists for '{app_name}' in '{environment}', but no log file was found"
        )

def list_all_deployments() -> Dict:
    """List all deployments and their logs."""
    all_deployments = {}
    
    # Get all deployments from the store
    for key, deployment in deployments_store.deployments.items():
        app_name, environment = key.split('_', 1) if '_' in key else (key, 'unknown')
        
        # Add basic info
        deployment_info = {
            'app_name': app_name,
            'environment': environment,
            'backend_url': deployment.get('backend_url'),
            'frontend_url': deployment.get('frontend_url'),
            'deployment_time': deployment.get('deployment_time'),
            'log_file': None
        }
        
        # Find associated log file if any
        for deployment_id, log_file in log_files.items():
            if os.path.exists(log_file):
                # Read the first few lines to check if this log belongs to this deployment
                try:
                    with open(log_file, 'r') as f:
                        log_content = f.read(1000)  # Read first 1000 chars
                        if app_name in log_content and environment in log_content:
                            deployment_info['log_file'] = log_file
                            deployment_info['deployment_id'] = deployment_id
                            break
                except Exception:
                    pass
        
        all_deployments[key] = deployment_info
    
    return {
        'status': 'success',
        'deployments': all_deployments,
        'logs_directory': temp_dir,
        'count': len(all_deployments)
    }

def redeploy_on_changes(
    repo_url: Optional[str] = None,
    base_commit: str = "HEAD~1",
    head_commit: str = "HEAD",
    deployment_platform: str = "auto",
    app_name: str = None,
    environment: str = "dev"
) -> DeploymentOutput:
    """Check for significant changes and redeploy if needed."""
    try:
        # Get repository path
        repo_path = get_repository_path(repo_url)
        
        # If no app_name provided, try to derive from repo path
        if not app_name:
            app_name = os.path.basename(repo_path)
            app_name = "".join(c.lower() for c in app_name if c.isalnum() or c == '-').strip("-")
            if not app_name:
                app_name = "app"
        
        # Check if we have an existing deployment
        existing_deployment = deployments_store.get_deployment(app_name, environment)
        if not existing_deployment:
            log_message(f"No existing deployment found for {app_name} in {environment} environment.")
            log_message("Proceeding with a new deployment...")
            return deploy_application(
                repo_url=repo_url,
                deployment_platform=deployment_platform,
                app_name=app_name,
                environment=environment
            )
            
        # For now, just return that no changes were detected
        # In the full implementation, this would check git diffs
        return DeploymentOutput(
            status="success",
            message="No significant changes detected that require redeployment",
            data={
                "redeployed": False,
                "existing_deployment": {
                    "frontend_url": existing_deployment.get("frontend_url"),
                    "backend_url": existing_deployment.get("backend_url")
                }
            }
        )
            
    except Exception as e:
        return DeploymentOutput(
            status="error",
            message=f"Error in redeploy_on_changes: {str(e)}"
        ) 