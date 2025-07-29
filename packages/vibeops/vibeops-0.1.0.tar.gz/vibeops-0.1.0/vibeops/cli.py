#!/usr/bin/env python3
"""
VibeOps CLI - Configure Cursor to use VibeOps MCP server
"""

import os
import json
import click
import getpass
import platform
import requests
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
import shutil
import subprocess
import sys

console = Console()

def get_cursor_config_dir():
    """Get the Cursor configuration directory based on the operating system"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage"
    elif system == "Windows":
        return Path(os.environ.get("APPDATA", "")) / "Cursor" / "User" / "globalStorage"
    elif system == "Linux":
        return Path.home() / ".config" / "Cursor" / "User" / "globalStorage"
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
@click.option('--server-url', help='URL of remote VibeOps MCP server (e.g., https://your-server.com)')
@click.option('--mode', type=click.Choice(['local', 'remote']), help='Configuration mode')
def init(server_url, mode):
    """Initialize VibeOps MCP server configuration in Cursor"""
    
    console.print(Panel.fit(
        "[bold blue]VibeOps MCP Server Configuration[/bold blue]\n"
        "This will configure Cursor to use VibeOps for DevOps automation",
        border_style="blue"
    ))
    
    # Determine mode
    if not mode:
        if server_url:
            mode = 'remote'
        else:
            mode = Prompt.ask(
                "Configuration mode",
                choices=['local', 'remote'],
                default='local'
            )
    
    # Get server URL for remote mode
    if mode == 'remote' and not server_url:
        server_url = Prompt.ask(
            "Enter the URL of your VibeOps MCP server",
            default="https://your-vibeops-server.com"
        )
    
    # Test remote server connection
    if mode == 'remote':
        console.print(f"[yellow]Testing connection to {server_url}...[/yellow]")
        success, result = test_server_connection(server_url)
        if success:
            console.print(f"[green]✓ Server connection successful![/green]")
            console.print(f"Server info: {result.get('message', 'VibeOps MCP Server')}")
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
    mcp_config_file = cursor_dir / "mcp_servers.json"
    
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
    
    # Configure based on mode
    if mode == 'local':
        # Local STDIO configuration
        current_dir = os.getcwd()
        python_path = sys.executable
        
        config["mcpServers"]["vibeops"] = {
            "command": python_path,
            "args": ["-m", "vibeops.server"],
            "cwd": current_dir,
            "env": {
                "PATH": os.environ.get("PATH", "")
            }
        }
        
        console.print("[green]✓ Configured for local STDIO mode[/green]")
        
        # Collect and store credentials locally
        collect_credentials_local(cursor_dir)
        
    else:  # remote mode
        # Remote server configuration
        config["mcpServers"]["vibeops"] = {
            "command": "npx",
            "args": [
                "@modelcontextprotocol/server-fetch",
                server_url
            ],
            "env": {
                "MCP_SERVER_URL": server_url
            }
        }
        
        console.print(f"[green]✓ Configured for remote server: {server_url}[/green]")
        
        # For remote mode, we don't store credentials locally
        # Users will provide them when using the tools
        console.print("[yellow]Note: For remote mode, you'll provide credentials when deploying[/yellow]")
    
    # Save configuration
    with open(mcp_config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    console.print(f"[green]✓ Configuration saved to {mcp_config_file}[/green]")
    
    # Instructions
    console.print(Panel(
        "[bold]Next Steps:[/bold]\n\n"
        "1. Restart Cursor to load the new MCP configuration\n"
        "2. Open a project in Cursor\n"
        "3. Use the VibeOps tools for deployment:\n"
        "   • Deploy applications to AWS and Vercel\n"
        "   • Check deployment logs\n"
        "   • Monitor deployment status\n\n"
        f"[dim]Configuration mode: {mode}[/dim]" +
        (f"\n[dim]Server URL: {server_url}[/dim]" if mode == 'remote' else ""),
        title="Setup Complete!",
        border_style="green"
    ))

def collect_credentials_local(cursor_dir):
    """Collect and store credentials for local mode"""
    console.print("\n[bold]Credential Collection[/bold]")
    console.print("These credentials will be stored locally and used by the MCP server")
    
    # Create .env file for credentials
    env_file = cursor_dir / ".vibeops.env"
    
    credentials = {}
    
    # AWS Credentials
    console.print("\n[bold blue]AWS Credentials[/bold blue] (Required for backend deployments)")
    aws_access_key = Prompt.ask("AWS Access Key ID", password=False)
    aws_secret_key = Prompt.ask("AWS Secret Access Key", password=True)
    aws_region = Prompt.ask("AWS Region", default="us-east-1")
    
    credentials.update({
        "AWS_ACCESS_KEY_ID": aws_access_key,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key,
        "AWS_DEFAULT_REGION": aws_region
    })
    
    # Vercel Token
    console.print("\n[bold blue]Vercel Token[/bold blue] (Required for frontend deployments)")
    vercel_token = Prompt.ask("Vercel Token", password=True)
    credentials["VERCEL_TOKEN"] = vercel_token
    
    # GitHub Token (optional)
    if Confirm.ask("\nDo you want to add a GitHub token? (Optional, for private repos)"):
        github_token = Prompt.ask("GitHub Token", password=True)
        credentials["GITHUB_TOKEN"] = github_token
    
    # Write credentials to .env file
    with open(env_file, 'w') as f:
        for key, value in credentials.items():
            f.write(f"{key}={value}\n")
    
    # Set file permissions (readable only by owner)
    os.chmod(env_file, 0o600)
    
    console.print(f"[green]✓ Credentials saved to {env_file}[/green]")
    console.print("[yellow]Note: Keep your credentials secure and never share them[/yellow]")

@cli.command()
def status():
    """Check VibeOps configuration status"""
    cursor_dir = get_cursor_config_dir()
    if not cursor_dir:
        return
    
    mcp_config_file = cursor_dir / "mcp_servers.json"
    env_file = cursor_dir / ".vibeops.env"
    
    console.print(Panel.fit("[bold]VibeOps Configuration Status[/bold]", border_style="blue"))
    
    # Check MCP configuration
    if mcp_config_file.exists():
        try:
            with open(mcp_config_file, 'r') as f:
                config = json.load(f)
            
            if "mcpServers" in config and "vibeops" in config["mcpServers"]:
                vibeops_config = config["mcpServers"]["vibeops"]
                console.print("[green]✓ MCP server configured[/green]")
                
                # Determine mode
                if "npx" in vibeops_config.get("command", ""):
                    mode = "remote"
                    server_url = vibeops_config.get("env", {}).get("MCP_SERVER_URL", "Unknown")
                    console.print(f"  Mode: Remote server")
                    console.print(f"  Server URL: {server_url}")
                    
                    # Test remote server
                    if server_url != "Unknown":
                        success, result = test_server_connection(server_url)
                        if success:
                            console.print(f"  [green]✓ Server is accessible[/green]")
                        else:
                            console.print(f"  [red]✗ Server not accessible: {result}[/red]")
                else:
                    mode = "local"
                    console.print(f"  Mode: Local STDIO")
                    console.print(f"  Command: {vibeops_config.get('command', 'Unknown')}")
                    console.print(f"  Working directory: {vibeops_config.get('cwd', 'Unknown')}")
            else:
                console.print("[red]✗ VibeOps not configured in MCP servers[/red]")
        except json.JSONDecodeError:
            console.print("[red]✗ Invalid MCP configuration file[/red]")
    else:
        console.print("[red]✗ MCP configuration file not found[/red]")
    
    # Check credentials (only for local mode)
    if env_file.exists():
        console.print("[green]✓ Local credentials file found[/green]")
        
        # Check which credentials are set
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            required_creds = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "VERCEL_TOKEN"]
            for cred in required_creds:
                if cred in env_content:
                    console.print(f"  [green]✓ {cred} is set[/green]")
                else:
                    console.print(f"  [red]✗ {cred} is missing[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error reading credentials: {e}[/red]")
    else:
        console.print("[yellow]! Local credentials file not found (OK for remote mode)[/yellow]")
    
    # Configuration paths
    console.print(f"\n[dim]Configuration directory: {cursor_dir}[/dim]")
    console.print(f"[dim]MCP config file: {mcp_config_file}[/dim]")
    console.print(f"[dim]Credentials file: {env_file}[/dim]")

@cli.command()
@click.option('--port', default=8000, help='Port to run the server on')
@click.option('--mode', type=click.Choice(['stdio', 'sse', 'http']), default='stdio', help='Server mode')
def serve(port, mode):
    """Start the VibeOps MCP server directly"""
    console.print(f"[blue]Starting VibeOps MCP server in {mode.upper()} mode...[/blue]")
    
    if mode == 'stdio':
        from .server import VibeOpsServer
        server = VibeOpsServer(mode='stdio')
        server.run_stdio_server()
    else:
        import asyncio
        from .server import VibeOpsServer
        
        async def run_server():
            server = VibeOpsServer(mode=mode)
            await server.run_sse_server(port)
        
        asyncio.run(run_server())

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