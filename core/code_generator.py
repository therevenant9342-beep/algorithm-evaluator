import random

def generate_test_arrays(size: int) -> dict:
    """
    Inputs: The size of the array 'n' (e.g., 1000).
    Outputs: A dictionary containing three types of arrays for testing.
    This helps the system evaluate Best, Average, and Worst cases.
    """
    
    # 1. Average Case: Completely random numbers
    random_array = [random.randint(0, 10000) for _ in range(size)]
    
    # 2. Best/Worst Case (Depends on algorithm): Already sorted
    sorted_array = list(range(size))
    
    # 3. Best/Worst Case (Depends on algorithm): Reverse sorted
    reversed_array = list(range(size, 0, -1))
    
    return {
        "random": random_array,
        "sorted": sorted_array,
        "reversed": reversed_array
    }