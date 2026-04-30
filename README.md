---

## Algorithm Performance Evaluator

The Algorithm Performance Evaluator is a graphical desktop application designed to benchmark and automatically estimate the Big-O time complexity of user-provided Python code.

### 🌟 Key Features

- **Integrated Code Editor**: Features a custom line-numbered text editor with regex-based syntax highlighting for Python keywords, functions, built-ins, and strings.
- **Built-in Algorithm Templates**: Quickly load starter templates for common algorithms, including Bubble Sort, Merge Sort, Linear Search, and Recursive Fibonacci.
- **Comprehensive Benchmarking**: Automatically executes code across average-case (random arrays), best-case (sorted arrays), and worst-case (reversed arrays) scenarios to provide a complete performance profile.
- **Advanced Complexity Detection**: Estimates Big-O time complexity by evaluating empirical execution times against input sizes using a blend of R-squared statistical fits and theoretical tail-ratio voting.
- **Interactive Visualizations**: Generates dynamic performance graphs using `matplotlib`, utilizing PCHIP interpolation in log-log space to accurately plot and smooth non-linear asymptotic growth.
- **High-DPI Support**: Automatically configures UI scaling on Windows environments to prevent blurry rendering.

### 📊 Supported Complexity Classes

The statistical analyzer is trained to identify and categorize the following time complexities:

- **O(1)**: Constant — independent of input size.
- **O(n)**: Linear — scales directly with input.
- **O(n log n)**: Linearithmic — efficient divide & conquer.
- **O(n²)**: Quadratic — nested loop pattern detected.
- **O(n³)**: Cubic — triple nested loops detected.
- **O(2^n)**: Exponential — combinatorial blowup.

### 🛠️ Usage Directives

To properly benchmark your code, ensure it adheres to the following executor requirements:

- **Target Function**: The code evaluator specifically targets a callable function named `my_algorithm`. If this function is missing, the static validation will fail.
- **Custom Evaluation Sizes**: You can override the default array benchmarking sizes (10, 50, 100, 500, 1000) by adding a specific comment directive in your code: `# EVAL_SIZES: 100, 500, 1000, 5000`.
- **Execution Modes**: The app supports both an "Auto" mode for full complexity benchmarking and a "Manual" mode that allows you to test the algorithm against a single, user-defined input array.

### 🏗️ Architecture Overview

The application is structured into the following core modules:

- **`ui/main_window.py`**: The primary `customtkinter` interface managing the layout, thread execution, and results dashboard.
- **`core/executor.py`**: Handles safe compilation of user code, disables garbage collection for consistent profiling, and orchestrates the automated execution sweeps.
- **`core/analyzer.py`**: The mathematical engine that applies domain constraints and heuristic tiebreakers to determine the closest theoretical complexity match.
- **`ui/plotter.py`**: Translates the benchmark metrics into styled graphs with filled regions indicating best, average, and worst execution times.
