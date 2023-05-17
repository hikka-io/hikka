from ..base import Base, NativeDatetimeField
from tortoise import fields


class Character(Base):
    name_ja = fields.CharField(null=True, max_length=255)
    name_en = fields.CharField(null=True, max_length=255)
    name_ua = fields.CharField(null=True, max_length=255)

    content_id = fields.CharField(max_length=36, unique=True, index=True)
    favorites = fields.IntField(null=True, default=0)
    slug = fields.CharField(max_length=255)
    updated = NativeDatetimeField()

    # ToDo: initialized

    # ToDo: image

    class Meta:
        table = "service_content_characters"


class AnimeCharacter(Base):
    main = fields.BooleanField()

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="characters"
    )

    character: fields.ForeignKeyRelation["Character"] = fields.ForeignKeyField(
        "models.Character", related_name="anime_roles"
    )

    class Meta:
        table = "service_content_anime_characters"

        unique_together = ("anime", "character")
