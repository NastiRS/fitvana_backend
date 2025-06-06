from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.database.config import init_db
from src.routers.announcement import router as announcement_router
from src.routers.blog_post import router as blog_post_router
from src.routers.category import router as category_router
from src.routers.section import router as section_router
from src.routers.tag import router as tag_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    init_db()
    print("Inicialización de base de datos completada.")
    yield
    print("Cerrando aplicación...")


app = FastAPI(
    title="FastAPI Example",
    description="A simple FastAPI example",
    version="1.0",
    # lifespan=lifespan,
)

app.include_router(blog_post_router)
app.include_router(category_router)
app.include_router(tag_router)
app.include_router(section_router)
app.include_router(announcement_router)


@app.get("/health")
async def health():
    return {"message": "OK"}
