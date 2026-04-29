"""
===========================================================================
Code Generator - Boilerplate & Template Utilities
===========================================================================
Provides starter templates that are inserted into the code editor,
and helper functions to parse/validate user-submitted code.
"""

# The default template shown when the app launches or the editor is reset.
DEFAULT_TEMPLATE = """\
def my_algorithm(arr):
    # Write your sorting or searching logic here.
    # 'arr' is a list of integers. Return the result.
    pass\
"""

# A library of named algorithm templates the user can load from the UI.
TEMPLATES: dict[str, str] = {
    "Blank": DEFAULT_TEMPLATE,
    "Bubble Sort — O(n²)": """\
def my_algorithm(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr\
""",
    "Linear Search — O(n)": """\
# EVAL_SIZES: 100, 500, 1000, 5000, 10000
def my_algorithm(arr):
    # Find the maximum value — always scans the ENTIRE array regardless
    # of input order, giving a clean O(n) signal across all three cases.
    # Target-based search was replaced because the target position varied
    # unpredictably across different array sizes, producing noisy curves.
    if not arr:
        return None
    maximum = arr[0]
    for val in arr:
        if val > maximum:
            maximum = val
    return maximum\
""",
    "Constant Access — O(1)": """\
def my_algorithm(arr):
    if not arr:
        return None
    return arr[0]\
""",
    "Merge Sort — O(n log n)": """\
# EVAL_SIZES: 100, 500, 1000, 5000, 10000
def my_algorithm(arr):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left  = my_algorithm(arr[:mid])
    right = my_algorithm(arr[mid:])

    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result\
""",
    "Triple Nested Loop — O(n³)": """\
# EVAL_SIZES: 5, 10, 20, 40, 60
# Safe upper bound: n=60 → 60³ = 216,000 ops (runs in milliseconds).
# Do NOT remove or raise EVAL_SIZES — n=1000 would freeze the UI.
def my_algorithm(arr):
    n = len(arr)
    total = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                total += arr[i] - arr[j] + arr[k]
    return total\
""",
    "Fibonacci Recursive — O(2^n)": """\
# EVAL_SIZES: 5, 8, 12, 16, 20
# Safe upper bound: fib(20) needs ~22K Python calls (~1-2 sec total).
# Do NOT remove or raise EVAL_SIZES — fib(1000) would hang indefinitely.
def my_algorithm(arr):
    def fib(num):
        if num <= 1:
            return num
        return fib(num - 1) + fib(num - 2)

    # Use array length as input to fib so the executor's size sweep
    # drives the input directly: size=5 → fib(5), size=20 → fib(20).
    n = len(arr)
    return fib(n)\
""",
}


def get_template(name: str) -> str:
    """
    Returns the code template string for the given name.
    Falls back to the blank template if the name is not found.
    """
    return TEMPLATES.get(name, DEFAULT_TEMPLATE)


def list_template_names() -> list[str]:
    """Returns all available template names for populating a dropdown menu."""
    return list(TEMPLATES.keys())


def validate_code(code_string: str) -> tuple[bool, str]:
    """
    Performs a lightweight static check on the user's code before execution.

    Returns:
        (True, "")           — code looks valid.
        (False, reason_str)  — code has a detectable problem.
    """
    if not code_string.strip():
        return False, "The editor is empty. Please enter an algorithm."

    if "my_algorithm" not in code_string:
        return (
            False,
            "No function named 'my_algorithm' found. The evaluator requires this exact name.",
        )

    # Attempt a compile-time syntax check without running anything.
    try:
        compile(code_string, "<editor>", "exec")
    except SyntaxError as exc:
        return False, f"Syntax error on line {exc.lineno}: {exc.msg}"

    return True, ""
