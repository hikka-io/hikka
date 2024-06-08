from app.schemas import MangaSearchArgs


def build_manga_filters_ms(search: MangaSearchArgs):
    status = [f"status = {status}" for status in search.status]

    media_type = [
        f"media_type = {media_type}" for media_type in search.media_type
    ]

    magazines = [f"magazines = {magazine}" for magazine in search.magazines]
    genres = [f"genres = {genre}" for genre in search.genres]

    translated = []
    score = []
    year = []

    if search.score[0] and search.score[0] > 0:
        score.append([f"score>={search.score[0]}"])

    if search.score[1]:
        score.append([f"score<={search.score[1]}"])

    if search.only_translated:
        translated = ["translated_ua = true"]

    if search.years[0]:
        year.append(f"year>={search.years[0]}")

    if search.years[1]:
        year.append(f"year<={search.years[1]}")

    search_filters = [
        translated,
        media_type,
        magazines,
        status,
        *genres,
        *score,
        *year,
    ]

    return [entry for entry in search_filters if entry]
