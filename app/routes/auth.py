from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import requests
import os
import pymongo
from datetime import datetime, timedelta
from ..util.utils import read_json, get_mongo_collection

router = APIRouter()

SECRET_KEY = "INeedJWT"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


mongo_config_file_path = os.path.join(os.path.dirname(__file__), '../config', 'mongo_config.json')
mongo_config_file_content = read_json(mongo_config_file_path)
client = pymongo.MongoClient()
users_collection = get_mongo_collection(client, mongo_config_file_content["user_collection_name"])


def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire, "sub": str(data.get("sub"))})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(user_id: int):
    user = users_collection.find_one({"user_id": user_id})
    return user


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id


@router.post("/token")
async def login_for_access_token(user_id: int, password: str):
    user = get_user(user_id)
    if len(user) == 0 or password != user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_jwt_token({"sub": user["user_id"]}), "token_type": "bearer"}


def get_jwt_token(user_id, password):
    response = requests.post(
        "http://localhost:8000/auth/token",
        data={"user_id": int(user_id), "password": password}
    )
    return response.json().get("access_token", None)

