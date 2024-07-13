from starlette.middleware.base import BaseHTTPMiddleware
from starlette.authentication import AuthenticationBackend, AuthenticationError
from starlette.requests import Request
import jwt
from jwt import InvalidSignatureError, ExpiredSignatureError
from fastapi.responses import JSONResponse
from fastapi import HTTPException

def checkTokenValidation(token):
    try:
        decode = jwt.decode(token,"secretkeyforcupidy","HS256")
    except InvalidSignatureError:
        raise AuthenticationError("Invalid token type")
    except ExpiredSignatureError:
        raise AuthenticationError("Token already expired")
    except:
        raise AuthenticationError("Unknown token error")
    
class AccessToken(AuthenticationBackend):
    async def authenticate(self, request: Request):
        if request.url.path.endswith(('login','refresh')):
            return
        if "Authorization" not in request.headers:
            raise AuthenticationError("Please provide Authorization in headers")
        checkTokenValidation(request.headers["Authorization"].split(" ")[1])
        