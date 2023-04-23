from service.models import Company
from tortoise import Tortoise
from service import utils
from . import requests
import config

async def aggregator_companies():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    pages = 1
    page = 1

    while page <= pages:
        data = await requests.get_companies(page)
        pages = data["pagination"]["pages"]

        create_companies = []
        update_companies = []

        for company_data in data["list"]:
            updated = utils.from_timestamp(company_data["updated"])
            slug = utils.slugify(
                company_data["name"], company_data["reference"]
            )

            if company := await Company.filter(slug=slug).first():
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
                    "conetent_id": company_data["reference"],
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

        page += 1
