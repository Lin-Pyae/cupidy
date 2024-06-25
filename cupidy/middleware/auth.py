from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class ExampleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("hello")
        # Process request here (e.g., logging, authentication)
        response = await call_next(request)
        # Process response here (e.g., adding headers)
        return response