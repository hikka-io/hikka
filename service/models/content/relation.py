from tortoise import fields
from ..base import Base

class RelationBase(Base):
    relation_type = fields.CharField(index=True, max_length=32)

class AnimeToAnimeRelation(RelationBase):
    related: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="related_anime_to_anime"
    )

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="relations_anime_to_anime"
    )

    class Meta:
        table = "service_content_anime_to_anime_relations"

        unique_together = ("anime", "related")
