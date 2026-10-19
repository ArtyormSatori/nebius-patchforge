"""Main application entrypoint for PatchForge-Nemotron."""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "web", "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")

app = FastAPI(
    title="PatchForge-Nemotron",
    description="Autonomous Reliability & Security Remediation Agent powered by NVIDIA Nemotron on Nebius Token Factory",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files & templates
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Register API routes
app.include_router(api_router)


@app.get("/")
async def home(request: Request):
    """Render main web dashboard."""
    return templates.TemplateResponse(request=request, name="index.html")


if __name__ == "__main__":
    import uvicorn
    from app.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=False,
    )
