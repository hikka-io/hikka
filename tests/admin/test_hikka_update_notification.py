from app.admin import service


async def test_hikka_update_notification(
    test_session, create_test_user, create_dummy_user
):
    update_name = "hikka_update_1"

    # First we create system update notification
    await service.create_hikka_update_notification(
        test_session,
        update_name,
        "Update description",
        "Update title",
        "https://example.com",
    )

    # Now we check notifications for this update
    notifications_count = await service.count_hikka_update_notifications(
        test_session, update_name
    )

    # Should be 2
    assert notifications_count == 2

    # Now let's imagine we made a mistake and created it again
    await service.create_hikka_update_notification(
        test_session,
        update_name,
        "Update description",
        "Update title",
        "https://example.com",
    )

    # Now let's check notifications count again
    notifications_count = await service.count_hikka_update_notifications(
        test_session, update_name
    )

    # Still should be 2
    assert notifications_count == 2

    # Now let's imagine something horrible has happened
    # and we need to delete notification
    await service.delete_hikka_update_notification(test_session, update_name)

    # Now let's check notifications count again
    notifications_count = await service.count_hikka_update_notifications(
        test_session, update_name
    )

    # There should be no notifications
    assert notifications_count == 0
