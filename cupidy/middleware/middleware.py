from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from cupidy.middleware.auth import AccessToken


def middleware_stack():
    stack = list()
    stack.append(Middleware(
        AuthenticationMiddleware,
        backend=AccessToken()))
    
    return stack

    
