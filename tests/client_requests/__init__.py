from .auth import request_activation_resend
from .auth import request_password_confirm
from .auth import request_password_reset
from .auth import request_activation
from .auth import request_signup
from .auth import request_login

from .oauth import request_oauth_post
from .oauth import request_oauth_url

from .user import request_profile
from .user import request_me

from .follow import request_follow_stats
from .follow import request_follow_check
from .follow import request_followers
from .follow import request_following
from .follow import request_unfollow
from .follow import request_follow

from .anime import request_anime_recommendations
from .anime import request_anime_characters
from .anime import request_anime_franchise
from .anime import request_anime_episodes
from .anime import request_anime_search
from .anime import request_anime_genres
from .anime import request_anime_staff
from .anime import request_anime_info

from .manga import request_manga_search
from .manga import request_manga_info

from .novel import request_novel_search
from .novel import request_novel_info

from .characters import request_characters_search
from .characters import request_characters_anime
from .characters import request_characters_info

from .companies import request_companies_search
from .companies import request_companies_anime
from .companies import request_companies_info

from .people import request_people_search
from .people import request_people_anime
from .people import request_people_info

from .favourite import request_favourite_delete
from .favourite import request_favourite_list
from .favourite import request_favourite_add
from .favourite import request_favourite

from .watch import request_watch_random
from .watch import request_watch_delete
from .watch import request_watch_stats
from .watch import request_watch_list
from .watch import request_watch_add
from .watch import request_watch

from .read import request_read_random
from .read import request_read_delete
from .read import request_read_stats
from .read import request_read_list
from .read import request_read_add
from .read import request_read

from .edit import request_accept_edit
from .edit import request_create_edit
from .edit import request_update_edit
from .edit import request_close_edit
from .edit import request_deny_edit
from .edit import request_edit_list
from .edit import request_edit

from .comments import request_comments_latest
from .comments import request_comments_write
from .comments import request_comments_list
from .comments import request_comments_edit
from .comments import request_comments_hide

from .settings import request_settings_delete_watch
from .settings import request_settings_delete_image
from .settings import request_settings_import_watch
from .settings import request_settings_description
from .settings import request_settings_username
from .settings import request_settings_password
from .settings import request_settings_email

from .collections import request_create_collection
from .collections import request_update_collection
from .collections import request_delete_collection
from .collections import request_collection_info
from .collections import request_collections

from .notifications import request_notifications_count
from .notifications import request_notification_seen
from .notifications import request_notifications

from .vote import request_vote_status
from .vote import request_vote

from .upload import request_upload

__all__ = [
    "request_activation_resend",
    "request_password_confirm",
    "request_password_reset",
    "request_activation",
    "request_signup",
    "request_login",
    "request_oauth_post",
    "request_oauth_url",
    "request_profile",
    "request_me",
    "request_follow_stats",
    "request_follow_check",
    "request_followers",
    "request_following",
    "request_unfollow",
    "request_follow",
    "request_anime_recommendations",
    "request_anime_characters",
    "request_anime_franchise",
    "request_anime_episodes",
    "request_anime_search",
    "request_anime_genres",
    "request_anime_staff",
    "request_anime_info",
    "request_manga_search",
    "request_manga_info",
    "request_novel_search",
    "request_novel_info",
    "request_characters_search",
    "request_characters_anime",
    "request_characters_info",
    "request_companies_search",
    "request_companies_anime",
    "request_companies_info",
    "request_people_search",
    "request_people_anime",
    "request_people_info",
    "request_favourite_delete",
    "request_favourite_list",
    "request_favourite_add",
    "request_favourite",
    "request_watch_random",
    "request_watch_delete",
    "request_watch_stats",
    "request_watch_list",
    "request_watch_add",
    "request_watch",
    "request_read_random",
    "request_read_delete",
    "request_read_stats",
    "request_read_list",
    "request_read_add",
    "request_read",
    "request_accept_edit",
    "request_create_edit",
    "request_update_edit",
    "request_close_edit",
    "request_deny_edit",
    "request_edit_list",
    "request_edit",
    "request_comments_latest",
    "request_comments_write",
    "request_comments_list",
    "request_comments_edit",
    "request_comments_hide",
    "request_settings_delete_watch",
    "request_settings_delete_image",
    "request_settings_import_watch",
    "request_settings_description",
    "request_settings_username",
    "request_settings_password",
    "request_settings_email",
    "request_create_collection",
    "request_update_collection",
    "request_delete_collection",
    "request_collection_info",
    "request_collections",
    "request_notifications_count",
    "request_notification_seen",
    "request_notifications",
    "request_vote_status",
    "request_vote",
    "request_upload",
]
