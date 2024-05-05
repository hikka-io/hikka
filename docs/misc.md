# Misc (old readme)

## Migrations

```bash
alembic init -t async alembic
alembic revision --autogenerate -m "Migration name"
alembic upgrade head
```


## Meilisearch

```bash
./meilisearch --http-addr 127.0.0.1:8800 --env development --master-key xyz
```

## Ruff check

```bash
ruff check app/
```

## PostgreSQL

Enable Ltree:
```sql
CREATE EXTENSION IF NOT EXISTS ltree;
```
