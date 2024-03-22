def request_vote(client, token, content_type, reference, score):
    return client.put(
        f"/vote/{content_type}/{reference}",
        headers={"Auth": token},
        json={"score": score},
    )


def request_vote_status(client, token, content_type, reference):
    return client.get(
        f"/vote/{content_type}/{reference}", headers={"Auth": token}
    )
