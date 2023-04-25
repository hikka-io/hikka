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
    start_date = NativeDatetimeField(null=True)
    end_date = NativeDatetimeField(null=True)
    duration = fields.IntField(null=True)
    episodes = fields.IntField(null=True)
    nsfw = fields.BooleanField(null=True)

    # ToDo: images

    # # Content relations
    # anitube: fields.ManyToManyRelation["AnitubeAnime"] = fields.ManyToManyField(
    #     "models.AnitubeAnime", related_name="mal",
    #     through="service_relation_mal_anitube"
    # )

    # toloka: fields.ManyToManyRelation["TolokaAnime"] = fields.ManyToManyField(
    #     "models.TolokaAnime", related_name="mal",
    #     through="service_relation_mal_toloka"
    # )


    studios: fields.ManyToManyRelation["MALCompany"] = fields.ManyToManyField(
        "models.Company", related_name="studio_anime",
        through="service_relation_anime_studios"
    )

    producers: fields.ManyToManyRelation["MALCompany"] = fields.ManyToManyField(
        "models.Company", related_name="producer_anime",
        through="service_relation_anime_producers"
    )

    # franchise: fields.ForeignKeyRelation["MALAnimeFranchise"] = fields.ForeignKeyField(
    #     "models.MALAnimeFranchise", related_name="anime",
    #     null=True, on_delete=fields.SET_NULL
    # )

    # related_anime_to_anime: fields.ReverseRelation["MALAnimeToAnimeRelation"]
    # related_manga_to_anime: fields.ReverseRelation["MALMangaToAnimeRelation"]

    # relations_anime_to_manga: fields.ReverseRelation["MALAnimeToMangaRelation"]
    # recommended_to: fields.ReverseRelation["MALAnimeToAnimeRelation"]

    # recommendations: fields.ReverseRelation["MALAnimeRecommendation"]
    # recommended_to: fields.ReverseRelation["MALAnimeToAnimeRelation"]

    # synonyms: fields.ManyToManyRelation["MALAnimeSynonym"]
    genres: fields.ManyToManyRelation["AnimeGenre"]

    # episodes_list: fields.ReverseRelation["MALAnimeEpisodes"]
    # characters: fields.ReverseRelation["MALAnimeCharacter"]
    # external: fields.ReverseRelation["MALAnimeExternal"]
    # images: fields.ReverseRelation["MALAnimeImage"]
    # videos: fields.ReverseRelation["MALAnimeImage"]
    # voices: fields.ReverseRelation["MALAnimeVoice"]
    # stats: fields.ReverseRelation["MALAnimeStats"]
    # staff: fields.ReverseRelation["MALAnimeStaff"]
    # ost: fields.ReverseRelation["MALAnimeOST"]

    class Meta:
        table = "service_content_anime"
