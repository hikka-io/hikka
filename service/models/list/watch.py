from ..base import Base, NativeDatetimeField
from tortoise import fields

class AnimeWatch(Base):
    status = fields.CharField(max_length=16)
    user_score = fields.IntField(default=0)
    episodes = fields.IntField(default=0)
    note = fields.TextField(null=True)
    created = NativeDatetimeField()
    updated = NativeDatetimeField()

    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="watch"
    )

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="watch"
    )

    class Meta:
        table = "service_watch"

        unique_together = ("user", "anime")
