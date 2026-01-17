from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from .schemas import CustomModel
from fastapi import Request
from pydantic import Field


class ErrorResponse(CustomModel):
    message: str = Field(examples=["Example error message"])
    code: str = Field(examples=["example_error"])


errors = {
    "admin": {
        "nothing-to-update": [
            "Nothing to update",
            "Нічого оновлювати",
            400,
        ],
        "user-not-found": [
            "User not found",
            "Користувач не знайдений",
            404,
        ],
    },
    "auth": {
        "activation-valid": [
            "Previous activation token still valid",
            "Попередній токен активації досі дійсний",
            400,
        ],
        "reset-valid": [
            "Previous password reset token still valid",
            "Попередній токен скидання паролю досі дійсний",
            400,
        ],
        "invalid-client-credentials": [
            "Invalid client credentials",
            "Недійсні облікові дані клієнта",
            400,
        ],
        "email-exists": [
            "User with that email already exists",
            "Користувач з такою поштою вже існує",
            400,
        ],
        "activation-expired": [
            "Activation token has expired",
            "Токен активації вже не дійсний",
            400,
        ],
        "token-request-expired": [
            "Token request has expired",
            "Запит на токен вже не дійсний",
            400,
        ],
        "activation-invalid": [
            "Activation token is invalid",
            "Поганий токен активації",
            400,
        ],
        "invalid-token-request": [
            "Invalid token request",
            "Поганий запит на токен",
            400,
        ],
        "not-token-owner": [
            "User is not token owner",
            "Користувач не власний токена",
            400,
        ],
        "oauth-code-required": [
            "OAuth code required",
            "Потрібен код OAuth",
            400,
        ],
        "invalid-provider": [
            "Invalid OAuth provider",
            "Поганий провайдер OAuth",
            400,
        ],
        "username-taken": [
            "Username already taken",
            "Хтось вже використовуй цей юзернейм",
            400,
        ],
        "reset-expired": [
            "Password reset token has expired",
            "Токен скидання паролю вже не дійсний",
            400,
        ],
        "reset-invalid": [
            "Password reset token is invalid",
            "Поганий токен скидання паролю",
            400,
        ],
        "already-activated": ["Already activated", "Вже активовано", 400],
        "invalid-token": [
            "Auth token is invalid",
            "Поганий токен автентифікації",
            400,
        ],
        "missing-token": [
            "Auth token is missing",
            "Немає токену автентифікації",
            400,
        ],
        "invalid-password": ["Invalid password", "Поганий пароль", 400],
        "client-not-found": ["Client not found", "Клієнт не знайдено", 404],
        "token-expired": ["Token has expired", "Токен вже не дійсний", 400],
        "invalid-code": ["Invalid OAuth code", "Поганий код OAuth", 400],
        "oauth-error": ["Error during OAuth", "Помилка під час OAuth", 400],
        "user-not-found": ["User not found", "Користувача не знайдено", 404],
        "invalid-scope": [
            "Invalid scope",
            "Поганий скоуп (я не знайшов відповідника, вибачте)",
            400,
        ],
        "not-available": [
            "Signup not available",
            "Реєстрація не доступна",
            400,
        ],
        "invalid-username": ["Invalid username", "Поганий юзернейм", 400],
        "scope-empty": ["Scope empty", "Пустий скоуп", 400],
    },
    "settings": {
        "username-cooldown": ["Username can be changed once per hour", "", 400],
        "email-cooldown": ["Email can be changed once per day", "", 400],
        "username-taken": ["Username already taken", "", 400],
        "invalid-username": ["Invalid username", "", 400],
    },
    "permission": {
        "denied": [
            "You don't have permission for this action",
            "У вас немає дозволу на цю дію",
            403,
        ],
    },
    "anime": {
        "no-franchise": [
            "This anime doesn't have franchise",
            "У цього аніме немає франшизи",
            400,
        ],
        "unknown-producer": ["Unknown producer", "Невідомий виробник", 400],
        "unknown-studio": ["Unknown studio", "Невідома студія", 400],
        "bad-year": ["Invalid years passed", "Задано погані роки", 400],
        "unknown-genre": ["Unknown genre", "Невідомий жанр", 400],
        "not-found": ["Anime not found", "Аніме не знайдено", 404],
    },
    "manga": {
        "unknown-magazine": ["Unknown magazine", "Невідомий журнал", 400],
        "unknown-genre": ["Unknown genre", "Невідомий жанр", 400],
        "not-found": ["Manga not found", "Манґа не знайдена", 404],
    },
    "novel": {
        "unknown-magazine": ["Unknown magazine", "Невідомий журнал", 400],
        "unknown-genre": ["Unknown genre", "Невідомий жанр", 400],
        "not-found": ["Novel not found", "Ранобе не знайдено", 404],
    },
    "edit": {
        "rate-limit": [
            "You have reached the edit rate limit, try later",
            "Ви досягли ліміту на правки (ого!), спробуйте пізніше",
            429,
        ],
        "missing-content-type": [
            "You must specify content type",
            "Вам треба вказати тип коненту",
            400,
        ],
        "not-pending": [
            "Only pending edit can be changed",
            "Можна підтвердити тільки правку, що на розгляді",
            400,
        ],
        "moderator-not-found": [
            "Moderator not found",
            "Модератора не знайдено",
            404,
        ],
        "not-author": [
            "Only author can modify edit",
            "Тільки автор може редагувати цю цю правку",
            400,
        ],
        "invalid-content-id": [
            "Invalid content id",
            "Поганий ідентифікатор контенту",
            400,
        ],
        "content-not-found": ["Content not found", "Контент не знайдено", 404],
        "author-not-found": ["Author not found", "Автора не знайдено", 404],
        "bad-edit": ["This edit is invalid", "Ця правка погана", 400],
        "invalid-field": ["Invalid field", "Погане поле", 400],
        "not-found": ["Edit not found", "Правка не знайдена", 404],
        "empty-edit": ["Empty edit", "Пуста правка", 400],
    },
    "comment": {
        "rate-limit": [
            "You have reached comment rate limit, try later",
            "Ви досялги ліміту на коментарі, спробуйте пізніше",
            429,
        ],
        "not-editable": [
            "This comment can't be edited anymore",
            "Цей коментар більше не відрегадуєш",
            400,
        ],
        "parent-not-found": [
            "Parent comment not found",
            "Батьківський коментар не знайдено",
            404,
        ],
        "already-hidden": [
            "Comment is already hidden",
            "Цей коментар вже сховано",
            400,
        ],
        "not-owner": [
            "You can't edit this comment",
            "Ви не можете редагувати цей коментар",
            400,
        ],
        "content-not-found": ["Content not found", "Контент не знайдено", 404],
        "max-depth": [
            "Max reply depth reached",
            "Досягнуто (дна) максимальної глибини відповід",
            400,
        ],
        "empty-markdown": ["Empty markdown", "Пуста розмітка", 400],
        "not-found": ["Comment not found", "Коментар не знайдено", 404],
        "hidden": ["Comment is hidden", "Коментар приховано", 400],
    },
    "studio": {
        "not-found": ["Studio not found", "Не вдалось знайти цю студію", 404],
    },
    "genre": {
        "not-found": ["Genre not found", "Жанр не знайдено", 404],
    },
    "watch": {
        "bad-episodes": [
            "Bad episodes number provided",
            "Ви вказали поганий номер епізоду",
            400,
        ],
        "empty-random": [
            "User watch list is empty",
            "Список перегляду користувача пустий :(",
            400,
        ],
        "not-found": [
            "Watch record not found",
            "Запис перегляду не знайдено",
            404,
        ],
    },
    "read": {
        "bad-chapters": [
            "Bad chapters number provided",
            "Ви вказали поганий номер розділу",
            400,
        ],
        "bad-volumes": [
            "Bad volumes number provided",
            "Ви вказали поганий номер тому",
            400,
        ],
        "empty-random": [
            "User read list is empty",
            "Список читання користувача пустий",
            400,
        ],
        "content-not-found": ["Content not found", "Контент не знайдено", 404],
        "not-found": [
            "Read record not found",
            "Запис читання не знайдено",
            404,
        ],
    },
    "favourite": {
        "exists": [
            "Favourite record already exists",
            "Ми знаємо, що вам подобається, ви вже казали",
            400,
        ],
        "not-found": ["Favourite record not found", "Немає в улюбленому", 404],
        "content-not-found": ["Content not found", "Контент не знайдено", 404],
    },
    "captcha": {
        "invalid": ["Failed to validate captcha", "А ти точно людина?", 401],
    },
    "user": {
        "not-found": ["User not found", "Користувача не знайдено", 404],
        "deleted": ["Deleted", "Видалено...", 400],
    },
    "follow": {
        "already-following": [
            "This user is already followed",
            "Ви вже стежите за цим користувачем (сталкер)",
            400,
        ],
        "not-following": [
            "This user is not followed",
            "Ви (поки) не стежите за цим користувачем",
            400,
        ],
        "invalid-action": ["Invalid action", "Погана дія", 401],
        "self": [
            "Can't follow self",
            "Ех, на самого себе не підпишешся, а дуже хотілось...",
            400,
        ],
    },
    "search": {
        "query-down": [
            "Search by query unavailable at the moment",
            "Пошук помер, намагаємось оживити його...",
            400,
        ],
    },
    "company": {
        "not-found": ["Company not found", "Компанію не знайдено", 404],
    },
    "character": {
        "not-found": ["Character not found", "Персонажа не знайдено", 404],
    },
    "person": {
        "not-found": ["Person not found", "Людину не знайдено", 404],
    },
    "upload": {
        "rate-limit": [
            "You have reached upload rate limit, try later",
            "Ви досягли ліміту на завантаження (сервер не резиновий), спробуйте пізніше",
            429,
        ],
        "not-square": [
            "Image should be square",
            "Зображення має бути квадратним",
            400,
        ],
        "bad-resolution": ["Bad resolution", "Погана роздільна якість", 400],
        "bad-mime": ["Don't be bad mime", "Не будьте поганим мімом", 400],
        "bad-size": ["Bad file size", "Поганий розмір файлу", 400],
        "missconfigured-permission": [
            "If you see this, check upload permissions in rate limit",
            "Якщо ви бачите це, треба перевірити дозволи на завантаження в рейт лімітах",
            400,
        ],
    },
    "notification": {
        "not-found": ["Notification not found", "Сповіщення не знайдено", 404],
        "seen": [
            "Notification already seen",
            "Ви вже бачили це сповіщення",
            400,
        ],
    },
    "collections": {
        "bad-content-type": [
            "You can't change collection content type",
            "Тип контент в колекції змінити не можна",
            400,
        ],
        "bad-order-not-consecutive": [
            "Order must be consecutive",
            "Порядок має бути послідовним",
            400,
        ],
        "bad-order-duplicated": [
            "You can't set duplicated order",
            "У порядку не може бути повторень",
            400,
        ],
        "empty-content-type": [
            "Content type is not specified",
            "Тип контенту не вказано",
            400,
        ],
        "content-limit": [
            "Collection content limit violation",
            "Досягнуто обмеження на кількість контенту",
            400,
        ],
        "limit": [
            "You have reached collections limit",
            "Ви досягли ліміту на кількість колекцій, як це взагалі трапилось?!",
            400,
        ],
        "bad-order-start": [
            "Order must start from 1",
            "Порядок має починатись з 1",
            400,
        ],
        "unlabled-content": ["Unlabeled content", "Негрупований контент", 400],
        "bad-labels-order": ["Bad labels order", "Поганий порядок груп", 400],
        "author-not-found": ["Author not found", "Автора не знайдено", 404],
        "not-found": ["Collection not found", "Колекцію не знайдено", 404],
        "bad-label": ["Unknown label", "Невідома група", 400],
        "bad-content": ["Bad content", "Поганий контент", 400],
        "moderator-content-update": [
            "Moderator can't update content in collection",
            "Тільки автор колекції можне змінювати контент всередині",
            400,
        ],
    },
    "vote": {
        "content-not-found": ["Content not found", "Контент не знайдено", 404],
        "not-found": ["Vote record not found", "Вашу оцінку не знайдено", 404],
    },
    "schedule": {
        "incompatible-filters": [
            "You've specified incompatible filters",
            "Ви вказали несумісні фільтри",
            400,
        ],
        "watch-no-user": [
            "You can't use only_watch without user",
            "Не можна використовувати only_watch без користувача",
            400,
        ],
    },
    "related": {
        "no-franchise": [
            "Content doesn't have franchise",
            "У цього тайтлу немає франшизи",
            400,
        ],
        "content-not-found": ["Content not found", "Контент не знайдено", 404],
    },
    "system": {
        "rate-limit": [
            "You have reached the rate limit, try later",
            "Ви досягли межі, спробуйте пізніше",
            429,
        ],
        "bad-backup-token": [
            "Bad backup token",
            "Не дійсний токен для бекапу",
            401,
        ],
    },
    "moderation-log": {
        "no-access": ["You do not have permission to access", 400],
    },
    "client": {
        "already-verified": [
            "Client is already verified",
            "Клієнт вже верифіковано",
            400,
        ],
        "not-owner": [
            "User not owner of the client",
            "Користувач не є власником клієнта",
            400,
        ],
        "max-clients": [
            "Maximum clients reached",
            "Досягнуто максимальної кількості клієнтів",
            400,
        ],
        "not-found": ["Client not found", "Клієнт не знайдено", 404],
    },
    "articles": {
        "bad-draft": [
            "You can't set published article to draft",
            "Ви не можете перемістити опубліковану статтю до чернеток",
            400,
        ],
        "not-trusted": [
            "You can't make this article trusted",
            "Ви не можете помітит цю статтю як довірену",
            403,
        ],
        "bad-category": [
            "You can't use this category",
            "Ви не можете використовувати цю категорію",
            400,
        ],
        "duplicate-image-url": [
            "Duplicate image url",
            "Дублікат посилання на зображення",
            400,
        ],
        "used-image": [
            "This image already been used",
            "Це зображення вже було використано деінде",
            400,
        ],
        "author-not-found": ["Author not found", "Автора не знайдено", 404],
        "bad-image-url": [
            "Bad image url",
            "Погане посилання на зображення",
            400,
        ],
        "not-found": ["Article not found", "Статтю не знайдено", 404],
    },
    "content": {
        "not-found": ["Content not found", "Контент не знайдено", 404],
    },
    "artifacts": {
        "not-found": ["Artifact not found", "Артефакт не знайдено", 404],
    },
}


class Abort(Exception):
    def __init__(self, scope: str, message: str):
        self.scope = scope
        self.message = message


def build_error_code(scope: str, message: str):
    return scope.replace("-", "_") + ":" + message.replace("-", "_")


async def abort_handler(request: Request, exception: Abort):
    error_code = build_error_code(exception.scope, exception.message)

    try:
        error_message_en = errors[exception.scope][exception.message][0]
        error_message = errors[exception.scope][exception.message][1]
        status_code = errors[exception.scope][exception.message][2]
    except Exception:
        error_message_en = "Unknown error"
        error_message = "Невідома помилка"
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={
            "message_en": error_message_en,
            "message": error_message,
            "code": error_code,
        },
    )


async def validation_handler(
    request: Request, exception: RequestValidationError
):
    print(exception.errors())
    error = exception.errors()[0]

    field_location = error["loc"][0]
    error_message = f"in request {field_location}"

    if len(error["loc"]) > 1:
        field_name = error["loc"][1]
        error_message = f"{field_name} {error_message}"

    error_message = f"Invalid field {error_message}"

    return JSONResponse(
        status_code=400,
        content={
            "code": "system:validation_error",
            "message": error_message.capitalize(),
        },
    )
