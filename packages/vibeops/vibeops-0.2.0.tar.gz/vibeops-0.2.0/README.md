# VibeOps 🚀

**DevOps automation tool with MCP server integration for Cursor**

[![PyPI version](https://badge.fury.io/py/vibeops.svg)](https://badge.fury.io/py/vibeops)
[![Python Support](https://img.shields.io/pypi/pyversions/vibeops.svg)](https://pypi.org/project/vibeops/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

VibeOps is a powerful DevOps automation tool that integrates with Cursor via the Model Context Protocol (MCP). It provides seamless deployment capabilities for fullstack applications to AWS and Vercel with real-time progress tracking.

## ✨ Features

- 🎯 **Universal MCP Server** - Deploy once, use by everyone
- 🔒 **Security-First** - Stateless, multi-tenant architecture
- ⚡ **Real-time Progress** - SSE streaming for deployment updates
- 🌐 **Multi-Cloud** - AWS (EC2, S3) and Vercel support
- 🤖 **Auto-Detection** - Automatically detects app types (React, Node.js, Python, etc.)
- 📊 **Monitoring** - Health checks, logs, and deployment tracking
- 🛠️ **Easy Setup** - Simple CLI for Cursor configuration

## 🚀 Quick Start

### Installation

```bash
pip install vibeops
```

### Basic Setup

```bash
# Configure Cursor for local development
vibeops init --mode local

# Or configure for remote server
vibeops init --server-url https://your-vibeops-server.com

# Check configuration
vibeops status
```

### Usage in Cursor

Once configured, you can use VibeOps directly in Cursor:

```
Deploy my React app to Vercel and AWS:
- AWS Access Key: AKIA...
- AWS Secret Key: xyz...
- Vercel Token: vercel_...
- App Name: my-awesome-app
- Platform: fullstack
```

## 🏗️ Architecture

VibeOps consists of two main components:

### 1. Universal MCP Server
- **Stateless** - No credentials stored on server
- **Multi-tenant** - Multiple users can use the same instance
- **Scalable** - Deploy on free cloud tiers (Oracle Cloud, AWS, etc.)

### 2. CLI Package
- **Easy Configuration** - Automatically configures Cursor
- **Credential Management** - Secure local storage or parameter passing
- **Server Management** - Start/stop local servers

## 📦 Installation Options

### For End Users (CLI Only)
```bash
pip install vibeops
```

### For Server Deployment
```bash
pip install vibeops[server]
```

### For Development
```bash
pip install vibeops[dev]
```

## 🔧 Configuration Modes

### Local Mode (Development)
```bash
vibeops init --mode local
```
- Runs MCP server locally via STDIO
- Credentials stored securely on your machine
- Perfect for individual development

### Remote Mode (Team/Production)
```bash
vibeops init --server-url https://your-server.com
```
- Connects to remote MCP server
- Credentials passed as parameters (not stored)
- Perfect for team collaboration

## 🌐 Server Deployment

Deploy your own VibeOps server for team use:

### Oracle Cloud Free Tier (Recommended)
```bash
# 4 ARM OCPUs, 24GB RAM, 200GB storage - Forever Free!
git clone https://github.com/vibeops/vibeops.git
cd vibeops
python -m vibeops.server --mode sse --port 8000
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

## 🎯 Supported Deployments

| Application Type | Frontend | Backend | Database |
|-----------------|----------|---------|----------|
| **React/Next.js** | Vercel | AWS EC2 | PostgreSQL/MySQL |
| **Vue/Angular** | Vercel | AWS EC2 | PostgreSQL/MySQL |
| **Node.js API** | - | AWS EC2 | PostgreSQL/MySQL |
| **Python/Django** | - | AWS EC2 | PostgreSQL/MySQL |
| **Fullstack** | Vercel | AWS EC2 | PostgreSQL/MySQL |

## 📋 CLI Commands

```bash
# Initialize VibeOps configuration
vibeops init [--mode local|remote] [--server-url URL]

# Check configuration status
vibeops status

# Start local server (for development)
vibeops serve [--mode stdio|sse|http] [--port 8000]

# Test remote server connection
vibeops test-server https://your-server.com
```

## 🔒 Security

- **No Credential Storage** - Server never stores user credentials
- **HTTPS/SSL** - Encrypted communication
- **Multi-tenant Isolation** - Each deployment runs in isolation
- **Audit Logging** - All actions logged with user IDs

## 🛠️ Development

### Local Development Setup
```bash
git clone https://github.com/vibeops/vibeops.git
cd vibeops
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black vibeops/
flake8 vibeops/
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete server deployment instructions
- [API Reference](docs/api.md) - MCP server API documentation
- [Security Guide](docs/security.md) - Security best practices
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/vibeops/vibeops/issues)
- **Discussions**: [GitHub Discussions](https://github.com/vibeops/vibeops/discussions)
- **Documentation**: [docs.vibeops.dev](https://docs.vibeops.dev)

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [Cursor](https://cursor.sh/) for the amazing AI-powered IDE
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP server framework

---

**Made with ❤️ by the VibeOps Team**
