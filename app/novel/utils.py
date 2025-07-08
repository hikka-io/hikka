from app.schemas import NovelSearchArgs


def build_novel_filters_ms(search: NovelSearchArgs):
    status = [f"status = {status}" for status in search.status]

    media_type = [
        f"media_type = {media_type}" for media_type in search.media_type
    ]

    magazines = [f"magazines = {magazine}" for magazine in search.magazines]
    
    include_genres = []
    exclude_genres = []

    for genre in search.genres:
        if genre.startswith("-"):
            exclude_genres.append(f'genres != "{genre[1:]}"')
        else:
            include_genres.append(f'genres = "{genre}"')

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
        include_genres,
        exclude_genres,
        *score,
        *year,
    ]

    return [entry for entry in search_filters if entry]
