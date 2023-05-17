from app.database import sessionmanager
from app.models import Company
from sqlalchemy import select
from . import requests
from app import utils
import asyncio
import config


async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_companies(page)
        return data["list"]


async def save_companies(data):
    sessionmanager.init(config.database)

    async with sessionmanager.session() as session:
        references = [entry["reference"] for entry in data]

        cache = await session.scalars(
            select(Company).where(Company.content_id.in_(references))
        )

        companies_cache = {entry.content_id: entry for entry in cache}

        add_companies = []

        for company_data in data:
            updated = utils.from_timestamp(company_data["updated"])
            slug = utils.slugify(
                company_data["name"], company_data["reference"]
            )

            if company_data["reference"] in companies_cache:
                company = companies_cache[company_data["reference"]]

                if company.updated == updated:
                    continue

                if company.favorites == company_data["favorites"]:
                    continue

                company.favorites = company_data["favorites"]
                company.updated = updated

                add_companies.append(company)

                print(f"Updated company: {company.name} ({company.favorites})")

            else:
                company = Company(
                    **{
                        "content_id": company_data["reference"],
                        "favorites": company_data["favorites"],
                        "name": company_data["name"],
                        "updated": updated,
                        "slug": slug,
                    }
                )

                add_companies.append(company)

                print(f"Added company: {company.name} ({company.favorites})")

        session.add_all(add_companies)
        await session.commit()


async def aggregator_companies():
    data = await requests.get_companies(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    for data_chunk in utils.chunkify(data, 20000):
        await save_companies(data_chunk)
