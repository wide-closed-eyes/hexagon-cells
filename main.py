from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.core.hexagon import H3CellsStorage


async def lifespan(app):
    h3_storage = H3CellsStorage()
    app.state.h3_storage = h3_storage

    yield


app = FastAPI(title="H3 API", version="0.0.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=api_router)
