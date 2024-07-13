from jwt import InvalidSignatureError, ExpiredSignatureError
from starlette.authentication import AuthenticationBackend, AuthenticationError
import jwt


def checkTokenValidation(token, secret_key):
    try:
        decode = jwt.decode(token,secret_key,"HS256")
    except InvalidSignatureError:
        raise AuthenticationError("Invalid token type")
    except ExpiredSignatureError:
        raise AuthenticationError("Token already expired")
    except:
        raise AuthenticationError("Unknown token error")