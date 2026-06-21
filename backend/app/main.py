from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import recipes as recipes_router

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # port par défaut de Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


app.include_router(
    recipes_router.router,
    prefix="/api/v1",
)