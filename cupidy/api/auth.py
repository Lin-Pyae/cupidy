from fastapi import APIRouter, Body
from cupidy.services.auth import generate_token
from fastapi import HTTPException
from cupidy.services.auth import validate_refresh_token

router = APIRouter()

@router.get("/")
def example():
    return {"hello": "world"}

@router.get("/login")
def login():
    access_token, refresh_token = generate_token({"name":"johndoe","age":12})

    return {"access_token":access_token, "refresh_token":refresh_token}

@router.post("/refresh")
def get_new_access_token(refresh_token: dict = Body(...)):
    mock_db_data = {"name":"linpyae","rk":"hhh243"}
    return {validate_refresh_token(refresh_token["refresh_token"])}
