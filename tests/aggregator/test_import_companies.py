from app.models import Company
from sqlalchemy import select
from sqlalchemy import func


async def test_import_companies(test_session, aggregator_companies):
    companies_count = await test_session.scalar(select(func.count(Company.id)))
    assert companies_count == 39

    # Check individual company
    company = await test_session.scalar(
        select(Company).filter(Company.slug == "mappa-360033")
    )

    assert company is not None
    assert company.name == "MAPPA"
    assert company.favorites == 25846
