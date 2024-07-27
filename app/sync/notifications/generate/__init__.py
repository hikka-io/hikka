from .thirdparty_login import generate_thirdparty_login
from .collection_vote import generate_collection_vote
from .anime_schedule import generate_anime_schedule
from .comment_write import generate_comment_write
from .comment_vote import generate_comment_vote
from .edit_update import generate_edit_update
from .edit_accept import generate_edit_accept
from .edit_deny import generate_edit_deny
from .follow import generate_follow

__all__ = [
    "generate_thirdparty_login",
    "generate_collection_vote",
    "generate_anime_schedule",
    "generate_comment_write",
    "generate_comment_vote",
    "generate_edit_update",
    "generate_edit_accept",
    "generate_edit_deny",
    "generate_follow",
]
