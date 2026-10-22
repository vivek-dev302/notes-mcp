# Notes MCP Server

A remote MCP server that lets AI clients (Claude, Kiro, MCP Inspector, etc.) create, list, and delete notes. Built with FastMCP, PostgreSQL, and Auth0 OAuth.

## Stack

- **[FastMCP](https://gofastmcp.com)** — MCP server framework
- **PostgreSQL** — persistent note storage
- **Auth0** — OAuth 2.1 authentication (Auth for MCP / DCR / CIMD)
- **Render** — hosting

---

## Project Structure

```
├── mcp_server.py       # MCP server — tools and auth wiring
├── notes_app.py        # Database layer (PostgreSQL CRUD)
├── docker-compose.yml  # Local PostgreSQL via Docker
├── render.yaml         # Render deployment config (web service + DB)
├── requirements.txt    # Python dependencies
├── .python-version     # Python 3.11
└── .env.example        # Environment variable template
```

---

## Tools Exposed

| Tool | Description |
|---|---|
| `list_my_notes` | List all saved notes |
| `add_a_note` | Save a new note |
| `delete_a_note` | Delete a note by ID |

---

## Local Development

### Prerequisites

- Python 3.11
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for local PostgreSQL)
- [ngrok](https://ngrok.com) (to expose local server for Auth0 callback)
- An [Auth0](https://auth0.com) account

### 1. Clone and install dependencies

```bash
git clone https://github.com/your-username/notes-mcp
cd notes-mcp
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Start local PostgreSQL

```bash
docker compose up -d
```

This starts a PostgreSQL instance at `localhost:5432` with database `notes` and password `secret`.

### 3. Expose local server with ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g. `https://abc123.ngrok-free.app`).

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:secret@localhost:5432/notes
AUTH0_DOMAIN=https://your-tenant.us.auth0.com/
SERVER_BASE_URL=https://abc123.ngrok-free.app
```

### 5. Auth0 setup

1. Sign up at [auth0.com](https://auth0.com) and create a tenant
2. Go to **Settings → Advanced** and enable:
   Auth for MCP
   - DCR (Dynamic Client Registration)
   - CIMD (Client ID Metadata Document Registration)
   - Resource Parameter Compatibility Profile
3. Go to **Authentication → Database** → your connection → **Advanced** → enable **Promote to Domain Level**
4. Go to **Applications → APIs → Create API**:
   - Identifier: `https://abc123.ngrok-free.app/mcp` (your ngrok URL + `/mcp`)
   - Signing algorithm: RS256
5. Start the server (step 6) — it logs the exact `aud` value at startup. Your API identifier must match it exactly.

### 6. Run the server

```bash
python mcp_server.py
```

Server starts at `http://0.0.0.0:8000/mcp`.

### 7. Connect with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

- Transport: Streamable HTTP
- URL: `https://abc123.ngrok-free.app/mcp`

On first connect, MCP Inspector registers itself via DCR. Go to Auth0 → **Applications → Applications** → find the auto-registered app → **APIs tab** → authorize it for your API.

---

## Adding Google Login

Google login can be added entirely from the Auth0 dashboard — no code changes needed.

1. Auth0 → **Authentication → Social → google-oauth2 → Settings**
2. Add your Google OAuth Client ID and Secret (from [Google Cloud Console](https://console.cloud.google.com))
3. Scroll to **Advanced → Promote Connection to Domain Level** → enable
4. Save

Users will now see a "Continue with Google" button on the Auth0 login page.

For local testing, Auth0 provides dev keys so you can skip the Google Cloud setup entirely — just promote the connection to domain level.

---

## Deploying to Render

### One-click deploy via Blueprint

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → **Blueprint** → connect repo
3. Render reads `render.yaml` and creates:
   - A free PostgreSQL database
   - A web service with `DATABASE_URL` auto-wired
4. In Render → your service → **Environment**, add:
   ```
   AUTH0_DOMAIN=https://your-tenant.us.auth0.com/
   SERVER_BASE_URL=https://your-app.onrender.com
   ```
5. Deploy

### Auth0 API for production

Create a second API in Auth0:
- Identifier: `https://your-app.onrender.com/mcp`

The server logs the exact audience at startup — make sure it matches.

---

## MCP Client Config

### HTTP (remote server)

```json
{
  "mcpServers": {
    "notes": {
      "url": "https://your-app.onrender.com/mcp"
    }
  }
}
```

### stdio (local, no auth)

```json
{
  "mcpServers": {
    "notes-local": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/notes-mcp"
    }
  }
}
```

---

## Common Issues

**"Service not found"** — The audience passed to Auth0 has a leading/trailing space or doesn't match any registered API identifier. Check for whitespace in the Auth0 API identifier.

**"Unknown client"** — The MCP client (e.g. Claude Code) uses CIMD and needs to be manually registered in Auth0. Go to Applications → Create Application → Import from URL → enter the client's CIMD URL.

**"Client not authorized"** — The client registered via DCR but hasn't been granted access to your API yet. Go to the auto-registered app → APIs tab → authorize it.

**Tools timeout in MCP Inspector** — Server is running in stateful mode. Make sure `stateless_http=True` is set in `mcp.run()`.

**"Site isn't working" in browser** — Expected. `/mcp` is a POST-only endpoint. Browsers do GET, which returns nothing useful. Use MCP Inspector or a proper MCP client.
