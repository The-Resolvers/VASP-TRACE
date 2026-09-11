from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import trace
from app.core.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

app.include_router(trace.router, prefix="/api", tags=["trace"])

@app.get("/")
async def root():
    return {"message": "VASP Trace Engine API is running"}
