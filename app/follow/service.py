from app.models import User


async def get_follow_stats(user: User):
    return {
        "followers": await user.followers.filter().count(),
        "following": await user.following.filter().count(),
    }


async def is_following(follow_user: User, user: User):
    return await user.following.filter(id=follow_user.id).first() != None


async def follow(follow_user: User, user: User):
    await user.following.add(follow_user)
    return True


async def unfollow(follow_user: User, user: User):
    await user.following.remove(follow_user)
    return False
