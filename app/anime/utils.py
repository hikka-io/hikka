from app.utils import enumerate_seasons
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

    include_genres = []
    exclude_genres = []

    for genre in search.genres:
        if genre.startswith("-"):
            exclude_genres.append(f"genres != {genre[1:]}")
        else:
            include_genres.append(f"genres = {genre}")

    translated = []
    score = []
    year = []

    # Score filters
    if search.score[0] and search.score[0] > 0:
        score.append([f"score>={search.score[0]}"])

    if search.score[1]:
        score.append([f"score<={search.score[1]}"])

    # Native score filters
    if search.native_score[0] and search.native_score[0] > 0:
        score.append([f"native_score>={search.native_score[0]}"])

    if search.native_score[1]:
        score.append([f"native_score<={search.native_score[1]}"])

    if search.only_translated:
        translated = ["translated_ua = true"]

    # Special filter for multi season titles
    airing_seasons = []

    if search.years[0] is not None and search.years[1] is not None:
        # Special filter for multi season titles
        if (
            search.include_multiseason
            and isinstance(search.years[0], int)
            and isinstance(search.years[1], int)
        ):
            for year_tmp in range(search.years[0], search.years[1] + 1):
                for season_tmp in search.season:
                    airing_seasons.append(
                        f"airing_seasons = {season_tmp}_{year_tmp}"
                    )

        # If user passed 2 complex year filters we build it here
        if isinstance(search.years[0], tuple) and isinstance(
            search.years[1], tuple
        ):
            airing_seasons += [
                f"airing_seasons = {airing_season}"
                for airing_season in enumerate_seasons(
                    search.years[0], search.years[1]
                )
            ]

    if search.years[0] and isinstance(search.years[0], int):
        year.append(f"year>={search.years[0]}")

    if search.years[1] and isinstance(search.years[1], int):
        year.append(f"year<={search.years[1]}")

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
        *include_genres,
        *exclude_genres,
        *score,
    ]

    return [entry for entry in search_filters if entry]
