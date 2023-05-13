from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "service_content_anime" ADD "season" VARCHAR(6);
        ALTER TABLE "service_content_anime" ADD "year" INT;
        CREATE INDEX "idx_service_con_season_a699bc" ON "service_content_anime" ("season");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX "idx_service_con_season_a699bc";
        ALTER TABLE "service_content_anime" DROP COLUMN "season";
        ALTER TABLE "service_content_anime" DROP COLUMN "year";"""
