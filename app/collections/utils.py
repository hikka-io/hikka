def check_consecutive(numbers: list[int]) -> bool:
    return sorted(numbers) == list(range(min(numbers), max(numbers) + 1))
