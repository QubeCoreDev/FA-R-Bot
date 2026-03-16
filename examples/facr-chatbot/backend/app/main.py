"""FastAPI entry point for the FAČR chatbot backend."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from chatkit.server import StreamingResult
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, JSONResponse

from .server import FACRServer, create_facr_server

_project_root = Path(__file__).resolve().parent.parent.parent
_env_path = _project_root / ".env"
load_dotenv(_env_path)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_facr_server: FACRServer | None = None

_frontend_dist = _project_root / "frontend" / "dist"
_serve_frontend = _frontend_dist.is_dir()


@asynccontextmanager
async def lifespan(application: FastAPI):
    global _facr_server
    try:
        _facr_server = create_facr_server()
        logger.info("FAČR server initialized successfully")
    except Exception as exc:
        logger.error("Failed to initialize FAČR server: %s", exc)
        raise
    yield


app = FastAPI(title="FAČR Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_server() -> FACRServer:
    assert _facr_server is not None, "Server not initialized — is OPENAI_API_KEY set?"
    return _facr_server


@app.post("/facr/chatkit")
async def chatkit_endpoint(
    request: Request,
    server: FACRServer = Depends(get_server),
) -> Response:
    payload = await request.body()
    result = await server.process(payload, {"request": request})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    if hasattr(result, "json"):
        return Response(content=result.json, media_type="application/json")
    return JSONResponse(result)


@app.get("/facr/health")
async def health_check() -> dict[str, Any]:
    if _facr_server is None:
        return {"status": "initializing"}
    chunk_count = len(_facr_server.kb.chunks)
    doc_count = len(_facr_server.kb.document_names)
    return {
        "status": "healthy",
        "knowledge_base": {
            "documents": doc_count,
            "chunks": chunk_count,
        },
    }


if _serve_frontend:
    app.mount(
        "/assets",
        StaticFiles(directory=str(_frontend_dist / "assets")),
        name="static-assets",
    )

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve frontend SPA — any non-API path returns index.html."""
        file_path = _frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(_frontend_dist / "index.html"))

    logger.info("Serving frontend from %s", _frontend_dist)
