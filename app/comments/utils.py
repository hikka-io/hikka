from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.utils import path_to_uuid
from .schemas import CommentNode
from app.models import Comment

# Convert uuid reference to comment path
def uuid_to_path(obj_uuid):
    return str(obj_uuid).replace("-", "_")

def children_exists_query():
    Child = aliased(Comment)

    return (
        select(1)
        .select_from(Child)
        .where(
            Child.path.descendant_of(Comment.path),
            Child.deleted == False, # noqa: E712
            Child.hidden == False, # noqa: E712
            Child.id != Comment.id,
        )
        .correlate(Comment)
    )


def build_comments(base_comment, sub_comments):
    def calculate_total_replies(node):
        node.total_replies = len(node.replies)
        for reply in node.replies:
            calculate_total_replies(reply)

    tree = CommentNode.create(path_to_uuid(base_comment.path[-1]), base_comment)
    tree_dict = {tree.reference: tree}
    base_depth = base_comment.depth

    for sub_comment in sub_comments:
        path = [path_to_uuid(element) for element in sub_comment.path]
        tree_node = tree_dict[path[base_depth - 1]]

        for path_node in path[base_depth:]:
            reply = next(
                (
                    reply_node
                    for reply_node in tree_node.replies
                    if reply_node.reference == path_node
                ),
                None,
            )

            if not reply:
                reply = CommentNode.create(path_node)
                tree_node.replies.append(reply)
                tree_dict[path_node] = reply

            tree_node = reply

        tree_node.from_comment(sub_comment)

    tree.replies = [
        reply
        for reply in tree.replies
        if not (reply.hidden and not reply.replies)
    ]

    calculate_total_replies(tree)

    return tree
