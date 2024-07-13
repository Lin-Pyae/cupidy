import jwt
import datetime, secrets
from cupidy.services.util import checkTokenValidation

at_secret_key = "secretkeyforcupidy"
rt_secret_key = "refreshkey"
access_token_expire_seconds = 30
refresh_token_expire_seconds = 60

def generate_token(usr_data):
    access_expire  = datetime.datetime.utcnow() + datetime.timedelta(seconds=access_token_expire_seconds)
    usr_data["exp"] = access_expire
    encoded_access_token = jwt.encode(usr_data,at_secret_key,algorithm="HS256")
    return encoded_access_token, generate_refresh_token()

def generate_refresh_token():
    refresh_expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=refresh_token_expire_seconds)
    encode_refresh_token = jwt.encode({"exp":refresh_expire},rt_secret_key,algorithm="HS256")
    return encode_refresh_token


def validate_refresh_token(refresh_token):
    checkTokenValidation(refresh_token,rt_secret_key)
    access_token = generate_token({"name":"johndoe","age":12})
    refresh_token = generate_refresh_token()
    return {"access_token":access_token,"refresh_token":refresh_token}
    

