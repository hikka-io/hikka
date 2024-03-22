def request_vote(client, token, content_type, reference, score):
    return client.put(
        f"/vote/{content_type}/{reference}",
        headers={"Auth": token},
        json={"score": score},
    )
