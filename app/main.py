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
    # Lightweight startup migration: ensure user_id column exists for per-user data scoping
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            # Categories.user_id
            res = conn.execute(text("PRAGMA table_info('categories')"))
            cols = {row[1] for row in res}
            if 'user_id' not in cols:
                conn.execute(text("ALTER TABLE categories ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
            # Transactions.user_id
            res2 = conn.execute(text("PRAGMA table_info('transactions')"))
            cols2 = {row[1] for row in res2}
            if 'user_id' not in cols2:
                conn.execute(text("ALTER TABLE transactions ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE"))
            conn.commit()
    except Exception:
        # Avoid crashing the app on startup; ignore migration errors in dev
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

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return FileResponse("app\\static\\login.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return FileResponse("app\\static\\register.html")

# @app.get("/api/ping")
# async def ping():
#     return {"message": "pong"}

