from fastapi import FastAPI
from cupidy.middleware.middleware import middleware_stack
from cupidy.api import api_router

app = FastAPI(middleware=middleware_stack())

app.include_router(api_router, prefix="/api/v1")