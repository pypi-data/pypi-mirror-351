# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-27

### Added
- Initial release of VibeOps
- Universal MCP server for DevOps automation
- Support for AWS and Vercel deployments
- Real-time deployment progress via SSE
- CLI tool for easy Cursor configuration
- Multi-tenant, stateless server architecture
- Automatic application type detection
- Support for fullstack, frontend, and backend deployments
- Comprehensive deployment templates
- Oracle Cloud Free Tier deployment guide
- Security-first credential handling

### Features
- **MCP Server Modes**: STDIO (local), SSE (remote), HTTP (remote)
- **Cloud Providers**: AWS (EC2, S3), Vercel
- **Application Types**: React, Next.js, Vue, Node.js, Python, Java, Go
- **Infrastructure**: Terraform-based deployments
- **Monitoring**: Health checks, deployment logs, progress tracking
- **CLI Commands**: `vibeops init`, `vibeops status`, `vibeops serve`

### Security
- Stateless server design (no credential storage)
- HTTPS/SSL support
- Multi-tenant isolation
- Secure credential passing via parameters

### Documentation
- Complete deployment guide for Oracle Cloud
- CLI usage documentation
- API reference
- Security best practices 