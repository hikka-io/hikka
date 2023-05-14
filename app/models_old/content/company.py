from ..base import Base, NativeDatetimeField
from tortoise import fields


class Company(Base):
    name = fields.CharField(null=True, max_length=255)

    content_id = fields.CharField(max_length=36, unique=True, index=True)
    slug = fields.CharField(index=True, max_length=255)
    favorites = fields.IntField(null=True, default=0)
    updated = NativeDatetimeField()

    producer_anime: fields.ManyToManyRelation["Anime"]
    studio_anime: fields.ManyToManyRelation["Anime"]

    # ToDo: image

    class Meta:
        table = "service_content_companies"
