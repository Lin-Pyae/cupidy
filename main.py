from fastapi import FastAPI
from cupidy.middleware.auth import ExampleMiddleware
from cupidy.api import api_router

app = FastAPI()

app.add_middleware(ExampleMiddleware)
app.include_router(api_router, prefix="/api/v1")