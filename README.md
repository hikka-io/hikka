# Hikka Backend

Run Hikka:

```bash
uvicorn run:app --reload --port=8888
```

## Migrations

```bash
alembic init -t async alembic
alembic revision --autogenerate -m "Migration name"
alembic upgrade head
```

## Aggregator SQL

```sql
SELECT count(*) FROM service_content_anime WHERE needs_update = true;

UPDATE service_content_anime SET needs_update = true;
```

## Meilisearch

```bash
./meilisearch --http-addr 127.0.0.1:8800 --env development --master-key xyz
```


```json
{"genres": ["supernatural", "drama"], "years": [1999, 2023], "season": ["summer"], "rating": ["r_plus"]}
```

## Ruff check

```bash
ruff check app/
```