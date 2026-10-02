from .schemas import CollectionsListArgs


def check_consecutive(numbers: list[int]) -> bool:
    return sorted(numbers) == list(range(min(numbers), max(numbers) + 1))


def build_collection_filters(args: CollectionsListArgs):
    content_type = (
        [f"content_type = {args.content_type}"] if args.content_type else []
    )

    # Tags are AND-ed, same as Collection.tags.any in collections_list_filter
    tags = [f"tags = '{tag}'" for tag in args.tags]

    return [*content_type, *tags]
