def request_notifications_count(client, token):
    return client.get("/notifications/count", headers={"Auth": token})


def request_notifications(client, token):
    return client.get("/notifications", headers={"Auth": token})


def request_notification_seen(client, notification_reference, token):
    return client.post(
        f"/notifications/{notification_reference}/seen",
        headers={"Auth": token},
    )
