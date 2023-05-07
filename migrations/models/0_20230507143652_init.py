from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "service_content_anime_franchises" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name_en" VARCHAR(255),
    "name_ua" VARCHAR(255),
    "updated" TIMESTAMP,
    "scored_by" INT NOT NULL  DEFAULT 0,
    "score" DOUBLE PRECISION NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "service_content_anime" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "title_ja" VARCHAR(255),
    "title_en" VARCHAR(255),
    "title_ua" VARCHAR(255),
    "synopsis_en" TEXT,
    "synopsis_ua" TEXT,
    "content_id" VARCHAR(36) NOT NULL UNIQUE,
    "needs_update" BOOL NOT NULL  DEFAULT False,
    "slug" VARCHAR(255) NOT NULL,
    "updated" TIMESTAMP NOT NULL,
    "media_type" VARCHAR(16),
    "rating" VARCHAR(16),
    "source" VARCHAR(16),
    "status" VARCHAR(16),
    "scored_by" INT   DEFAULT 0,
    "score" DOUBLE PRECISION   DEFAULT 0,
    "start_date" TIMESTAMP,
    "end_date" TIMESTAMP,
    "duration" INT,
    "episodes" INT,
    "nsfw" BOOL,
    "translations" JSONB NOT NULL,
    "synonyms" JSONB NOT NULL,
    "external" JSONB NOT NULL,
    "videos" JSONB NOT NULL,
    "stats" JSONB NOT NULL,
    "ost" JSONB NOT NULL,
    "franchise_id" UUID REFERENCES "service_content_anime_franchises" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_service_con_content_ea4f27" ON "service_content_anime" ("content_id");
CREATE INDEX IF NOT EXISTS "idx_service_con_media_t_f423ee" ON "service_content_anime" ("media_type");
CREATE INDEX IF NOT EXISTS "idx_service_con_rating_c9f1fc" ON "service_content_anime" ("rating");
CREATE INDEX IF NOT EXISTS "idx_service_con_source_c3a968" ON "service_content_anime" ("source");
CREATE INDEX IF NOT EXISTS "idx_service_con_status_2ae8c8" ON "service_content_anime" ("status");
CREATE TABLE IF NOT EXISTS "service_content_anime_episodes" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "title_ja" TEXT,
    "title_en" TEXT,
    "title_ua" TEXT,
    "aired" TIMESTAMP,
    "index" INT NOT NULL,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "service_content_anime_genres" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name_en" VARCHAR(64),
    "name_ua" VARCHAR(64),
    "content_id" VARCHAR(36) NOT NULL UNIQUE,
    "slug" VARCHAR(255) NOT NULL UNIQUE,
    "type" VARCHAR(32) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_service_con_content_3fc243" ON "service_content_anime_genres" ("content_id");
CREATE INDEX IF NOT EXISTS "idx_service_con_slug_aedc6b" ON "service_content_anime_genres" ("slug");
CREATE TABLE IF NOT EXISTS "service_content_anime_recommendations" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "weight" INT NOT NULL,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "recommendation_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_service_con_anime_i_0e8666" UNIQUE ("anime_id", "recommendation_id")
);
CREATE TABLE IF NOT EXISTS "service_content_characters" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name_ja" VARCHAR(255),
    "name_en" VARCHAR(255),
    "name_ua" VARCHAR(255),
    "content_id" VARCHAR(36) NOT NULL UNIQUE,
    "favorites" INT   DEFAULT 0,
    "slug" VARCHAR(255) NOT NULL,
    "updated" TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_service_con_content_55d7ce" ON "service_content_characters" ("content_id");
CREATE TABLE IF NOT EXISTS "service_content_anime_characters" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "main" BOOL NOT NULL,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "character_id" UUID NOT NULL REFERENCES "service_content_characters" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_service_con_anime_i_fa3a59" UNIQUE ("anime_id", "character_id")
);
CREATE TABLE IF NOT EXISTS "service_content_companies" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name" VARCHAR(255),
    "content_id" VARCHAR(36) NOT NULL UNIQUE,
    "favorites" INT   DEFAULT 0,
    "slug" VARCHAR(255) NOT NULL,
    "updated" TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_service_con_content_6949c6" ON "service_content_companies" ("content_id");
CREATE TABLE IF NOT EXISTS "service_content_people" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "name_native" VARCHAR(255),
    "name_en" VARCHAR(255),
    "name_ua" VARCHAR(255),
    "content_id" VARCHAR(36) NOT NULL UNIQUE,
    "favorites" INT   DEFAULT 0,
    "slug" VARCHAR(255) NOT NULL,
    "updated" TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_service_con_content_acea66" ON "service_content_people" ("content_id");
CREATE TABLE IF NOT EXISTS "service_content_anime_staff" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "role" TEXT,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "person_id" UUID NOT NULL REFERENCES "service_content_people" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_service_con_anime_i_45bde3" UNIQUE ("anime_id", "person_id")
);
CREATE TABLE IF NOT EXISTS "service_content_anime_voices" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "language" VARCHAR(32) NOT NULL,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "character_id" UUID NOT NULL REFERENCES "service_content_characters" ("id") ON DELETE CASCADE,
    "person_id" UUID NOT NULL REFERENCES "service_content_people" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_service_con_anime_i_b0d585" UNIQUE ("anime_id", "character_id", "person_id")
);
CREATE INDEX IF NOT EXISTS "idx_service_con_languag_70145d" ON "service_content_anime_voices" ("language");
CREATE TABLE IF NOT EXISTS "service_users" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "username" VARCHAR(16) NOT NULL UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "description" VARCHAR(140),
    "password_hash" VARCHAR(60) NOT NULL,
    "activated" BOOL NOT NULL  DEFAULT False,
    "banned" BOOL NOT NULL  DEFAULT False,
    "last_active" TIMESTAMP NOT NULL,
    "created" TIMESTAMP NOT NULL,
    "login" TIMESTAMP NOT NULL,
    "activation_token" VARCHAR(64),
    "activation_expire" TIMESTAMP,
    "password_reset_token" VARCHAR(64),
    "password_reset_expire" TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_service_use_usernam_0fb1bb" ON "service_users" ("username");
CREATE INDEX IF NOT EXISTS "idx_service_use_email_64d6c5" ON "service_users" ("email");
CREATE TABLE IF NOT EXISTS "service_favourite_anime" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created" TIMESTAMP NOT NULL,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "service_users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_service_fav_user_id_30b108" UNIQUE ("user_id", "anime_id")
);
CREATE TABLE IF NOT EXISTS "service_watch" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "status" VARCHAR(16) NOT NULL,
    "user_score" INT NOT NULL  DEFAULT 0,
    "episodes" INT NOT NULL  DEFAULT 0,
    "note" TEXT,
    "created" TIMESTAMP NOT NULL,
    "updated" TIMESTAMP NOT NULL,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "service_users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_service_wat_user_id_8a5313" UNIQUE ("user_id", "anime_id")
);
CREATE TABLE IF NOT EXISTS "service_auth_tokens" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "secret" VARCHAR(64) NOT NULL UNIQUE,
    "expiration" TIMESTAMP NOT NULL,
    "created" TIMESTAMP NOT NULL,
    "user_id" UUID NOT NULL REFERENCES "service_users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_service_aut_secret_16cb2e" ON "service_auth_tokens" ("secret");
CREATE TABLE IF NOT EXISTS "service_email_messages" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "sent_time" TIMESTAMP,
    "sent" BOOL NOT NULL  DEFAULT False,
    "type" VARCHAR(32) NOT NULL,
    "created" TIMESTAMP NOT NULL,
    "content" TEXT NOT NULL,
    "receiver_id" UUID NOT NULL REFERENCES "service_users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "service_relation_anime_studios" (
    "service_content_anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "company_id" UUID NOT NULL REFERENCES "service_content_companies" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "service_relation_anime_producers" (
    "service_content_anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE,
    "company_id" UUID NOT NULL REFERENCES "service_content_companies" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "service_relation_anime_genres" (
    "service_content_anime_genres_id" UUID NOT NULL REFERENCES "service_content_anime_genres" ("id") ON DELETE CASCADE,
    "anime_id" UUID NOT NULL REFERENCES "service_content_anime" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "service_user_followers" (
    "service_users_id" UUID NOT NULL REFERENCES "service_users" ("id") ON DELETE CASCADE,
    "user_id" UUID NOT NULL REFERENCES "service_users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
