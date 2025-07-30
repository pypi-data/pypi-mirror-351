> [!NOTE]  
> App is in review process, it will be released here
>
>  https://apps.apple.com/app/apple-store/id6746345658
>
> Public Beta avialable here
>
> https://testflight.apple.com/join/E39P1hzw

# MCP Client for iOS

[![Auto Release](https://github.com/Aayush9029/mcp-server/actions/workflows/auto-release.yml/badge.svg)](https://github.com/Aayush9029/mcp-server/actions/workflows/auto-release.yml)
[![pages-build-deployment](https://github.com/Aayush9029/mcp-server/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/Aayush9029/mcp-server/actions/workflows/pages/pages-build-deployment)
[![PyPI version](https://badge.fury.io/py/task-mcp.svg)](https://badge.fury.io/py/task-mcp)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<p>

![image](https://github.com/user-attachments/assets/a655c5ca-97e9-4ec6-af5b-95b8ebf07d5e)

</p>

### Verified with 
<img src="https://github.com/user-attachments/assets/c05449f1-4da8-4228-9bba-6821f70a3ab8" width="40px" />
<img src="https://github.com/user-attachments/assets/caa206db-bf97-4376-81c1-20d542d5963a" width="40px" />
<img src="https://github.com/user-attachments/assets/c2cbc255-af9b-4683-ba12-c36a4b1e6268" width="40px" />
<img src="https://github.com/user-attachments/assets/ec6c1c3d-8209-406f-986d-4fb1d76b401b" width="40px" />
<img src="https://github.com/user-attachments/assets/220a04be-f6f2-4a3d-b161-b961311d6775" width="40px" />
<img src="https://github.com/user-attachments/assets/69781fbe-5888-4cd0-98d8-be71dbb14e8c" width="40px" />

## Task Management MCP Server

Bridge AI assistants with real-world task management

This MCP server connects Claude Desktop, Cursor, and other AI tools to a powerful task management API, enabling intelligent workflows that create, update, and track tasks automatically on your iPhone.

### What You Can Do

- Ask Claude to create tasks during coding sessions
- Let Cursor update task status as it completes work
- Get notifications on your iPhone when AI assistants finish tasks
- Track progress across multiple AI tools and automation scripts
- Manage priorities with AI-suggested urgency levels

Perfect for developers who want their AI assistants to collaborate on real projects with automatic task tracking and mobile notifications.

## Quick Start

### 1. Get Your API Key

Download the iOS app [here](https://apps.apple.com/app/apple-store/id6746345658)

### 2. Choose Your Setup

#### For Claude Desktop (Recommended)

Add this to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://task-mcp-server.aayushpokharel9029.workers.dev/sse?apiKey=YOUR_API_KEY"
      ]
    }
  }
}
```

#### For Cursor or Other MCP Clients

```json
{
  "mcpServers": {
    "task-manager": {
      "url": "https://task-mcp-server.aayushpokharel9029.workers.dev/sse?apiKey=YOUR_API_KEY"
    }
  }
}
```

Replace `YOUR_API_KEY` with your actual API key.

### 3. Start Using It

Once configured, your AI assistant can:

- "Create a high-priority task to review the pull request"
- "Show me all pending tasks"
- "Mark the deployment task as completed"
- "Update the bug fix to urgent priority"

## Available Tools

The server provides these capabilities to AI assistants:

### `create_task`
Create new tasks with title, description, priority, and notification settings.

### `list_tasks`
View all tasks with optional filtering by status, priority, or date.

### `get_task`
Get detailed information about any specific task.

### `update_task`
Modify task properties including status, priority, and description.

### `delete_task`
Remove completed or cancelled tasks.

## Technical Details

### Documentation

- **REST API Documentation**:
  - [FastAPI Docs](https://mcpclient.lovedoingthings.com/docs)
  - [ReDoc](https://mcpclient.lovedoingthings.com/redoc#tag/Tasks/operation/create_task_api_tasks__post)
- **MCP Server Documentation**: [https://task-mcp-server.aayushpokharel9029.workers.dev](https://task-mcp-server.aayushpokharel9029.workers.dev)

### API Details

- **Authentication**: API key via `X-API-Key` header
- **Supported Priorities**: LOW, MEDIUM, HIGH, URGENT
- **Supported Statuses**: TODO, IN_PROGRESS, DONE, CANCELLED

## Security & Privacy

- **API Key Isolation**: Each key maintains completely separate task data
- **No Cross-Access**: Tasks are never shared between different API keys
- **Secure Communication**: All requests require authentication headers
- **Real-time Updates**: Changes sync instantly to your iPhone app

## Need Help?

If your AI assistant isn't connecting:

1. Check that your API key is correctly formatted
2. Verify the configuration file location
3. Restart your MCP client after configuration changes

For issues or feature requests, visit the [GitHub Issues](https://github.com/Aayush9029/mcp-server/issues).

---

GitHub: [@Aayush9029](https://github.com/Aayush9029/mcp-server) • Twitter: [@aayushbuilds](https://twitter.com/aayushbuilds)
