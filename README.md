# Gmail MCP Server (FastAPI + Claude Desktop)

This project is a minimal Gmail **MCP server** built with FastAPI. It exposes a `/send-email/` HTTP endpoint and an MCP tool that can be called from MCP‑aware clients like Claude Desktop, so you can send real Gmail emails just by chatting with an AI assistant.

The flow is:

1. FastAPI app provides a `POST /send-email/` endpoint that sends email via the Gmail API.
2. `fastapi-mcp` wraps the app and exposes an MCP endpoint at `/mcp`.
3. Claude Desktop connects to the MCP server and calls the email tool when you ask it to send an email.

---

## 1. Project structure

Key files:

- `mcp_server.py` – FastAPI app with `/send-email/` and MCP wrapper.  
- `send_email.py` – Gmail API helper functions (OAuth, MIME message creation, sending).  
- `test_gmail_auth.py` – One‑time script to perform Gmail OAuth and create `token.json`.  
- `requirements.txt` – Python dependencies.  

**Not in Git (must be provided by each user):**

- `credentials.json` – Google OAuth client secrets downloaded from Google Cloud.  
- `token.json` – Gmail access/refresh tokens generated locally after you run `test_gmail_auth.py`.  

---

## 2. Prerequisites

Before you start, install:

- **Python 3.11+**  
- **Node.js** (for `npx` – used by Claude Desktop to run the MCP bridge)  
- **Claude Desktop** (latest version from Anthropic’s website)  
- A Google account with access to Gmail  

Clone the repo:
git clone https://github.com/TushaarKD/Kalpesh_MCP_Project.git
cd Kalpesh_MCP_Project


---

## 3. Set up Python environment

Create and activate a virtual environment:

python -m venv venv
.\venv\Scripts\Activate.ps1


Install dependencies:
pip install -r requirements.txt

This installs FastAPI, Uvicorn, Gmail API libraries, `fastapi-mcp`, etc.

---

## 4. Enable Gmail API and get credentials

1. Go to the **Google Cloud Console** and create a project (or use an existing one).  
2. In **APIs & Services → Library**, enable the **Gmail API** for your project.  
3. In **APIs & Services → Credentials**, create credentials:  
   - Type: **OAuth client ID**  
   - Application type: **Desktop app**  
4. Download the `credentials.json` file and place it in the **root** of this project (same folder as `mcp_server.py`).  
5. Make sure `credentials.json` is **not** committed to Git; it is in `.gitignore`.

---

## 5. Run Gmail OAuth once (`test_gmail_auth.py`)

With the venv active and `credentials.json` in place:

python test_gmail_auth.py


What this does:

- If `token.json` does not exist, it opens a browser window for Google login and consent.  
- After you approve access, it saves `token.json` in the project root.  
- Subsequent runs reuse or refresh this token without asking you to log in again.

Both `credentials.json` and `token.json` are local to your machine and should never be committed.

---

## 6. Start the Gmail MCP server

Start the FastAPI + MCP server:

uvicorn mcp_server:app --reload


By default this runs on `http://127.0.0.1:8000`.

### 6.1 Test the HTTP API (optional but recommended)

Open Swagger UI:

- Go to `http://localhost:8000/docs` in your browser.  
- Find `POST /send-email/`.  
- Click **Try it out** and use a JSON body like:

{
"to_email": "your-recipient@example.com",
"subject": "MCP Gmail test",
"body": "Hello from the Gmail MCP FastAPI server!"
}


Click **Execute**. You should see a success response and receive an email at the target address.

You can do the same from `curl`:

curl -X POST "http://127.0.0.1:8000/send-email/"
-H "Content-Type: application/json"
-d '{
"to_email": "your-recipient@example.com",
"subject": "MCP Gmail test via curl",
"body": "Hello from the Gmail MCP FastAPI server (curl)."
}'



---

## 7. MCP endpoint

The MCP server is exposed at:

http://localhost:8000/mcp


If you open that URL in a browser, you will see a JSON‑RPC error like:

{"jsonrpc":"2.0","id":"server-error","error":{"code":-32600,"message":"Not Acceptable: Client must accept text/event-stream"}}


This is expected. MCP over HTTP uses **Server‑Sent Events**, so it requires special headers. MCP clients (like Claude Desktop) handle this for you.

---

## 8. Connect to Claude Desktop

Claude Desktop needs a **local MCP process** that speaks MCP over stdio. We use a small bridge called `mcp-remote` (run via `npx`) which forwards between Claude Desktop and your HTTP MCP server.

### 8.1 Install Node.js

If you don’t have Node.js, install the latest LTS from the official website. This gives you `npm` and `npx`.

### 8.2 Edit `claude_desktop_config.json`

Claude Desktop stores its config in `claude_desktop_config.json`. On Windows it is typically located at:

C:\Users<YourUser>\AppData\Roaming\Claude\claude_desktop_config.json


In Claude Desktop:

1. Open **Settings → Developer → Edit Config** to open this file.  
2. Add the following block under `"mcpServers"` (merge with existing content if needed):

{
"mcpServers": {
"gmail-mcp": {
"command": "npx",
"args": [
"-y",
"mcp-remote",
"http://localhost:8000/mcp",
"--transport",
"http-only"
]
}
}
}



- `gmail-mcp` is the name of this MCP server as seen by Claude.  
- `command` and `args` start a local bridge process that connects Claude Desktop to your HTTP MCP endpoint.

Save the file.

### 8.3 Restart Claude Desktop

1. Quit Claude Desktop completely (including tray icon).  
2. Start Claude Desktop again so it reloads the config.  
3. Ensure your FastAPI server is still running (`uvicorn mcp_server:app --reload`).  

In a new chat, Claude should now be able to use the `gmail-mcp` server.

---

## 9. Using the Gmail MCP tool from Claude

With everything running:

1. Open a new Claude Desktop chat.  
2. Ask something like:

> “Use the gmail-mcp server to send an email to `your-recipient@example.com` with subject `Test from Claude MCP` and body `Hello from my local Gmail MCP server`.”

Claude will:

- Discover the `gmail-mcp` tools.  
- Call the tool that maps to `POST /send-email/` with `to_email`, `subject`, and `body`.  
- Your FastAPI logs should show the email being sent.  
- You should receive the email at the recipient address.

---

## 10. Security notes

- **Do not commit** `credentials.json` or `token.json` to Git.  
- Only run this server on your own machine or in a secure environment; it has the power to send email from your Gmail account.  
- For demos, use a dedicated Gmail account if possible.


