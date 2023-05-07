from ..base import Base, NativeDatetimeField
from tortoise import fields


class Anime(Base):
    # Multilang fields
    title_ja = fields.CharField(null=True, max_length=255)
    title_en = fields.CharField(null=True, max_length=255)
    title_ua = fields.CharField(null=True, max_length=255)
    synopsis_en = fields.TextField(null=True)
    synopsis_ua = fields.TextField(null=True)

    # Service fields
    content_id = fields.CharField(max_length=36, unique=True, index=True)
    needs_update = fields.BooleanField(default=False)
    slug = fields.CharField(max_length=255)
    updated = NativeDatetimeField()

    # Metadata
    media_type = fields.CharField(null=True, max_length=16, index=True)
    rating = fields.CharField(null=True, max_length=16, index=True)
    source = fields.CharField(null=True, max_length=16, index=True)
    status = fields.CharField(null=True, max_length=16, index=True)
    scored_by = fields.IntField(null=True, default=0)
    score = fields.FloatField(null=True, default=0)
    total_episodes = fields.IntField(null=True)
    start_date = NativeDatetimeField(null=True)
    end_date = NativeDatetimeField(null=True)
    duration = fields.IntField(null=True)
    episodes = fields.IntField(null=True)
    nsfw = fields.BooleanField(null=True)

    translations = fields.JSONField(default=[])
    synonyms = fields.JSONField(default=[])
    external = fields.JSONField(default=[])
    videos = fields.JSONField(default=[])
    stats = fields.JSONField(default={})
    ost = fields.JSONField(default=[])

    # ToDo: images

    studios: fields.ManyToManyRelation["MALCompany"] = fields.ManyToManyField(
        "models.Company",
        related_name="studio_anime",
        through="service_relation_anime_studios",
    )

    producers: fields.ManyToManyRelation["MALCompany"] = fields.ManyToManyField(
        "models.Company",
        related_name="producer_anime",
        through="service_relation_anime_producers",
    )

    franchise: fields.ForeignKeyRelation[
        "AnimeFranchise"
    ] = fields.ForeignKeyField(
        "models.AnimeFranchise",
        related_name="anime",
        on_delete=fields.SET_NULL,
        null=True,
    )

    recommendations: fields.ReverseRelation["AnimeRecommendation"]
    recommended_to: fields.ReverseRelation["AnimeRecommendation"]

    episodes_list: fields.ReverseRelation["AnimeEpisodes"]
    characters: fields.ReverseRelation["AnimeCharacter"]
    voices: fields.ReverseRelation["AnimeVoice"]
    staff: fields.ReverseRelation["AnimeStaff"]

    genres: fields.ManyToManyRelation["AnimeGenre"]

    # images: fields.ReverseRelation["MALAnimeImage"]

    class Meta:
        table = "service_content_anime"
