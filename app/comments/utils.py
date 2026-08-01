from app.common.schemas.comments import CommentNode
from app.utils import path_to_uuid


# Convert uuid reference to comment path
def uuid_to_path(obj_uuid):
    return str(obj_uuid).replace("-", "_")


def build_comments(base_comment, sub_comments):
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

    return tree
