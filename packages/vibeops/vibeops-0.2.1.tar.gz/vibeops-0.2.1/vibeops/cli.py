#!/usr/bin/env python3
"""
VibeOps CLI - Configure Cursor to use VibeOps MCP server
"""

import os
import json
import click
import platform
import requests
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()

def get_cursor_config_dir():
    """Get the Cursor configuration directory based on the operating system"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / ".cursor"
    elif system == "Windows":
        return Path.home() / ".cursor"
    elif system == "Linux":
        return Path.home() / ".cursor"
    else:
        console.print(f"[red]Unsupported operating system: {system}[/red]")
        return None

def test_server_connection(server_url):
    """Test connection to a remote MCP server"""
    try:
        health_url = f"{server_url.rstrip('/')}/health"
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"Server returned status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)

@click.group()
def cli():
    """VibeOps CLI - Configure Cursor for DevOps automation"""
    pass

@cli.command()
@click.option('--server-url', help='URL of remote VibeOps MCP server', default='http://20.83.174.151')
def init(server_url):
    """Initialize VibeOps MCP server configuration in Cursor"""
    
    console.print(Panel.fit(
        "[bold blue]VibeOps MCP Server Configuration[/bold blue]\n"
        "This will configure Cursor to connect to the VibeOps Universal Server",
        border_style="blue"
    ))
    
    console.print(f"[green]Configuring Cursor to use VibeOps Universal Server: {server_url}[/green]")
    
    # Test server connection
    console.print(f"[yellow]Testing connection to {server_url}...[/yellow]")
    success, result = test_server_connection(server_url)
    if success:
        console.print(f"[green]✓ Server connection successful![/green]")
        server_info = result.get('server', 'VibeOps MCP Server')
        console.print(f"Server info: {server_info}")
    else:
        console.print(f"[red]✗ Failed to connect to server: {result}[/red]")
        if not Confirm.ask("Continue anyway?"):
            return
    
    # Get Cursor config directory
    cursor_dir = get_cursor_config_dir()
    if not cursor_dir:
        return
    
    # Create directory if it doesn't exist
    cursor_dir.mkdir(parents=True, exist_ok=True)
    
    # MCP servers config file
    mcp_config_file = cursor_dir / "mcp.json"
    
    # Load existing config or create new
    if mcp_config_file.exists():
        try:
            with open(mcp_config_file, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}
    
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Configure remote server connection using HTTP transport
    config["mcpServers"]["vibeops"] = {
        "command": "python",
        "args": [
            "-c",
            f"""
import sys
import json
import requests
import uuid
from datetime import datetime

# Simple HTTP MCP client for remote VibeOps server
class RemoteVibeOpsClient:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
    
    def call_tool(self, tool_name, **kwargs):
        try:
            response = self.session.post(
                f'{{self.server_url}}/mcp/tools/{{tool_name}}',
                json=kwargs,
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {{"error": str(e)}}

# Initialize client
client = RemoteVibeOpsClient('{server_url}')

# Handle MCP protocol
while True:
    try:
        line = sys.stdin.readline()
        if not line:
            break
        
        request = json.loads(line.strip())
        
        if request.get('method') == 'tools/list':
            # Return available tools
            tools = [
                {{
                    "name": "deploy_application_universal",
                    "description": "Deploy applications to AWS and Vercel with user credentials",
                    "inputSchema": {{
                        "type": "object",
                        "properties": {{
                            "aws_access_key": {{"type": "string", "description": "AWS Access Key ID"}},
                            "aws_secret_key": {{"type": "string", "description": "AWS Secret Access Key"}},
                            "vercel_token": {{"type": "string", "description": "Vercel API token (optional)"}},
                            "repo_url": {{"type": "string", "description": "Git repository URL (optional)"}},
                            "app_name": {{"type": "string", "description": "Application name"}},
                            "deployment_platform": {{"type": "string", "description": "Platform: auto, aws, vercel, fullstack"}},
                            "environment": {{"type": "string", "description": "Environment: dev, staging, prod"}}
                        }},
                        "required": ["aws_access_key", "aws_secret_key"]
                    }}
                }},
                {{
                    "name": "get_deployment_advice",
                    "description": "Get AI-powered deployment advice and planning",
                    "inputSchema": {{
                        "type": "object",
                        "properties": {{
                            "project_description": {{"type": "string", "description": "Description of the project"}},
                            "tech_stack": {{"type": "string", "description": "Technologies used"}},
                            "requirements": {{"type": "string", "description": "Special requirements"}}
                        }},
                        "required": ["project_description"]
                    }}
                }},
                {{
                    "name": "analyze_deployment_error",
                    "description": "Analyze deployment errors with AI assistance",
                    "inputSchema": {{
                        "type": "object",
                        "properties": {{
                            "error_message": {{"type": "string", "description": "Error message or log"}},
                            "deployment_context": {{"type": "string", "description": "Deployment context"}}
                        }},
                        "required": ["error_message"]
                    }}
                }},
                {{
                    "name": "get_deployment_status",
                    "description": "Get status of a deployment",
                    "inputSchema": {{
                        "type": "object",
                        "properties": {{
                            "deployment_id": {{"type": "string", "description": "Deployment ID"}}
                        }},
                        "required": ["deployment_id"]
                    }}
                }}
            ]
            
            response = {{
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {{"tools": tools}}
            }}
            
        elif request.get('method') == 'tools/call':
            # Call the tool on remote server
            tool_name = request.get('params', {{}}).get('name')
            arguments = request.get('params', {{}}).get('arguments', {{}})
            
            result = client.call_tool(tool_name, **arguments)
            
            response = {{
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {{
                    "content": [
                        {{
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }}
                    ]
                }}
            }}
            
        else:
            response = {{
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {{"code": -32601, "message": "Method not found"}}
            }}
        
        print(json.dumps(response))
        sys.stdout.flush()
        
    except Exception as e:
        error_response = {{
            "jsonrpc": "2.0",
            "id": request.get("id") if 'request' in locals() else None,
            "error": {{"code": -32603, "message": str(e)}}
        }}
        print(json.dumps(error_response))
        sys.stdout.flush()
"""
        ],
        "env": {
            "MCP_SERVER_URL": server_url,
            "PYTHONPATH": os.environ.get("PYTHONPATH", "")
        }
    }
    
    # Save configuration
    with open(mcp_config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    console.print(f"[green]✓ Configuration saved to {mcp_config_file}[/green]")
    console.print(f"[green]✓ Configured Cursor to connect to: {server_url}[/green]")
    console.print("[blue]💡 The server supports AI-powered deployment advice and error analysis![/blue]")
    
    # Instructions
    console.print(Panel(
        "[bold]Next Steps:[/bold]\n\n"
        "1. Restart Cursor to load the new MCP configuration\n"
        "2. Open a project in Cursor\n"
        "3. Chat with Cursor and use VibeOps tools:\n"
        "   • Deploy applications to AWS and Vercel\n"
        "   • Get AI-powered deployment advice\n"
        "   • Analyze deployment errors\n"
        "   • Check deployment status\n\n"
        f"[dim]Server URL: {server_url}[/dim]\n"
        "[dim]You'll provide your AWS/Vercel credentials when deploying[/dim]",
        title="Setup Complete!",
        border_style="green"
    ))

@cli.command()
def status():
    """Check VibeOps configuration status"""
    cursor_dir = get_cursor_config_dir()
    if not cursor_dir:
        return
    
    mcp_config_file = cursor_dir / "mcp.json"
    
    console.print(Panel.fit("[bold]VibeOps Configuration Status[/bold]", border_style="blue"))
    
    # Check MCP configuration
    if mcp_config_file.exists():
        try:
            with open(mcp_config_file, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" in config and "vibeops" in config["mcpServers"]:
                vibeops_config = config["mcpServers"]["vibeops"]
                console.print("[green]✓ VibeOps MCP server configured[/green]")
                
                server_url = vibeops_config.get("env", {}).get("MCP_SERVER_URL", "Unknown")
                console.print(f"  Server URL: {server_url}")
                
                # Test remote server
                if server_url != "Unknown":
                    success, result = test_server_connection(server_url)
                    if success:
                        console.print(f"  [green]✓ Server is accessible[/green]")
                    else:
                        console.print(f"  [red]✗ Server not accessible: {result}[/red]")
            else:
                console.print("[red]✗ VibeOps not configured in MCP servers[/red]")
        except json.JSONDecodeError:
            console.print("[red]✗ Invalid MCP configuration file[/red]")
    else:
        console.print("[red]✗ MCP configuration file not found[/red]")
    
    # Configuration paths
    console.print(f"\n[dim]Configuration directory: {cursor_dir}[/dim]")
    console.print(f"[dim]MCP config file: {mcp_config_file}[/dim]")

@cli.command()
@click.argument('server_url')
def test_server(server_url):
    """Test connection to a remote VibeOps MCP server"""
    console.print(f"[blue]Testing connection to {server_url}...[/blue]")
    
    success, result = test_server_connection(server_url)
    
    if success:
        console.print(f"[green]✓ Connection successful![/green]")
        console.print(f"Server response: {json.dumps(result, indent=2)}")
    else:
        console.print(f"[red]✗ Connection failed: {result}[/red]")

if __name__ == "__main__":
    cli() 