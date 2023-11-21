def request_settings_description(client, token, description):
    return client.post(
        "/settings/description",
        headers={"Auth": token},
        json={"description": description},
    )
