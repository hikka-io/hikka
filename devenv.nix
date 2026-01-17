{ pkgs, lib, config, inputs, ... }:

let
  dbUser = "user";
  dbPass = "password";
  dbName = "hikka";

  meilisearch-1-4-2 = pkgs.stdenv.mkDerivation (finalAttrs: {
    pname = "meilisearch";
    version = "1.4.2";

    src = let
      system = pkgs.stdenv.hostPlatform.system;
      selectSource = url: hash: pkgs.fetchurl { inherit url hash; };
      sources = {
        "x86_64-linux" = selectSource
          "https://github.com/meilisearch/meilisearch/releases/download/v${finalAttrs.version}/meilisearch-linux-amd64"
          "sha256-tUuaziE7DUVVjF0OeXEPcYtj0uKcGQ+5W+Adwn6xylw=";
          
        "aarch64-darwin" = selectSource
          "https://github.com/meilisearch/meilisearch/releases/download/v${finalAttrs.version}/meilisearch-macos-apple-silicon"
          "sha256-jLeeSWGDtpls0Va7mUA7JxU05oW1qRzp6ie0f5V3TGI=";
      };
    in sources.${system} or (throw "Unsupported system: ${system}");

    dontUnpack = true;

    nativeBuildInputs = lib.optionals pkgs.stdenv.hostPlatform.isLinux [ 
      pkgs.autoPatchelfHook 
    ];

    buildInputs = lib.optionals pkgs.stdenv.hostPlatform.isLinux [ 
      pkgs.stdenv.cc.cc.lib 
    ];

    installPhase = ''
      runHook preInstall
      install -m755 -D $src $out/bin/meilisearch
      runHook postInstall
    '';

    meta = with lib; {
      description = "A lightning-fast search engine that fits effortlessly into your apps, websites, and workflow";
      homepage = "https://meilisearch.com";
      license = licenses.mit; 
      platforms = [ "x86_64-linux" "aarch64-darwin" ];
      mainProgram = "meilisearch";
      maintainers = [ Okashichan ];
    };
  });
in
{
  # https://devenv.sh/basics/
  # https://devenv.sh/packages/
  packages = [ pkgs.git pkgs.postgresql pkgs.postgresql.pg_config ];

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    
    # I'm not sure but eh
    version = lib.trim (builtins.readFile ./.python-version);
    
    poetry = {
      enable = true;
      install.enable = true;
    };
  };

  # https://devenv.sh/scripts/
  scripts.alembic-upgrade.exec = "alembic upgrade head";

  # https://devenv.sh/processes/
  processes.fastapi.exec = "uvicorn run:app --reload --port=8888";

  # https://devenv.sh/services/
  services = {
    meilisearch = {
      enable = true;
      package = meilisearch-1-4-2;
      listenPort = 8800;
    }; 
  };

  services.postgres = {
    enable = true;
    listen_addresses = "localhost";
    initialDatabases = [{ name = dbName; user = dbUser; pass = dbPass; }];
    initialScript = ''
      CREATE EXTENSION IF NOT EXISTS ltree;
      ALTER USER "${dbUser}" WITH SUPERUSER;
    '';
  };

  enterShell = ''
    python --version
    postgres --version
    alembic --version
    meilisearch --version
  '';

  env.DATABASE_URL = "postgresql+asyncpg://${dbUser}:${dbPass}@localhost:5432/${dbName}";

  # See full reference at https://devenv.sh/reference/options/
}