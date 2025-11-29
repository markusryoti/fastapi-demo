# FastAPI demo

## Migrations

```bash
uv run alembic init migrations
uv run alembic revision --autogenerate -m "<Migration name>"
uv run alembic upgrade head
```
