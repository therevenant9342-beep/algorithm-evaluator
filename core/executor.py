import time
import sys
import io

def run_user_code(code_string: str, input_array: list) -> dict:
    """
    Inputs: The code from the UI (string) and the array to test (list).
    Output: A dictionary containing the result and the time taken.
    """
    # Create a local scope for the function
    local_env = {}
    
    # We use a StringIO to catch anything the user might 'print'
    output_capture = io.StringIO()
    sys.stdout = output_capture
    
    try:
        # Step 1: Start the clock (nanoseconds for high precision) 
        start_time = time.perf_counter_ns()
        
        # Step 2: Execute the user's code
        exec(code_string, {}, local_env)
        
        # Step 3: Run the specific function (assuming the user named it 'my_algorithm')
        # We find the function in the local environment
        func = local_env.get('my_algorithm')
        result = func(input_array.copy())
        
        end_time = time.perf_counter_ns()
        
        return {
            "success": True,
            "runtime": end_time - start_time,
            "output": result
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        sys.stdout = sys.__stdout__ # Reset terminal output