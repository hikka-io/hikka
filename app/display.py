# ToDo: get rid of that


def user(user):
    return {
        "last_active": user.last_active,
        "description": user.description,
        "reference": user.reference,
        "username": user.username,
        "created": user.created,
    }


def token(token):
    return {
        "secret": token.secret,
        "reference": token.reference,
        "expiration": token.expiration,
        "created": token.created,
    }


def watch(watch):
    return {
        "user_score": watch.user_score,
        "reference": watch.reference,
        "episodes": watch.episodes,
        "created": watch.created,
        "updated": watch.updated,
        "status": watch.status,
        "note": watch.note,
    }
