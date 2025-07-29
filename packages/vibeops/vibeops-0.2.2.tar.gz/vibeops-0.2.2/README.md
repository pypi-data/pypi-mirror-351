# VibeOps

**Configure Cursor to use VibeOps MCP server for AI-powered DevOps automation**

VibeOps is a simple configuration tool that connects your Cursor IDE to the VibeOps Universal MCP server, giving you instant access to AI-powered DevOps automation directly in your chat interface.

## Quick Start

1. **Install the package:**
   ```bash
   pip install vibeops
   ```

2. **Configure Cursor:**
   ```bash
   vibeops init
   ```

3. **Restart Cursor** and start chatting with AI-powered DevOps assistance!

## What You Get

Once configured, you can chat with Cursor and use these powerful tools:

- 🚀 **Deploy applications** to AWS and Vercel with just your credentials
- 🤖 **Get AI-powered deployment advice** for your projects
- 🔍 **Analyze deployment errors** with intelligent suggestions
- 📊 **Monitor deployment status** in real-time
- 🏗️ **Automatic infrastructure setup** based on your app type

## Features

- **Zero Setup**: No need to run your own server - connects to our universal server
- **Secure**: You provide your own AWS/Vercel credentials when deploying
- **AI-Powered**: Get intelligent deployment advice and error analysis
- **Multi-Platform**: Supports fullstack deployments (frontend + backend)
- **Real-time**: Stream deployment progress and logs

## Usage

After running `vibeops init`, simply chat with Cursor:

```
"Deploy my React app to Vercel"
"Help me deploy this Node.js API to AWS"
"Analyze this deployment error: [paste error]"
"What's the best way to deploy a Next.js + Express app?"
```

The AI will guide you through the process and handle the deployment automatically.

## Commands

- `vibeops init` - Configure Cursor to use VibeOps MCP server
- `vibeops status` - Check configuration status
- `vibeops test-server <url>` - Test connection to MCP server

## Requirements

- Python 3.8+
- Cursor IDE
- AWS credentials (for backend deployments)
- Vercel token (for frontend deployments)

## How It Works

1. The `vibeops init` command configures Cursor's MCP settings
2. Cursor connects to the VibeOps Universal MCP server
3. You chat with Cursor using natural language
4. The AI uses your credentials to deploy to AWS/Vercel
5. You get real-time feedback and deployment URLs

## Security

- Your credentials are never stored on our servers
- You provide credentials only when deploying
- All communication is over HTTPS
- The MCP server is stateless and multi-tenant

## Support

- 📧 Email: team@vibeops.dev
- 🐛 Issues: [GitHub Issues](https://github.com/vibeops/vibeops/issues)
- 📖 Docs: [docs.vibeops.dev](https://docs.vibeops.dev)

## License

MIT License - see [LICENSE](LICENSE) file for details.
