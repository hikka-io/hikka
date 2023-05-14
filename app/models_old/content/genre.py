from tortoise import fields
from ..base import Base

class GenreBase(Base):
    name_en = fields.CharField(null=True, max_length=64)
    name_ua = fields.CharField(null=True, max_length=64)

    content_id = fields.CharField(max_length=36, unique=True, index=True)
    slug = fields.CharField(unique=True, index=True, max_length=255)
    type = fields.CharField(max_length=32)

class AnimeGenre(GenreBase):
    anime: fields.ManyToManyRelation["Anime"] = fields.ManyToManyField(
        "models.Anime", related_name="genres",
        through="service_relation_anime_genres"
    )

    class Meta:
        table = "service_content_anime_genres"
