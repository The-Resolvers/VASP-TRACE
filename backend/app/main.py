from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import trace
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings

import asyncio
from contextlib import asynccontextmanager
from app.services.osint_ingester import osint_ingester

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    # Start the OSINT ingester in the background
    ingester_task = asyncio.create_task(osint_ingester.run())
    yield
    # Shutdown
    osint_ingester.stop()
    await ingester_task
    await close_mongo_connection()

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trace.router, prefix="/api", tags=["trace"])

@app.get("/")
async def root():
    return {"message": "VASP Trace Engine API is running"}
