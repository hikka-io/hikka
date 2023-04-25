from service.models import Company
from tortoise import Tortoise
from service import utils
from . import requests
import asyncio
import config

async def make_request(semaphore, page):
    async with semaphore:
        data = await requests.get_companies(page)
        return data["list"]
    
async def save_companies(data):
    references = [entry["reference"] for entry in data]

    cache = await Company.filter(content_id__in=references)

    companies_cache = {entry.content_id: entry for entry in cache}

    create_companies = []
    update_companies = []

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

            update_companies.append(company)

            print(f"Updated company: {company.name} ({company.favorites})")

        else:
            company = Company(**{
                "content_id": company_data["reference"],
                "favorites": company_data["favorites"],
                "name": company_data["name"],
                "updated": updated,
                "slug": slug
            })

            create_companies.append(company)

            print(f"Added company: {company.name} ({company.favorites})")

    await Company.bulk_create(create_companies)

    if len(update_companies) > 0:
        await Company.bulk_update(update_companies, fields=[
            "updated", "favorites"
        ])

async def aggregator_companies():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    data = await requests.get_companies(1)
    pages = data["pagination"]["pages"]

    semaphore = asyncio.Semaphore(20)
    tasks = [make_request(semaphore, page) for page in range(1, pages + 1)]

    result = await asyncio.gather(*tasks)

    data = [item for sublist in result for item in sublist]

    await save_companies(data)
