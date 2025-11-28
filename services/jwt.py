from datetime import datetime, timedelta, timezone

import jwt
from pydantic import BaseModel

SECRET_KEY = "857e52df766ab85c6931c30813dc741e21dc59545f3ab8dac85fac7becc5aa62"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update(
        {
            "iss": "fastapi-demo",
            "aud": ["urn:fastapi-demo-clients"],
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
    )
    encoded_jwt = jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            key=SECRET_KEY,
            algorithms=[ALGORITHM],
            audience="urn:fastapi-demo-clients",
        )
        sub = payload.get("sub")
        if sub is None:
            raise Exception("sub field is missing")
        token_data = TokenData(email=sub)
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

    return token_data
