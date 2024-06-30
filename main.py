from fastapi import FastAPI
from cupidy.middleware.auth import ExampleMiddleware
from cupidy.api import api_router

app = FastAPI()

app.add_middleware(ExampleMiddleware)

# Test route
@app.get("/")
def read_root():
    return {"message": "Welcome to Cupidy API"}

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)