from ..base import Base, NativeDatetimeField
from tortoise import fields

class AnimeFavourite(Base):
    created = NativeDatetimeField()

    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="favourite"
    )

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="favourite"
    )

    class Meta:
        table = "service_favourite_anime"

        unique_together = ("user", "anime")
