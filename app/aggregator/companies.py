from app.models import Company, Image
from sqlalchemy import select
from app.utils import utcnow
from app import utils


async def save_companies(session, data):
    content_ids = [entry["content_id"] for entry in data]
    images = [entry["image"] for entry in data]

    cache = await session.scalars(
        select(Company).where(Company.content_id.in_(content_ids))
    )

    companies_cache = {entry.content_id: entry for entry in cache}

    cache = await session.scalars(select(Image).where(Image.path.in_(images)))

    image_cache = {entry.path: entry for entry in cache}

    add_companies = []

    for company_data in data:
        updated = utils.from_timestamp(company_data["updated"])
        slug = utils.slugify(
            company_data["name_en"], company_data["content_id"]
        )

        if company_data["content_id"] in companies_cache:
            company = companies_cache[company_data["content_id"]]

            if company.updated == updated:
                continue

            if company.favorites == company_data["favorites"]:
                continue

            company.favorites = company_data["favorites"]
            company.updated = updated

            add_companies.append(company)

            # print(f"Updated company: {company.name} ({company.favorites})")

        else:
            if not (image := image_cache.get(company_data["image"])):
                if company_data["image"]:
                    image = Image(
                        **{
                            "path": company_data["image"],
                            "created": utcnow(),
                            "uploaded": True,
                            "ignore": False,
                        }
                    )

                    image_cache[company_data["image"]] = image

            company = Company(
                **{
                    "needs_search_update": True,
                    "content_id": company_data["content_id"],
                    "favorites": company_data["favorites"],
                    "name": company_data["name_en"],
                    "image_relation": image,
                    "updated": updated,
                    "slug": slug,
                }
            )

            add_companies.append(company)

            # print(f"Added company: {company.name} ({company.favorites})")

    session.add_all(add_companies)
    await session.commit()
