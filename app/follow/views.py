# from .responses import UserResponse, WatchPaginationResponse
# from .responses import UserPaginationResponse
# from .args import WatchArgs, DescriptionArgs
# from .responses import FollowStatsResponse
# from .responses import WatchStatsResponse
from fastapi import APIRouter, Depends
from ..decorators import auth_required
from ..models import User, AnimeGenre
from ..args import PaginationArgs
from ..errors import Abort
from .. import constants
from .. import display
from .. import utils

router = APIRouter(prefix="/follow")

@router.put("/{username}", summary="Follow user",
    response_model=UserResponse
)
async def follow_user(
    username: str, user: User = Depends(auth_required())
):
    if not (follow_user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    await user.following.add(follow_user)

    return display.user(follow_user)

@router.delete("/{username}", summary="Unfollow user",
    response_model=UserResponse
)
async def follow_user(
    username: str,
    user: User = Depends(auth_required())
):
    if not (follow_user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    await user.following.remove(follow_user)

    return display.user(follow_user)

@router.get("/{username}/following", summary="Get user following list",
    response_model=UserPaginationResponse
)
async def user_following(
    username: str,
    args: PaginationArgs = Depends()
):
    if not (user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    # Pagination
    total = await user.following.filter().count()
    limit, offset, size = utils.pagination(args.page)
    pagination = utils.pagination_dict(total, args.page, size)

    following = await user.following.filter().limit(limit).offset(offset)

    result = []

    for follow_user in following:
        result.append(display.user(follow_user))

    return {
        "pagination": pagination,
        "list": result
    }

@router.get("/{username}/followers", summary="Get user followers",
    response_model=UserPaginationResponse
)
async def user_following(
    username: str,
    args: PaginationArgs = Depends()
):
    if not (user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    # Pagination
    total = await user.followers.filter().count()
    limit, offset, size = utils.pagination(args.page)
    pagination = utils.pagination_dict(total, args.page, size)

    followers = await user.followers.filter().limit(limit).offset(offset)

    result = []

    for follow_user in followers:
        result.append(display.user(follow_user))

    return {
        "pagination": pagination,
        "list": result
    }

@router.get("/{username}/stats", summary="Get user follow stats",
    response_model=FollowStatsResponse
)
async def user_follow_stats(
    username: str
):
    if not (user := await User.filter(username=username).first()):
        raise Abort("user", "not-found")

    followers = await user.followers.filter().count()
    following = await user.following.filter().count()

    return {
        "followers": followers,
        "following": following
    }
