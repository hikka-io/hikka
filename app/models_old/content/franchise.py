from ..base import Base, NativeDatetimeField
from tortoise import fields


class AnimeFranchise(Base):
    # Multilang fields
    name_en = fields.CharField(null=True, max_length=255)
    name_ua = fields.CharField(null=True, max_length=255)

    updated = NativeDatetimeField(null=True)
    scored_by = fields.IntField(default=0)
    score = fields.FloatField(default=0)

    anime: fields.ReverseRelation["Anime"]

    class Meta:
        table = "service_content_anime_franchises"
