def request_backup_images(client, token, page=1):
    return client.get(
        f"/backup/images?page={page}",
        headers={"Auth": token},
    )
