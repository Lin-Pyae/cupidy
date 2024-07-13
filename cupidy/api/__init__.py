from fastapi import APIRouter
from cupidy.api import auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/user")