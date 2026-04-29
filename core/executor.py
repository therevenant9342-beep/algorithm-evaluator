import time
import sys
import io
import re
import random
import gc

# Number of execution iterations used to determine the minimum runtime for benchmarking.
_REPEATS = 61


def _compile_code(code_string: str) -> dict:
    """
    Compiles the provided code string into a callable function named 'my_algorithm'.
    Returns a dictionary containing the success status and the callable or error message.
    """
    # Shared environment dictionary to support recursive function calls.
    shared_env = {}
    try:
        exec(compile(code_string, "<editor>", "exec"), shared_env, shared_env)
        fn = shared_env.get("my_algorithm")
        if fn is None:
            raise ValueError("No function named 'my_algorithm' found.")
        return {"success": True, "fn": fn}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def _execute_single_run(fn: callable, input_array: list) -> dict:
    """
    Executes the compiled function multiple times and returns the minimum execution 
    time in nanoseconds, along with the function result and captured standard output.
    """
    output_capture = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_capture

    # Disable garbage collection during profiling for consistent timing.
    gc.disable()

    try:
        samples = []
        last_result = None

        for _ in range(_REPEATS):
            arr_copy = input_array.copy()
            t0 = time.perf_counter_ns()
            last_result = fn(arr_copy)
            t1 = time.perf_counter_ns()
            samples.append(t1 - t0)

        return {
            "success": True,
            "runtime_ns": min(samples),
            "output": last_result,
            "console_output": output_capture.getvalue(),
        }
    except Exception as exc:
        return {"success": False, "error": str(exc)}
    finally:
        sys.stdout = original_stdout
        gc.enable()


def _parse_custom_sizes(code_string: str) -> list | None:
    """
    Extracts custom evaluation sizes from an '# EVAL_SIZES: ...' comment directive.
    Returns a list of integers, or None if the directive is not found or invalid.
    """
    match = re.search(r"#\s*EVAL_SIZES\s*:\s*([\d,\s]+)", code_string)
    if not match:
        return None
    try:
        return [int(x.strip()) for x in match.group(1).split(",") if x.strip()]
    except ValueError:
        return None


def run_evaluation(code_string: str, mode: str, manual_input: list = None) -> dict:
    """
    Orchestrates the execution and benchmarking of the provided code based on 
    the specified mode ('Manual' or 'Auto').
    """
    compiled = _compile_code(code_string)
    if not compiled["success"]:
        return {"type": "error", "message": compiled["error"]}
    fn = compiled["fn"]

    if mode == "Manual":
        test_array = manual_input if manual_input else [10, 2, 8, 1, 5, 9]
        result = _execute_single_run(fn, test_array)

        if not result["success"]:
            return {"type": "error", "message": result["error"]}

        return {"type": "manual", "results": result}

    elif mode == "Auto":
        input_sizes = _parse_custom_sizes(code_string) or [10, 50, 100, 500, 1000]

        # Initialize benchmarking metrics
        evaluation_metrics = {
            "sizes": input_sizes,
            "random_times": [],  
            "sorted_times": [],  
            "reversed_times": [], 
        }

        for size in input_sizes:
            # Deterministic seed ensures reproducible test arrays across runs
            rng = random.Random(42 + size)
            random_array = [rng.randint(0, 10000) for _ in range(size)]
            sorted_array = sorted(random_array)
            reversed_array = sorted_array[::-1]

            rand_res = _execute_single_run(fn, random_array)
            sort_res = _execute_single_run(fn, sorted_array)
            rev_res = _execute_single_run(fn, reversed_array)

            if not rand_res["success"]:
                return {
                    "type": "error",
                    "message": f"Average-case run failed: {rand_res['error']}",
                }
            if not sort_res["success"]:
                return {
                    "type": "error",
                    "message": f"Best-case run failed: {sort_res['error']}",
                }
            if not rev_res["success"]:
                return {
                    "type": "error",
                    "message": f"Worst-case run failed: {rev_res['error']}",
                }

            evaluation_metrics["random_times"].append(rand_res["runtime_ns"])
            evaluation_metrics["sorted_times"].append(sort_res["runtime_ns"])
            evaluation_metrics["reversed_times"].append(rev_res["runtime_ns"])

        return {"type": "auto", "metrics": evaluation_metrics}