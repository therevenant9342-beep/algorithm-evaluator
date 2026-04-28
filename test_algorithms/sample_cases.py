"""
This module contains the mandatory test algorithms for the documentation report.
Each function must accept an array 'arr' to match the GUI editor's format.
"""

def test_constant(arr: list):
    # O(1) Constant
    if len(arr) == 0:
        return None
    return arr[0]


def test_linear(arr: list):
    # O(n) Linear
    total = 0
    for element in arr:
        total += element
    return total


def test_linearithmic(arr: list):
    # O(n log n) Linearithmic — Merge Sort
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = test_linearithmic(arr[:mid])
    right = test_linearithmic(arr[mid:])

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def test_quadratic(arr: list):
    # O(n^2) Quadratic — Bubble Sort
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def test_cubic(arr: list):
    # O(n^3) Cubic — Triple nested loop (counts triplet combinations)
    n = len(arr)
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                if arr[i] + arr[j] + arr[k] == 0:
                    count += 1
    return count


def test_exponential(arr: list):
    # O(2^n) Exponential — Naïve recursive Fibonacci (uses n = len(arr))
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)

    return fib(len(arr))
