from tortoise import fields
from ..base import Base

class RecommendationBase(Base):
    weight = fields.IntField()

class AnimeRecommendation(RecommendationBase):
    recommendation: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="recommended_to"
    )

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="recommendations"
    )

    class Meta:
        table = "service_content_anime_recommendations"

        unique_together = ("anime", "recommendation")
