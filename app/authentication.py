from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

SECRET_KEY = "port2portbackendtotemsecretkey"
ALGORITHM = "HS256"
oauth_scheme = HTTPBearer()


def create_jwt_token(id: int, email: str, is_seller:bool = False):
    payload = {"id": id, "email": email, "is_seller": is_seller}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decrypt_jwt_token(token: str):
    payload =  jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload

def get_token_from_request(token: HTTPAuthorizationCredentials = Depends(oauth_scheme)):
    return token.credentials

def get_current_user(token: str = Depends(get_token_from_request)):
    return decrypt_jwt_token(token)