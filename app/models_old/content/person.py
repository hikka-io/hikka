from ..base import Base, NativeDatetimeField
from tortoise import fields

class Person(Base):
    name_native = fields.CharField(null=True, max_length=255)
    name_en = fields.CharField(null=True, max_length=255)
    name_ua = fields.CharField(null=True, max_length=255)

    content_id = fields.CharField(max_length=36, unique=True, index=True)
    favorites = fields.IntField(null=True, default=0)
    slug = fields.CharField(max_length=255)
    updated = NativeDatetimeField()

    # ToDo: initialized

    # ToDo: image

    class Meta:
        table = "service_content_people"
