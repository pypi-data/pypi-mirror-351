#!/bin/bash
# VibeOps Generated User Data Script
# App: ${app_name} (${environment})

set -e

# Update system
apt-get update
apt-get upgrade -y

# Install common dependencies
apt-get install -y curl wget git unzip software-properties-common

# Install Node.js (for JavaScript/TypeScript apps)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Install Python (for Python apps)
apt-get install -y python3 python3-pip python3-venv

# Install Java (for Java apps)
apt-get install -y openjdk-17-jdk

# Install Go (for Go apps)
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile

# Install Docker
apt-get install -y docker.io
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Install Nginx (reverse proxy)
apt-get install -y nginx

# Create application directory
mkdir -p /opt/${app_name}
cd /opt/${app_name}

# Clone repository
git clone ${repo_url} .
git checkout ${branch}

# Set ownership
chown -R ubuntu:ubuntu /opt/${app_name}

# Switch to ubuntu user for application setup
sudo -u ubuntu bash << 'EOF'
cd /opt/${app_name}

# Install dependencies
${install_command}

# Build application if needed
if [ -n "${build_command}" ]; then
    ${build_command}
fi

# Create systemd service
sudo tee /etc/systemd/system/${app_name}.service > /dev/null << 'SERVICE'
[Unit]
Description=${app_name} Application
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/${app_name}
ExecStart=/bin/bash -c '${start_command}'
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=${port}

[Install]
WantedBy=multi-user.target
SERVICE

EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable ${app_name}
systemctl start ${app_name}

# Configure Nginx reverse proxy
cat > /etc/nginx/sites-available/${app_name} << 'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:${port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINX

# Enable the site
ln -sf /etc/nginx/sites-available/${app_name} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# Create deployment info file
cat > /opt/${app_name}/deployment-info.json << INFO
{
    "app_name": "${app_name}",
    "environment": "${environment}",
    "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "repo_url": "${repo_url}",
    "branch": "${branch}",
    "port": "${port}",
    "managed_by": "VibeOps"
}
INFO

echo "VibeOps deployment completed successfully!"
echo "Application should be available at http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):${port}" 