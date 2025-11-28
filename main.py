from contextlib import asynccontextmanager

from fastapi import FastAPI

from infrastructure.db.db import init_db
from routers import auth, todos, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    init_db()

    yield

    print("Shutting down application...")


app = FastAPI(lifespan=lifespan)


app.include_router(todos.router, prefix="/todos", tags=["Todos"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
