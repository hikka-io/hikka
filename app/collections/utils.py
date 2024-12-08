def check_consecutive(numbers):
    return sorted(numbers) == list(range(min(numbers), max(numbers) + 1))
