from .schemas import AnimeSearchArgs


def build_anime_filters(search: AnimeSearchArgs):
    rating = [f"rating = {rating}" for rating in search.rating]
    status = [f"status = {status}" for status in search.status]
    source = [f"source = {source}" for source in search.source]

    media_type = [
        f"media_type = {media_type}" for media_type in search.media_type
    ]

    season = [f"season = {season}" for season in search.season]
    producers = [f"producers = {producer}" for producer in search.producers]
    studios = [f"studios = {studio}" for studio in search.studios]
    genres = [f"genres = {genre}" for genre in search.genres]

    translated = []
    score = []
    year = []

    if search.years[0]:
        year.append([f"year>={search.years[0]}"])

    if search.years[1]:
        year.append([f"year<={search.years[1]}"])

    if search.score[0] and search.score[0] > 0:
        score.append([f"score>={search.score[0]}"])

    if search.score[1]:
        score.append([f"score<={search.score[1]}"])

    if search.only_translated:
        translated = ["translated_ua = true"]

    search_filters = [
        translated,
        rating,
        status,
        source,
        media_type,
        season,
        producers,
        studios,
        *genres,
        *year,
        *score,
    ]

    return [entry for entry in search_filters if entry]
