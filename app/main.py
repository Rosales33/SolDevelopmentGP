from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.artists import router as artists_router
from app.routers.albums import router as albums_router
from app.routers.tracks import router as tracks_router


app = FastAPI(title="Chinook API")

app.include_router(health_router)
app.include_router(artists_router)
app.include_router(albums_router)
app.include_router(tracks_router)
