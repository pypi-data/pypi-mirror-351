# VibeOps Generated Terraform Configuration for Backend Deployment
# Generated on: {{timestamp}}
# App: {{app_name}} ({{environment}})
# Type: {{app_type}} - {{framework}}

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "{{aws_region}}"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "{{app_name}}"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "{{environment}}"
}

# VPC and Networking
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.app_name}-${var.environment}-vpc"
    Environment = var.environment
    ManagedBy   = "VibeOps"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name        = "${var.app_name}-${var.environment}-igw"
    Environment = var.environment
    ManagedBy   = "VibeOps"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.app_name}-${var.environment}-public-subnet"
    Environment = var.environment
    ManagedBy   = "VibeOps"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}-public-rt"
    Environment = var.environment
    ManagedBy   = "VibeOps"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group
resource "aws_security_group" "app" {
  name_prefix = "${var.app_name}-${var.environment}-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = {{port}}
    to_port     = {{port}}
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}-sg"
    Environment = var.environment
    ManagedBy   = "VibeOps"
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Key Pair
resource "aws_key_pair" "app" {
  key_name   = "${var.app_name}-${var.environment}-key"
  public_key = file("~/.ssh/id_rsa.pub")

  tags = {
    Name        = "${var.app_name}-${var.environment}-key"
    Environment = var.environment
    ManagedBy   = "VibeOps"
  }
}

# EC2 Instance
resource "aws_instance" "app" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name              = aws_key_pair.app.key_name
  vpc_security_group_ids = [aws_security_group.app.id]
  subnet_id             = aws_subnet.public.id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    app_name = var.app_name
    environment = var.environment
    repo_url = "{{repo_url}}"
    branch = "{{branch}}"
    install_command = "{{install_command}}"
    build_command = "{{build_command}}"
    start_command = "{{start_command}}"
    port = "{{port}}"
  }))

  tags = {
    Name        = "${var.app_name}-${var.environment}-instance"
    Environment = var.environment
    ManagedBy   = "VibeOps"
    AppType     = "{{app_type}}"
    Framework   = "{{framework}}"
  }
}

# Outputs
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.app.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.app.public_dns
}

output "application_url" {
  description = "URL to access the application"
  value       = "http://${aws_instance.app.public_ip}:{{port}}"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_instance.app.public_ip}"
} 