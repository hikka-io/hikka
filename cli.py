from app.database import sessionmanager
from app.settings import get_settings
from app.sync import update_search
import asyncio
import typer


app = typer.Typer()


async def session_wrapper(cli_function):
    settings = get_settings()
    sessionmanager.init(settings.database.endpoint)

    await cli_function

    await sessionmanager.close()


async def meilisearch_update():
    await session_wrapper(update_search())


@app.command()
def cli_meilisearch_update(name: str):
    asyncio.run(meilisearch_update())


if __name__ == "__main__":
    app()
