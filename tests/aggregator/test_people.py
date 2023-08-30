from app.models import Person
from sqlalchemy import select
from sqlalchemy import func


async def test_import_people(test_session, aggregator_people):
    people_count = await test_session.scalar(select(func.count(Person.id)))
    assert people_count == 401

    # Check individual person
    person = await test_session.scalar(
        select(Person).filter(Person.slug == "shinichi-omata-9f95e6")
    )

    assert person is not None
    assert person.name_en == "Shinichi Omata"
    assert person.favorites == 235
