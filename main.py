from contextlib import asynccontextmanager

from fastapi import FastAPI
from alembic.config import Config
from alembic import command

from routers import auth, todos, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    # Run migrations using Alembic CLI
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield

    print("Shutting down application...")


app = FastAPI(lifespan=lifespan)


app.include_router(todos.router, prefix="/todos", tags=["Todos"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
