def request_upload(client, upload_type, token, file):
    return client.put(
        f"/upload/{upload_type}",
        headers={"Auth": token},
        files={"file": ("upload.jpg", file, "image/jpeg")},
    )
