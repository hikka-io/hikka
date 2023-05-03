from ..base import Base, NativeDatetimeField
from tortoise import fields

class AnimeEpisode(Base):
    title_ja = fields.TextField(null=True)
    title_en = fields.TextField(null=True)
    title_ua = fields.TextField(null=True)

    aired = NativeDatetimeField(null=True)
    index = fields.IntField()

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="episodes_list"
    )

    class Meta:
        table = "service_content_anime_episodes"
