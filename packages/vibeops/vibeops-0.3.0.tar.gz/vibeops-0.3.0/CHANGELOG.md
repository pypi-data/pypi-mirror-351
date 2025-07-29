# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-05-28

### Added
- Working SSE (Server-Sent Events) transport for MCP server
- Proper external connectivity with Azure Network Security Group configuration
- Simplified MCP configuration using URL-based approach instead of complex Python scripts

### Changed
- Updated CLI to use proper SSE endpoint format (`/sse`)
- Replaced complex Python script MCP configuration with simple URL-based configuration
- Improved server connection testing with proper SSE headers
- Updated default server URL to include port 8000

### Fixed
- External server connectivity issues resolved
- MCP server now properly accessible from Cursor
- SSE transport working correctly with FastMCP
- Azure VM firewall and NSG configuration completed

### Technical Details
- Server running on Azure VM at `20.83.174.151:8000`
- SSE endpoint: `http://20.83.174.151:8000/sse`
- Tools available: `deploy_application`, `check_deployment_logs`, `get_logs_by_app`, `redeploy_on_changes`, `list_all_deployments`

## [0.2.5] - 2025-05-28

### Added
- Initial MCP server implementation with FastMCP
- Support for deployment tools and logging
- Azure VM deployment configuration

### Changed
- Migrated from custom HTTP endpoints to proper MCP JSON-RPC format
- Updated tool names to match expected MCP conventions

### Fixed
- Transport configuration issues
- Tool name mismatches between client and server

## [0.2.0] - 2025-05-27

### Added
- Basic MCP server functionality
- Deployment automation tools
- CLI for configuration management

### Changed
- Initial package structure and dependencies

## [0.1.0] - 2025-05-26

### Added
- Initial release
- Basic DevOps automation functionality

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