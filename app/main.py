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

# Database setup: create tables on startup
from .database import Base, engine, SessionLocal  # noqa: E402
from . import models  # noqa: F401, ensure models are imported so tables are registered

@app.on_event("startup")
def on_startup():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    # Per requirement: remove all existing transactions so only real data from forms is used
    try:
        db = SessionLocal()
        db.query(models.Transaction).delete()
        db.commit()
    except Exception:
        # Avoid crashing the app on startup; in dev just ignore
        pass
    finally:
        try:
            db.close()
        except Exception:
            pass

if api_router is not None:
    app.include_router(api_router, prefix="/api")

# Serve static frontend
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

app.mount("/static", StaticFiles(directory="app\\static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("app\\static\\index.html")

# @app.get("/api/ping")
# async def ping():
#     return {"message": "pong"}
