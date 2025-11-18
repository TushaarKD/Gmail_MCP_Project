from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_mcp import FastApiMCP
from send_email import send_email


# ---------- Request model ----------

class EmailPayload(BaseModel):
    to_email: str
    subject: str
    body: str


# ---------- FastAPI app ----------

app = FastAPI()


@app.post("/send-email/")
async def send_email_endpoint(payload: EmailPayload):
    """
    Send an email using Gmail API.
    This endpoint will also be exposed as an MCP tool by fastapi-mcp.
    """
    sender = "tushaarkd@gmail.com"  # your Gmail address
    send_email(sender, payload.to_email, payload.subject, payload.body)
    return {"status": "ok", "message": f"Email sent to {payload.to_email}"}


# ---------- MCP wrapper (auto-generates tools from FastAPI) ----------

mcp = FastApiMCP(app)

# Mount the MCP server at /mcp (default)
mcp.mount_http()
