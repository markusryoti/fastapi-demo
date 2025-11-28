from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models.user import User
from services.jwt import Token, create_access_token, decode_token
from services.password import verify_password
from services.users import get_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = decode_token(token)
    except Exception:
        raise credentials_exception

    if token_data.email is None:
        raise credentials_exception

    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception

    return user


def authenticate_user(email: str, password: str) -> User | None:
    user = get_user(email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email},
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return [{"item_id": "Foo", "owner": current_user.email}]
