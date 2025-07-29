#!/usr/bin/env python3
"""
Setup script for VibeOps - DevOps automation tool with MCP server integration
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "VibeOps - DevOps automation tool with MCP server integration"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="vibeops",
    version="0.3.0",
    author="VibeOps Team",
    author_email="team@vibeops.dev",
    description="VibeOps - Universal DevOps automation with AI-powered deployment advice",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/vibeops/vibeops",
    project_urls={
        "Bug Tracker": "https://github.com/vibeops/vibeops/issues",
        "Documentation": "https://docs.vibeops.dev",
        "Source Code": "https://github.com/vibeops/vibeops",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "server": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "sse-starlette>=1.6.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vibeops=vibeops.cli:cli",
            "vibeops-server=vibeops.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "vibeops": [
            "templates/*.tf",
            "templates/*.sh",
            "templates/*.yml",
            "templates/*.yaml",
        ],
    },
    keywords=[
        "devops",
        "automation",
        "deployment",
        "aws",
        "vercel",
        "mcp",
        "cursor",
        "infrastructure",
        "terraform",
        "ci-cd",
    ],
    zip_safe=False,
) 