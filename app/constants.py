# Email types
EMAIL_ACTIVATION = "activation"
EMAIL_PASSWORD_RESET = "password_reset"

# Aggregator endpoint
AGGREGATOR = "http://localhost:7777/database"

# CDN endpoing
CDN_ENDPOINT = "https://cdn.hikka.io"

# Watch list statuses
WATCH_PLANNED = "planned"
WATCH_WATCHING = "watching"
WATCH_COMPLETED = "completed"
WATCH_ON_HOLD = "on_hold"
WATCH_DROPPED = "dropped"

WATCH = [
    WATCH_PLANNED,
    WATCH_WATCHING,
    WATCH_COMPLETED,
    WATCH_ON_HOLD,
    WATCH_DROPPED,
]

# Seasons
SEASON_WINTER = "winter"
SEASON_SPRING = "spring"
SEASON_SUMMER = "summer"
SEASON_FALL = "fall"

RELEASE_STATUS_DISCONTINUED = "discontinued"
RELEASE_STATUS_ANNOUNCED = "announced"
RELEASE_STATUS_FINISHED = "finished"
RELEASE_STATUS_ONGOING = "ongoing"
RELEASE_STATUS_PAUSED = "paused"

MEDIA_TYPE_SPECIAL = "special"
MEDIA_TYPE_MOVIE = "movie"
MEDIA_TYPE_MUSIC = "music"
MEDIA_TYPE_OVA = "ova"
MEDIA_TYPE_ONA = "ona"
MEDIA_TYPE_TV = "tv"

AGE_RATING_R_PLUS = "r_plus"
AGE_RATING_PG_13 = "pg_13"
AGE_RATING_PG = "pg"
AGE_RATING_RX = "rx"
AGE_RATING_G = "g"
AGE_RATING_R = "r"

VIDEO_PROMO = "video_promo"
VIDEO_MUSIC = "video_music"

OST_OPENING = "opening"
OST_ENDING = "ending"

SOURCE_DIGITAL_MANGA = "digital_manga"
SOURCE_PICTURE_BOOK = "picture_book"
SOURCE_VISUAL_NOVEL = "visual_novel"
SOURCE_4_KOMA_MANGA = "4_koma_manga"
SOURCE_LIGHT_NOVEL = "light_novel"
SOURCE_CARD_GAME = "card_game"
SOURCE_WEB_MANGA = "web_manga"
SOURCE_ORIGINAL = "original"
SOURCE_MANGA = "manga"
SOURCE_MUSIC = "music"
SOURCE_NOVEL = "novel"
SOURCE_OTHER = "other"
SOURCE_RADIO = "radio"
SOURCE_GAME = "game"
SOURCE_BOOK = "book"

SEARCH_RESULT_LIMIT = 12

# Meilisearch index names
SEARCH_INDEX_CHARACTERS = "content_characters"
SEARCH_INDEX_COMPANIES = "content_companies"
SEARCH_INDEX_PEOPLE = "content_people"
SEARCH_INDEX_ANIME = "content_anime"

COMPANY_ANIME_PRODUCER = "producer"
COMPANY_ANIME_STUDIO = "studio"

EDIT_PENDING = "pending"
EDIT_APPROVED = "approved"
EDIT_DENIED = "denied"
EDIT_CLOSED = "closed"

CONTENT_ANIME = "anime"
CONTENT_MANGA = "manga"
CONTENT_CHARACTER = "character"
CONTENT_COMPANY = "company"
CONTENT_EPISODE = "episode"
CONTENT_GENRE = "genre"
CONTENT_PERSON = "person"
CONTENT_STAFF = "staff"

# Roles
# ToDo: move to separate file (?)
ROLE_USER = "user"
ROLE_MODERATOR = "moderator"
ROLE_ADMIN = "admin"

# Permissions
PERMISSION_CREATE_EDIT = "content:create_edit"
PERMISSION_ACCEPT_EDIT = "content:accept_edit"
PERMISSION_REJECT_EDIT = "content:reject_edit"

# Role permissions
ROLES = {
    ROLE_USER: [
        PERMISSION_CREATE_EDIT,
    ],
    ROLE_MODERATOR: [
        PERMISSION_CREATE_EDIT,
        PERMISSION_ACCEPT_EDIT,
        PERMISSION_REJECT_EDIT,
    ],
    ROLE_ADMIN: [
        PERMISSION_CREATE_EDIT,
        PERMISSION_ACCEPT_EDIT,
        PERMISSION_REJECT_EDIT,
    ],
}
