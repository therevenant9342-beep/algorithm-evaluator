

import numpy as np

def identify_complexity(n_sizes: list, times: list) -> str:
    """
    n_sizes: List of input sizes (e.g., [10, 100, 1000])
    times: List of runtimes (e.g., [0.001, 0.01, 0.1])
    Returns: The string of the Big O notation (e.g., 'O(n^2)')
    """
    
    # Convert lists to numpy arrays for easier calculations
    n = np.array(n_sizes)
    t = np.array(times)
    
    # Prevent division by zero (if any size is zero)
    if np.any(n == 0):
        return "Unknown - n_sizes contains zero"
    
    # 1. Test for O(1) - Constant
    # If all times are approximately equal (constant)
    if np.std(t) / np.mean(t) < 0.1:  # Standard deviation less than 10% of mean
        return "O(1) - Constant"
    
    # 2. Test for O(n) - Linear
    # If t/n is approximately constant
    t_over_n = t / n
    if np.std(t_over_n) / np.mean(t_over_n) < 0.15:
        return "O(n) - Linear"
    
    # 3. Test for O(n log n) - Linearithmic
    # If t / (n * log(n)) is approximately constant
    n_log_n = n * np.log2(n)
    t_over_n_log_n = t / n_log_n
    if np.std(t_over_n_log_n) / np.mean(t_over_n_log_n) < 0.15:
        return "O(n log n) - Linearithmic"
    
    # 4. Test for O(n²) - Quadratic
    # If t/n² is approximately constant
    t_over_n_squared = t / (n ** 2)
    if np.std(t_over_n_squared) / np.mean(t_over_n_squared) < 0.15:
        return "O(n^2) - Quadratic"
    
    # 5. Test for O(n³) - Cubic
    t_over_n_cubed = t / (n ** 3)
    if np.std(t_over_n_cubed) / np.mean(t_over_n_cubed) < 0.15:
        return "O(n^3) - Cubic"
    
    # 6. Test for O(log n) - Logarithmic
    # If t / log(n) is approximately constant
    log_n = np.log2(n)
    # Avoid log(1) = 0 issue
    if np.any(log_n == 0):
        log_n = log_n + 0.001  # Small adjustment if log(1) exists
    t_over_log_n = t / log_n
    if np.std(t_over_log_n) / np.mean(t_over_log_n) < 0.15:
        return "O(log n) - Logarithmic"
    
    # 7. Test for O(2^n) - Exponential
    # If t / (2^n) is approximately constant (only for small n values)
    try:
        two_pow_n = 2 ** n
        # Skip if numbers become too large (infinity)
        if not np.any(np.isinf(two_pow_n)):
            t_over_2n = t / two_pow_n
            if np.std(t_over_2n) / np.mean(t_over_2n) < 0.15:
                return "O(2^n) - Exponential"
    except:
        pass  # Overflow occurred, skip this test
    
    # If no clear pattern was found
    return "Unknown - Complexity not recognized"

