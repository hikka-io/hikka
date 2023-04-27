from tortoise import fields
from ..base import Base

class AnimeStaff(Base):
    role = fields.TextField(null=True)

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="staff"
    )

    person: fields.ForeignKeyRelation["Person"] = fields.ForeignKeyField(
        "models.Person", related_name="staff_roles"
    )

    class Meta:
        table = "service_mal_anime_staff"

        unique_together = ("anime", "person")

class AnimeVoice(Base):
    language = fields.CharField(index=True, max_length=32)

    anime: fields.ForeignKeyRelation["Anime"] = fields.ForeignKeyField(
        "models.Anime", related_name="voices"
    )

    character: fields.ForeignKeyRelation["Character"] = fields.ForeignKeyField(
        "models.Character", related_name="voices"
    )

    person: fields.ForeignKeyRelation["Person"] = fields.ForeignKeyField(
        "models.Person", related_name="voice_roles"
    )

    class Meta:
        table = "service_mal_anime_voices"

        unique_together = ("anime", "character", "person")
