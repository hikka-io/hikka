# Hikka

Backend service for [hikka.io](https://hikka.io) - Ukrainian anime tracker.

## About The Project

### Built With

The list of frameworks, core libraries and software used in this project:

- [FastAPI](https://fastapi.tiangolo.com) - framework on top of which Hikka is build uppon
- [SQLAlchemy](https://www.sqlalchemy.org) - library to interact with our database
- [Alembic](https://alembic.sqlalchemy.org/en/latest) - tool for database migrations
- [APScheduler](https://github.com/agronholm/apscheduler) - task scheduling library
- [PostgreSQL](https://www.postgresql.org) - our main database software
- [meilisearch](https://www.meilisearch.com) - software for robust typo tolerant text search
- [pytest](https://docs.pytest.org) - helps us write better programs

And more!

## Getting Started

In order to get Hikka up and running on your local machine you must follow the following.

1. Clone this repository and enter project directory:
   ```sh
   git clone https://github.com/volbil/hikka.git
   cd hikka
   ```
2. Then choose one of the following installation methods:

[Option A — poetry (manual setup)](#option-a--poetry-manual-setup)

**Prerequisites**

This guide assumes you already have PostgreSQL installed and database named `hikka` created. For development you would also need [Poetry](https://python-poetry.org).

Optionally you also need to install Meilisearch [1.4.2](https://github.com/meilisearch/meilisearch/releases/tag/v1.4.2) to work with search. Please note this exact version must be installed because newer versions most likely contain API breaking changes.

[Option B — devenv (recommended)](#option-b--devenv-recommended)

**Prerequisites** 

Install [devenv](https://devenv.sh/getting-started/) before proceeding.

---

#### Option A — poetry (manual setup)

1. Create virtual environment and install dependencies using Poetry:
   ```sh
   poetry shell
   poetry install
   ```
2. Create `alembic.ini` and `settings.toml` files in project root directory, example configs can be found in [docs/](docs/). Make sure to update database endpoint since this is crucial for moving forward. We also suggest creating empty database for runnign tests and specifying it in `settings.toml` testing section.
3. Update database to latest migration:
   ```sh
   alembic upgrade head
   ```
4. Enable ltree extension in PostgreSQL by running (we need it for comments logic):
   ```sql
   CREATE EXTENSION IF NOT EXISTS ltree;
   ```
5. Now let's run tests to make sure everything is setup properly:
   ```sh
   pytest
   ```
6. If tests from previous step completed without any issues - congrats, now you can launch Hikka backend locally:
   ```sh
   uvicorn run:app --reload --port=8888
   ```

---

#### Option B — devenv (recommended)

[devenv](https://devenv.sh) provides a fully reproducible development environment that automatically manages PostgreSQL, Meilisearch, and all dependencies for you — no manual configuration needed.


1. Start all services (FastAPI, PostgreSQL, Meilisearch, pgweb):
   ```sh
   devenv up
   ```
   This launches the entire project stack. The following ports will be used:
   | Service      | Port |
   |--------------|------|
   | FastAPI      | 8888 |
   | PostgreSQL   | 5432 |
   | Meilisearch  | 8800 |
   | pgweb        | 8081 |
2. In a separate terminal, enter the dev shell to access project scripts:
   ```sh
   devenv shell
   ```
   Inside the shell, the following commands are available:
   | Command | Description |
   |---|---|
   | `run-test` | Run the test suite |
   | `alembic-upgrade` | Apply all pending database migrations |
   | `db-load-sample <hikka-sample.sql>` | Load a sample SQL dump and run migrations |

##### Customizing your local environment

You can override any devenv settings locally without touching the shared `devenv.nix`. Create a `devenv.local.nix` file in the project root — it is gitignored and intended for personal adjustments.

For example:
```nix
{ pkgs, lib, config, inputs, ... }:
{
  services.postgres.port = lib.mkForce 5433;
  services.meilisearch.listenPort = lib.mkForce 8900;

  files."settings.toml".toml.default = {
    backend.origins = lib.mkForce [ "http://localhost:3000" ];
    meilisearch.api_key = lib.mkForce "my-local-key";
    profiling.enabled = lib.mkForce false;
  };
}
```

> **Note:** `devenv.local.nix` is merged on top of `devenv.nix`, so you only need to specify the things you want to change.

## Contributing

Hikka is community driven project and we are always open to contributions. If you wish to make Hikka better here what you would need to do:

If you have a suggestion that would make this better, please fork the repo and create a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Here is couple suggestions which would ensure smooth cooperation:

- Write clean and concise code, we recommend using tools like [ruff](https://docs.astral.sh) to ensure code quality. Here is how we usually check code quality `ruff check app/`.
- Always write tests for your code, this would help us to review and accept your code faster.
- When creating pull request please write detailed explanation. This would make our work easier ;)

You can check our [Trello](https://trello.com/b/jJSSZccf/hikka) to see ideas for improvements proposed by our community as well as things we are currently working on.

We also suggest you to check out [our chat](https://t.me/hikka_io_chat) where we dwell. We can discuss and cooperate development there faster.

## License

Hikka is distributed under [AGPL-3.0-only](LICENSE.md). See `LICENSE.md` for more information.
