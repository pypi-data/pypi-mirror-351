#!/usr/bin/env python3
"""
VibeOps MCP Server - Universal deployment server for all users
"""

import os
import sys
import asyncio
import argparse
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables (only for server config, not user credentials)
load_dotenv()

# Import FastAPI and SSE dependencies
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse
    from sse_starlette.sse import EventSourceResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Import MCP and core functionality
from fastmcp import FastMCP
from .core import (
    deploy_application as core_deploy_application,
    check_deployment_logs,
    get_logs_by_app,
    list_all_deployments,
    redeploy_on_changes,
    DeploymentOutput,
    log_message
)

# Temporary directory for operations
import tempfile
temp_dir = tempfile.mkdtemp(prefix="vibeops-")

class VibeOpsServer:
    """Universal MCP Server for all users - stateless and multi-tenant"""
    
    def __init__(self, mode="stdio"):
        self.mode = mode
        self.mcp = FastMCP("VibeOps DevOps Automation")
        self.active_deployments = {}
        self._setup_tools()
    
    def _setup_tools(self):
        """Setup MCP tools that accept user credentials as parameters"""
        
        @self.mcp.tool()
        def deploy_application_universal(
            # User credentials (required)
            aws_access_key: str,
            aws_secret_key: str,
            vercel_token: Optional[str] = None,
            
            # Deployment parameters
            repo_url: Optional[str] = None,
            branch: str = "main",
            deployment_platform: str = "auto",
            aws_region: str = "us-east-1",
            app_name: str = "app",
            environment: str = "dev",
            application_dir: Optional[str] = None,
            force_vibecode: bool = False
        ) -> Dict:
            """
            Deploy an application using the best infrastructure for its type.
            
            This is the universal version that accepts user credentials as parameters.
            All users can use this server by providing their own credentials.
            """
            deployment_id = str(uuid.uuid4())
            
            # Validate required credentials
            if not aws_access_key or not aws_secret_key:
                return {
                    "status": "error",
                    "message": "AWS credentials are required. Please provide aws_access_key and aws_secret_key.",
                    "deployment_id": deployment_id
                }
            
            if self.mode in ["sse", "http"]:
                # For SSE mode, start async deployment with progress tracking
                self.active_deployments[deployment_id] = {
                    "status": "starting",
                    "progress": 0,
                    "messages": [],
                    "start_time": datetime.datetime.now(),
                    "result": None,
                    "user_id": f"user_{hash(aws_access_key) % 10000}"  # Simple user identification
                }
                
                # Start deployment in background
                asyncio.create_task(self._deploy_with_progress(
                    deployment_id,
                    repo_url=repo_url,
                    branch=branch,
                    deployment_platform=deployment_platform,
                    aws_access_key=aws_access_key,
                    aws_secret_key=aws_secret_key,
                    aws_region=aws_region,
                    vercel_token=vercel_token,
                    app_name=app_name,
                    environment=environment,
                    application_dir=application_dir,
                    force_vibecode=force_vibecode
                ))
                
                return {
                    "status": "started",
                    "deployment_id": deployment_id,
                    "message": f"Deployment started. Use deployment ID {deployment_id} to track progress.",
                    "stream_url": f"/deployments/{deployment_id}/stream" if self.mode == "sse" else None
                }
            else:
                # For STDIO mode, run synchronously
                return self._deploy_sync(
                    repo_url=repo_url,
                    branch=branch,
                    deployment_platform=deployment_platform,
                    aws_access_key=aws_access_key,
                    aws_secret_key=aws_secret_key,
                    aws_region=aws_region,
                    vercel_token=vercel_token,
                    app_name=app_name,
                    environment=environment,
                    application_dir=application_dir,
                    force_vibecode=force_vibecode
                )
        
        @self.mcp.tool()
        def get_deployment_status(deployment_id: str) -> Dict:
            """Get the current status of a deployment"""
            if deployment_id in self.active_deployments:
                deployment = self.active_deployments[deployment_id]
                return {
                    "status": deployment["status"],
                    "progress": deployment["progress"],
                    "messages": deployment["messages"][-10:],  # Last 10 messages
                    "start_time": deployment["start_time"].isoformat(),
                    "result": deployment.get("result")
                }
            else:
                return {
                    "status": "not_found",
                    "message": "Deployment not found"
                }
        
        @self.mcp.tool()
        def list_active_deployments() -> Dict:
            """List all active deployments"""
            return {
                "active_deployments": [
                    {
                        "deployment_id": dep_id,
                        "status": dep["status"],
                        "progress": dep["progress"],
                        "start_time": dep["start_time"].isoformat(),
                        "user_id": dep.get("user_id", "unknown")
                    }
                    for dep_id, dep in self.active_deployments.items()
                ]
            }
        
        @self.mcp.tool()
        def check_deployment_logs_universal(deployment_id: str) -> Dict:
            """Get logs for a specific deployment using the deployment ID"""
            return check_deployment_logs(deployment_id).dict()
    
    async def _deploy_with_progress(self, deployment_id: str, **kwargs):
        """Deploy with real-time progress updates for SSE"""
        try:
            deployment = self.active_deployments[deployment_id]
            
            # Custom log function that updates progress
            def progress_log(message, progress=None):
                deployment["messages"].append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}")
                if progress is not None:
                    deployment["progress"] = progress
                log_message(message, deployment_id)
            
            # Update progress throughout deployment
            deployment["status"] = "analyzing"
            deployment["progress"] = 5
            progress_log("Starting deployment analysis...")
            
            # Call the actual deployment function with progress tracking
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: core_deploy_application(**kwargs)
            )
            
            deployment["progress"] = 100
            deployment["status"] = "completed" if result.status == "success" else "failed"
            deployment["result"] = result.dict() if hasattr(result, 'dict') else result.__dict__
            progress_log(f"Deployment completed with status: {result.status}")
            
        except Exception as e:
            deployment = self.active_deployments[deployment_id]
            deployment["status"] = "failed"
            deployment["progress"] = 100
            deployment["messages"].append(f"Deployment failed: {str(e)}")
            deployment["result"] = {"status": "error", "message": str(e)}
    
    def _deploy_sync(self, **kwargs):
        """Synchronous deployment for STDIO mode"""
        result = core_deploy_application(**kwargs)
        return result.dict() if hasattr(result, 'dict') else result.__dict__
    
    async def stream_deployment_progress(self, deployment_id: str):
        """Stream deployment progress via SSE"""
        if deployment_id not in self.active_deployments:
            yield {"event": "error", "data": json.dumps({"error": "Deployment not found"})}
            return
        
        deployment = self.active_deployments[deployment_id]
        last_message_count = 0
        
        while deployment["status"] not in ["completed", "failed"]:
            # Send progress update
            yield {
                "event": "progress",
                "data": json.dumps({
                    "status": deployment["status"],
                    "progress": deployment["progress"],
                    "messages": deployment["messages"][last_message_count:]
                })
            }
            
            last_message_count = len(deployment["messages"])
            await asyncio.sleep(1)
        
        # Send final status
        yield {
            "event": "complete",
            "data": json.dumps({
                "status": deployment["status"],
                "progress": deployment["progress"],
                "messages": deployment["messages"][last_message_count:],
                "result": deployment.get("result")
            })
        }
    
    def create_fastapi_app(self):
        """Create FastAPI app for HTTP/SSE mode"""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI dependencies not available. Install with: pip install fastapi uvicorn sse-starlette")
        
        app = FastAPI(title="VibeOps Universal MCP Server", version="0.1.0")
        
        @app.get("/")
        async def root():
            return {
                "message": "VibeOps Universal MCP Server",
                "version": "0.1.0",
                "mode": self.mode,
                "endpoints": {
                    "health": "/health",
                    "deployments": "/deployments",
                    "stream": "/deployments/{deployment_id}/stream",
                    "mcp_deploy": "/mcp/tools/deploy"
                }
            }
        
        @app.get("/deployments/{deployment_id}/stream")
        async def stream_deployment(deployment_id: str):
            return EventSourceResponse(
                self.stream_deployment_progress(deployment_id)
            )
        
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy", 
                "mode": self.mode, 
                "active_deployments": len(self.active_deployments),
                "server": "VibeOps Universal MCP Server"
            }
        
        @app.get("/deployments")
        async def list_deployments():
            return {
                "active": list(self.active_deployments.keys()),
                "count": len(self.active_deployments)
            }
        
        # Add MCP endpoints
        @app.post("/mcp/tools/deploy")
        async def deploy_endpoint(request: Request):
            data = await request.json()
            # Call the MCP tool
            result = deploy_application_universal(**data)
            return result
        
        return app
    
    async def run_sse_server(self, port: int = 8000):
        """Run the server in SSE mode"""
        app = self.create_fastapi_app()
        config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
        server = uvicorn.Server(config)
        print(f"🚀 VibeOps Universal MCP Server starting in {self.mode.upper()} mode on port {port}")
        print(f"📊 Health check: http://0.0.0.0:{port}/health")
        print(f"📋 Deployments: http://0.0.0.0:{port}/deployments")
        print(f"🌐 This server can be used by anyone with their own credentials!")
        await server.serve()
    
    def run_stdio_server(self):
        """Run the server in STDIO mode"""
        print("🚀 VibeOps Universal MCP Server starting in STDIO mode")
        print("🌐 This server can be used by anyone with their own credentials!")
        self.mcp.run()


async def main():
    """Main entry point for the server"""
    parser = argparse.ArgumentParser(description="VibeOps Universal MCP Server")
    parser.add_argument("--mode", choices=["stdio", "sse", "http"], 
                       default="stdio", help="Server mode")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port for HTTP/SSE mode")
    
    args = parser.parse_args()
    
    server = VibeOpsServer(mode=args.mode)
    
    if args.mode == "stdio":
        server.run_stdio_server()
    elif args.mode in ["sse", "http"]:
        await server.run_sse_server(args.port)


if __name__ == "__main__":
    if len(sys.argv) > 1 and any(arg in sys.argv for arg in ["--mode", "sse", "http"]):
        # Async mode for SSE/HTTP
        asyncio.run(main())
    else:
        # Sync mode for STDIO
        server = VibeOpsServer(mode="stdio")
        server.run_stdio_server() 