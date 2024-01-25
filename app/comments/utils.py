from .schemas import CommentNode


# Convert uuid reference to comment path
def uuid_to_path(obj_uuid):
    return str(obj_uuid).replace("-", "_")


# Convert comment path to uuid reference
def path_to_uuid(obj_uuid):
    return str(obj_uuid).replace("_", "-")


def build_comments(root_node, sub_comments):
    tree = CommentNode(
        path_to_uuid(root_node.path), root_node.text, root_node.author
    )

    tree_dict = {tree.reference: tree}

    for sub_comment in sub_comments:
        path = [path_to_uuid(element) for element in sub_comment.path]
        tree_node = tree_dict[path[0]]

        for path_node in path[1:]:
            reply = next(
                (
                    reply_node
                    for reply_node in tree_node.replies
                    if reply_node.reference == path_node
                ),
                None,
            )

            if not reply:
                reply = CommentNode(path_node)
                tree_node.replies.append(reply)
                tree_node.total_replies += 1
                tree_dict[path_node] = reply

            tree_node = reply

        tree_node.author = sub_comment.author
        tree_node.text = sub_comment.text

    return tree


# I really hate this
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False
