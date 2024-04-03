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

    # Special filter for multi season titles
    airing_seasons = []
    if (
        search.include_multiseason
        and search.years[0] is not None
        and search.years[1] is not None
    ):
        for year_tmp in range(search.years[0], search.years[1] + 1):
            for season_tmp in search.season:
                airing_seasons.append(
                    f"airing_seasons = {season_tmp}_{year_tmp}"
                )

    # I really hate this but we need it for multiseason titles
    # https://www.meilisearch.com/docs/reference/api/search#filter
    convoluted_filters = (
        [*year, *season]
        if len(airing_seasons) == 0
        else [[*year, *season], airing_seasons]
    )

    search_filters = [
        translated,
        media_type,
        producers,
        rating,
        status,
        source,
        studios,
        *convoluted_filters,
        *genres,
        *score,
    ]

    return [entry for entry in search_filters if entry]
