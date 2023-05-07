# Hikka Backend

Run Hikka:

```bash
uvicorn run:app --reload --port=8888
```

## Migrations

```bash
aerich init -t config.tortoise
aerich init-db
aerich migrate --name migration_name
aerich upgrade
aerich downgrade
```

## Aggregator SQL

```sql
SELECT count(*) FROM service_content_anime WHERE needs_update = true;

UPDATE service_content_anime SET needs_update = true;
```
