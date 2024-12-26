from client_requests import request_create_article

# from client_requests import request_upload
from fastapi import status


async def test_articles_create_cover_bad_url(
    client,
    create_test_user,
    get_test_token,
    test_session,
):
    attachment_url = "https://cdn.hikka.io/uploads/baduser/attachment/bad.jpg"

    response = await request_create_article(
        client,
        get_test_token,
        {
            "cover": attachment_url,
            "text": "Lorem ipsum dor sit amet.",
            "title": "Interesting title",
            "tags": ["interesting", "tag"],
            "category": "news",
            "content": None,
            "draft": False,
            "trusted": False,
        },
    )

    # Make sure we got correct response code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["code"] == "articles:cover_not_found"
