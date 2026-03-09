{ pkgs, lib, config, inputs, ... }:

let
  db = {
    user = "user";
    pass = "password";
    name = "hikka";
    connectionString = "postgresql+asyncpg://${db.user}:${db.pass}@localhost:${toString ports.postgres}/${db.name}";
  };

  credsString = "-h localhost -p ${toString ports.postgres} -U ${db.user} -d ${db.name}";

  ports = {
    fastapi = 8888;
    postgres = 5432;
    meilisearch = 8800;
    pgweb = 8081;
  };

  postgres-16-3 = inputs.nixpkgs-postgres.legacyPackages.${pkgs.stdenv.system}.postgresql_16;
  meilisearch-1-9 = inputs.nixpkgs-meilisearch.legacyPackages.${pkgs.stdenv.system}.meilisearch;
in
{
  # https://devenv.sh/basics/
  # https://devenv.sh/packages/
  packages = with pkgs; [ git pgweb ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    
    # I'm not sure but eh
    version = lib.trim (builtins.readFile ./.python-version);
    
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  # https://devenv.sh/scripts/
  scripts = {
    run-test.exec = "uv run pytest";

    alembic-upgrade.exec = "uv run alembic upgrade head";

    db-load-sample.exec = ''
      if [ -z "$1" ]; then
        echo "Usage: db-load-sample <hikka-sample.sql>"
        exit 1
      fi

      psql \
        -h localhost \
        -p ${toString ports.postgres} \
        -U ${db.user} \
        -d ${db.name} \
        -f $1

      alembic-upgrade
    '';
  };

  # https://devenv.sh/processes/
  processes = {
    fastapi.exec = ''
      uv run uvicorn \
      run:app \
      --reload \
      --port=${toString ports.fastapi}
    '';
    
    sync.exec = ''
      while ! pg_isready ${credsString}; do 
        sleep 1
      done
      
      TABLE_COUNT=$(psql \
        ${credsString} \
        -tAc "SELECT count(*) \
        FROM information_schema.tables \
        WHERE table_schema = 'public';")

      if [ "$TABLE_COUNT" -eq "0" ]; then
        echo "ERROR: Database is empty. Run 'db-load-sample <hikka-sample.sql>' and restart." >&2
        exit 0
      fi

      uv run sync.py
    '';

    pgweb.exec = ''
      while ! pg_isready ${credsString}; do 
        sleep 1
      done

      pgweb --bind=127.0.0.1 \
        --listen=${toString ports.pgweb} \
        --url="${lib.replaceStrings ["+asyncpg"] [""] db.connectionString}?sslmode=disable";
    '';
  };

  # https://devenv.sh/services/
  services = {
    postgres = {
      enable = true;
      package = postgres-16-3;
      port = ports.postgres;

      listen_addresses = "localhost";
      initialDatabases = [{ name = db.name; user = db.user; pass = db.pass; }];
      initialScript = ''
        CREATE EXTENSION IF NOT EXISTS ltree;
        ALTER USER "${db.user}" WITH SUPERUSER;
        CREATE ROLE postgres WITH LOGIN SUPERUSER;
      '';
    };

    meilisearch = {
      enable = true;
      package = meilisearch-1-9;
      listenPort = ports.meilisearch;
    }; 
  };

  enterShell = ''
    python --version
    postgres --version
    uv run alembic --version
    meilisearch --version
  '';

  files = { 
    "settings.toml".toml = {
      default = {
        oauth.google = {
          client_id = "xxx.apps.googleusercontent.com";
          client_secret = "secret";
          redirect_uri = "http://localhost:5173";
          enabled = true;
        };

        database = {
          endpoint = db.connectionString;
        };

        mailgun = {
          endpoint = "https://api.eu.mailgun.net/v3/mail.hikka.io/messages";
          token = "token";
          email_from = "Hikka <noreply@mail.hikka.io>";
        };

        meilisearch = {
          url = "http://127.0.0.1:8800";
          api_key = "xyz";
        };

        backend = {
          plausible = "http://127.0.0.1:8000";
          plausible_token = "TOKEN";
          aggregator = "http://aggregator.local/database";
          sitemap_path = "/Users/user/Work/Hikka/sitemap";
          auth_emails = [ ];
          origins = [
            "http://localhost:8000"
            "http://localhost:3000"
            "https://hikka.io"
          ];
        };

        backup = {
          token = "backup_token";
        };

        captcha = {
          secret_key = "captcha_secret";
          site_key = "captcha_key";
          test = "fake_captcha";
        };

        s3 = {
          key = "s3_key";
          secret = "s3_secret";
          endpoint = "https://endpoint.s3.provider.com";
          bucket = "hikka";
        };

        profiling = {
          enabled = true;
          trigger = "query"; # [query/all]
          path = ".profile_info";
          profiling_secret = "secret";
        };

        aggregator = {
          telegram_notifications = true;
          telegram_message_thread_id = "117779";
          telegram_chat_id = "-1002142457586";
          telegram_bot_token = "token";
        };
      };

      testing = {
        database = {
          endpoint = "postgresql+asyncpg://user:password@localhost:5432/database-tests";
        };

        oauth.google = {
          client_id = "xxx.apps.googleusercontent.com";
          client_secret = "secret";
          redirect_uri = "http://example.com/oauth/google";
          enabled = true;
        };

        meilisearch = {
          url = "http://127.0.0.1:9900";
          api_key = "zyx";
        };

        backend = {
          auth_emails = [ "user@mail.com" ];
          origins = [ ];
        };

        backup = {
          token = "backup_token";
        };

        captcha = {
          secret_key = "test_secter_key";
          site_key = "test_site_key";
          test = "fake_captcha";
        };

        s3 = {
          key = "FAKE_KEY";
          secret = "FAKE_SECRET";
          endpoint = "https://fake.s3.example.com";
          bucket = "hikka-test";
        };

        profiling = {
          enabled = false;
          trigger = "query"; # [query/all]
          path = ".profile_info";
          profiling_secret = "secret";
        };

        aggregator = {
          telegram_notifications = false;
        };
      };
    };

    "alembic.ini".ini = {
      alembic = {
        # Path to migration
        script_location = "alembic";
        
        # Template for migration names
        file_template = "%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s";
        
        # We need this to include archived migrations
        recursive_version_locations = true;
        
        # SQLAlchemy database endpoint
        "sqlalchemy.url" = db.connectionString;
        
        # Misc configs
        prepend_sys_path = ".";
        version_path_separator = "os";
      };

      # Logging configuration (misc)
      loggers = {
        keys = "root,sqlalchemy,alembic";
      };

      handlers = {
        keys = "console";
      };

      formatters = {
        keys = "generic";
      };

      logger_root = {
        level = "WARN";
        handlers = "console";
        qualname = "";
      };

      logger_sqlalchemy = {
        level = "WARN";
        handlers = "";
        qualname = "sqlalchemy.engine";
      };

      logger_alembic = {
        level = "INFO";
        handlers = "";
        qualname = "alembic";
      };

      handler_console = {
        class = "StreamHandler";
        args = "(sys.stderr,)";
        level = "NOTSET";
        formatter = "generic";
      };

      formatter_generic = {
        format = "%(levelname)-5.5s [%(name)s] %(message)s";
        datefmt = "%H:%M:%S";
      };
    };
  };

  env.PGPASSWORD = db.pass;

  # See full reference at https://devenv.sh/reference/options/
}