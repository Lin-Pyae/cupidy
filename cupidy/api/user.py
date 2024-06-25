from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def example():
    return {"hello": "world"}