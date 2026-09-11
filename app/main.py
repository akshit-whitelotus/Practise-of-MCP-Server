from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.server import mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield

app=FastAPI(
    title="MCP Practise Server",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "message":"MCP Practice Server is running"
    }

@app.get("/health")
async def health():
    return{
        "status":"healthy"
    }

app.mount(
    "/mcp",
    mcp.streamable_http_app(
        streamable_http_path="/"
    )
)