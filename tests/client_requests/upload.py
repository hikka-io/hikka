def request_upload_avatar(client, token, file):
    return client.put(
        "/upload/avatar",
        headers={"Auth": token},
        files={"file": ("upload.jpg", file, "image/jpeg")},
    )
