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

In order to get Hikka up and running on your local machine you must follow this steps.

### Prerequisites

This guide assumes you already have PostgreSQL installed and database named `hikka` created. For development you would also need [Poetry](https://python-poetry.org).

Optionally you also need to install Meilisearch [1.4.2](https://github.com/meilisearch/meilisearch/releases/tag/v1.4.2) installed for working with. Please node this specific version must be installed because newer versions most likely contain API breaking changes.

### Installation

1. Clone this repository and enter project directory:
   ```sh
   git clone https://github.com/volbil/hikka.git
   cd hikka
   ```
2. Create virtual environment and install dependencies using Poetry:
   ```sh
   poetry shell
   poetry install
   ```
3. Create `alembic.ini` and `settings.toml` files in project root directory, example configs can be found in [docs/](docs/). Make sure to update database endpoint since this is crucial for moving forward. We also suggest creating empty database for runnign tests and specifying it in `settings.toml` testing section.
4. Update database to latest migration (keep in mind that migraiton id here might be outdated by now and you should always check [alembic/versions/](alembic/versions/) for latest migration):
   ```sh
   alembic upgrade 0c8a96ac77c9
   ```
6. Enable ltree extension in PostgreSQL by running (we need it for comments logic):
   ```sql
   CREATE EXTENSION IF NOT EXISTS ltree;
   ```
7. Now let's run tests to make sure everything is setup properly:
   ```sh
   pytest
   ```
8. If tests from previous step completed without any issues - congrats, now you can launch Hikka backend locally:
   ```sh
   uvicorn run:app --reload --port=8888
   ```

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
