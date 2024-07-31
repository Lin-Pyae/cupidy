from fastapi import FastAPI
from cupidy.middleware.middleware import middleware_stack
from fastapi.middleware.cors import CORSMiddleware
from cupidy.api import api_router
from cupidy.db.repository.db import init_db

app = FastAPI(middleware=middleware_stack())

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
