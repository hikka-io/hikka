from sqlalchemy.orm import Session
from sqlalchemy import event


transient_store = {}


@event.listens_for(Session, "before_commit")
def store_query_expression(session):
    # Before commit we persist values loaded via query_expression
    for instance in session.identity_map.values():
        if hasattr(instance, "my_score"):
            transient_store[id(instance)] = instance.my_score


@event.listens_for(Session, "after_commit")
def after_commit_handler(session):
    # And after commit we populate it back
    for instance in session.identity_map.values():
        if hasattr(instance, "my_score"):
            instance.my_score = transient_store.pop(id(instance), None)
