# VibeOps Universal MCP Server Deployment Guide

This guide shows you how to deploy the VibeOps MCP server for **universal access** - so anyone can use it with their own credentials.

## 🎯 Architecture Overview

**Two Components:**
1. **Universal MCP Server** - Deployed once, used by everyone (stateless)
2. **VibeOps CLI Package** - Installed by each user to configure Cursor

## 🚀 Part 1: Deploy Universal MCP Server

### Option 1: Oracle Cloud Free Tier (Recommended - Forever Free!)

Oracle Cloud offers the **best free tier** for hosting:
- **4 ARM OCPUs, 24GB RAM, 200GB storage - Forever Free**
- **10TB monthly bandwidth**
- **No time limits** (unlike AWS/GCP 12-month limits)

#### Step 1: Create Oracle Cloud Account
1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Sign up for free account
3. Complete verification (requires credit card but won't be charged)

#### Step 2: Create Compute Instance
```bash
# 1. In Oracle Cloud Console, go to Compute > Instances
# 2. Click "Create Instance"
# 3. Choose these settings:
#    - Name: vibeops-mcp-server
#    - Image: Ubuntu 22.04 (Always Free Eligible)
#    - Shape: VM.Standard.A1.Flex (ARM-based, Always Free)
#    - OCPUs: 4, Memory: 24GB
#    - Networking: Create new VCN (default settings)
#    - SSH Keys: Upload your public key or generate new ones

# 4. Click "Create" and wait for instance to start
```

#### Step 3: Configure Security Rules
```bash
# In Oracle Cloud Console:
# 1. Go to Networking > Virtual Cloud Networks
# 2. Click your VCN > Security Lists > Default Security List
# 3. Add Ingress Rules:
#    - Port 8000 (HTTP): Source 0.0.0.0/0
#    - Port 443 (HTTPS): Source 0.0.0.0/0
#    - Port 22 (SSH): Source 0.0.0.0/0 (already exists)
```

#### Step 4: Deploy VibeOps Server
```bash
# SSH into your Oracle Cloud instance
ssh ubuntu@<your-instance-public-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install -y python3.11 python3.11-pip python3.11-venv git

# Clone VibeOps (or upload your code)
git clone https://github.com/yourusername/vibeops.git
cd vibeops

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Install additional server dependencies
pip install fastapi uvicorn sse-starlette

# Create systemd service for auto-start
sudo tee /etc/systemd/system/vibeops-mcp.service > /dev/null <<EOF
[Unit]
Description=VibeOps Universal MCP Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/vibeops
Environment=PATH=/home/ubuntu/vibeops/venv/bin
ExecStart=/home/ubuntu/vibeops/venv/bin/python -m vibeops.server --mode sse --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable vibeops-mcp
sudo systemctl start vibeops-mcp

# Check status
sudo systemctl status vibeops-mcp

# Test the server
curl http://localhost:8000/health
```

#### Step 5: Setup SSL/HTTPS (Optional but Recommended)
```bash
# Install Nginx and Certbot
sudo apt install -y nginx certbot python3-certbot-nginx

# Configure Nginx
sudo tee /etc/nginx/sites-available/vibeops > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/vibeops /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate (if you have a domain)
sudo certbot --nginx -d your-domain.com
```

### Option 2: Other Free Cloud Providers

#### AWS Free Tier (12 months)
```bash
# t2.micro instance (1 vCPU, 1GB RAM)
# Limited but sufficient for testing
# Follow similar steps as Oracle Cloud
```

#### Google Cloud Free Tier (12 months + Always Free)
```bash
# e2-micro instance (0.25-1 vCPU, 1GB RAM)
# Always Free tier available
# Follow similar steps as Oracle Cloud
```

#### Railway (Easy deployment)
```bash
# 1. Fork the vibeops repository
# 2. Connect to Railway
# 3. Deploy with one click
# 4. Set PORT environment variable to 8000
```

## 🎯 Part 2: Configure Cursor to Use Deployed Server

### Method 1: Using VibeOps CLI (Recommended)

```bash
# Install VibeOps CLI
pip install vibeops

# Initialize with remote server
vibeops init --server-url https://your-vibeops-server.com

# This will:
# 1. Detect your Cursor config directory
# 2. Ask for your AWS/Vercel credentials
# 3. Configure Cursor to use the remote MCP server
# 4. Test the connection
```

### Method 2: Manual Cursor Configuration

Add this to your Cursor MCP configuration file:

**Location:** 
- macOS: `~/Library/Application Support/Cursor/User/globalStorage/mcp_servers.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp_servers.json`
- Linux: `~/.config/Cursor/User/globalStorage/mcp_servers.json`

```json
{
  "mcpServers": {
    "vibeops": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-fetch",
        "https://your-vibeops-server.com"
      ],
      "env": {
        "MCP_SERVER_URL": "https://your-vibeops-server.com"
      }
    }
  }
}
```

### Method 3: Direct HTTP Configuration

For advanced users, configure Cursor to use HTTP mode:

```json
{
  "mcpServers": {
    "vibeops": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", "@-",
        "https://your-vibeops-server.com/mcp/tools/deploy"
      ]
    }
  }
}
```

## 🔧 Usage Examples

Once configured, you can use VibeOps in Cursor:

```
Deploy my React app to Vercel and AWS:
- AWS Access Key: AKIA...
- AWS Secret Key: xyz...
- Vercel Token: vercel_...
- App Name: my-awesome-app
- Platform: fullstack
```

The server will:
1. Accept your credentials securely
2. Deploy your app without storing credentials
3. Return deployment URLs and status
4. Provide real-time progress updates

## 🔒 Security Features

- **Stateless**: No credentials stored on server
- **Multi-tenant**: Multiple users can use same server
- **Encrypted**: HTTPS/SSL support
- **Isolated**: Each deployment runs in isolation
- **Auditable**: All actions logged with user IDs

## 📊 Monitoring Your Deployment

```bash
# Check server status
curl https://your-vibeops-server.com/health

# View active deployments
curl https://your-vibeops-server.com/deployments

# Monitor logs
sudo journalctl -u vibeops-mcp -f

# Check resource usage
htop
df -h
```

## 🚀 Scaling Options

### For High Usage:
1. **Upgrade Oracle Cloud instance** (still free up to limits)
2. **Add load balancer** for multiple instances
3. **Use container orchestration** (Docker + Kubernetes)
4. **Add Redis** for session management
5. **Implement rate limiting** and authentication

### Production Deployment:
```bash
# Docker deployment
docker build -t vibeops-mcp .
docker run -d -p 8000:8000 --name vibeops-mcp vibeops-mcp

# Kubernetes deployment
kubectl apply -f k8s/
```

## 🎉 Success!

Your VibeOps MCP server is now:
- ✅ Deployed and accessible from anywhere
- ✅ Ready for multiple users with their own credentials
- ✅ Integrated with Cursor for seamless DevOps
- ✅ Running on free infrastructure (Oracle Cloud)
- ✅ Scalable and production-ready

**Next Steps:**
1. Share your server URL with team members
2. Each person installs `vibeops` CLI and configures Cursor
3. Everyone can deploy apps using their own credentials
4. Monitor usage and scale as needed

**Your Universal MCP Server URL:** `https://your-vibeops-server.com` 