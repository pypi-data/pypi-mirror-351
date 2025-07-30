from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from typing import Any

import datetime as dt
import os
import koco_product_sqlmodel.mdb_connect.users as mdb_users
import koco_product_sqlmodel.dbmodels.models_enums as m_enums

SECRET_KEY = os.environ.get(key="FASTAPI_SECURITY_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

router = APIRouter(tags=["Endpoints to AUTHENTICATION data and methods"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class PWHelper(BaseModel):
    password_str: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str) -> mdb_users.sqlm.CUser | None:
    return mdb_users.get_user_by_name(name_str=username)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: dt.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = dt.datetime.now(dt.timezone.utc) + expires_delta
    else:
        expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[mdb_users.sqlm.CUser, Depends(get_current_user)],
):
    if current_user.role_id not in (
        m_enums.CUserRoleIdEnum.admin,
        m_enums.CUserRoleIdEnum.editor,
        m_enums.CUserRoleIdEnum.reader,
    ):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_user_id_from_request(request: Request) -> int:
    token = request.headers.get("Authorization")[7:]
    current_user = await get_current_user(token=token)
    user = await get_current_active_user(current_user=current_user)
    return user.id


async def has_post_rights(
    current_user: Annotated[mdb_users.sqlm.CUser, Depends(get_current_user)],
):
    if current_user.role_id == m_enums.CUserRoleIdEnum.reader:
        raise HTTPException(status_code=400, detail="Insufficient rights")
    return current_user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post(
    "/pwhelper",
    dependencies=[Depends(get_current_active_user), Depends(has_post_rights)],
)
async def generate_hashed_password(
    form_data: Annotated[PWHelper, Depends()],
) -> str:
    """
    Convenience function to generate password hashes as long as there is no sign-up workflow
    """
    return get_password_hash(password=form_data.password_str)


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[mdb_users.sqlm.CUser, Depends(get_current_active_user)],
) -> dict[str, Any]:
    return current_user.model_dump(exclude={"password"})


def main():
    pass


if __name__ == "__main__":
    main()
