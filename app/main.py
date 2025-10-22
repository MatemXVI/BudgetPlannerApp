from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    # Local import so that the file can run even if optional deps are missing during scaffolding
    from .api import router as api_router
except Exception:  # pragma: no cover - during initial scaffold
    api_router = None

app = FastAPI(title="Budget Planner API", openapi_url="/api/openapi.json")

# Basic CORS setup for local dev
from .core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if api_router is not None:
    app.include_router(api_router, prefix="/api")


# Fallback ping if router import failed (keeps basic functionality in early stage)

@app.get("/")
async def index():
    return {"message": "Welcome to the Budget Planner API!"}
@app.get("/api/ping")
async def ping():
    return {"message": "pong"}
