from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers import articles, categories, tags, tokens, users, websockets, files

app = FastAPI(root_path="/api")
# app = FastAPI()
app.mount("/api/images", StaticFiles(directory="images"), name="images")

app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(tags.router)
app.include_router(tokens.router)
app.include_router(users.router)
app.include_router(websockets.router)
app.include_router(files.router)
