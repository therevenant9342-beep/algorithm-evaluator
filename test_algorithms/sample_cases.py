"""
QA test cases for evaluating algorithmic time complexity.
Contains reference implementations for standard Big-O complexity classes.
"""


def test_constant(arr: list):
    """Demonstrates O(1) time complexity."""
    if not arr:
        return None

    result = arr[0] + len(arr)
    return result


def test_linear(arr: list):
    """Demonstrates O(n) time complexity by finding the maximum value."""
    if not arr:
        return None

    max_val = arr[0]
    for num in arr:
        if num > max_val:
            max_val = num

    return max_val


def test_linearithmic(arr: list):
    """Demonstrates O(n log n) time complexity using Timsort."""
    arr.sort()
    return arr


def test_quadratic(arr: list):
    """Demonstrates O(n^2) time complexity using bubble sort."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def test_cubic(arr: list):
    """Demonstrates O(n^3) time complexity."""
    n = len(arr)
    total = 0

    # Cap iteration at 75 to prevent execution timeouts on large arrays
    limit = min(n, 75)

    for i in range(limit):
        for j in range(limit):
            for k in range(limit):
                total += 1

    return total


def test_exponential(arr: list):
    """Demonstrates O(2^n) time complexity using a recursive Fibonacci sequence."""

    def naive_fibonacci(num):
        if num <= 1:
            return num
        return naive_fibonacci(num - 1) + naive_fibonacci(num - 2)

    # Cap input at 20 to prevent execution timeouts on large arrays
    n = min(len(arr), 20)

    return naive_fibonacci(n)

