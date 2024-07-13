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
    try:
        new_token_set = validate_refresh_token(refresh_token["refresh_token"])
    except Exception as e:
        return {"error": str(e)}
    return new_token_set
