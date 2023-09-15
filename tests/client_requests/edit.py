def request_edit(client, edit_id):
    return client.get(f"/edit/{edit_id}")
