import logging
from io import StringIO
from chat_helpers import get_chat_response, test_openai_connection, map_env_variables
from utils import extract_python_code, extract_json_object
import sys
import os
import textwrap
import subprocess
import pkgutil
import importlib.util
import traceback

# Code snippet to be prepended to generated Python code
env_loading_code = """
import requests
from pathlib import Path
from dotenv import load_dotenv

# Define the path to the environment file
env_file_path = Path("oneConnection.env")

# Load environment variables from the specific file
load_dotenv(env_file_path, override=True)

"""

def preprocess_code(code):
    try:
        # Remove any leading/trailing whitespaces and normalize indentation
        normalized_code = textwrap.dedent(code).strip()
        
        # Compile to check for syntax errors
        compile(normalized_code, '<string>', 'exec')
        return normalized_code, None
    except SyntaxError as e:
        return None, f"SyntaxError: {e}"



def ensure_libraries_installed(code):
    # Extract import statements from the code
    import_statements = [
        line.strip().split('#')[0].strip() for line in code.splitlines() 
        if line.strip().startswith('import ') or line.strip().startswith('from ')
    ]

    required_libraries = set()

    for statement in import_statements:
        try:
            # Parse the library name
            if statement.startswith('import '):
                lib_names = statement[7:].strip().split(',')
                for lib in lib_names:
                    lib_name = lib.strip().split(' as ')[0].split('.')[0]
                    required_libraries.add(lib_name)
            elif statement.startswith('from '):
                full_module_name = statement[5:].strip().split(' import ')[0]
                lib_name = full_module_name.split('.')[0]
                required_libraries.add(lib_name)
        except Exception as e:
            logging.warning(f"Could not parse import statement: {statement}. Error: {e}")

    # Install missing libraries
    for lib in required_libraries:
        if importlib.util.find_spec(lib) is None:
            try:
                logging.info(f"Installing missing library: {lib}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to install library {lib}: {e}")


# def execute_code_with_retries(text_input):
#     log_stream = StringIO()
#     logging.basicConfig(stream=log_stream, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')


#     # Initial code execution
#     print("Sending input to LLM for initial response...")
#     llm_response = get_chat_response(text_input)

#     # Extract Python code and JSON from the LLM response
#     code_to_execute = extract_python_code(llm_response)

#     if not code_to_execute.strip():
#         logging.error("No valid Python code found in the LLM response.")
#         return "Error: No valid Python code extracted.", 'Error'

#     # Map environment variables into the code
#     code_to_execute = map_env_variables(code_to_execute, extract_json_object(llm_response))
#     code_to_execute = extract_python_code(code_to_execute)

#     code_to_execute = env_loading_code + code_to_execute

#     # Preprocess the code
#     # preprocessed_code, error = preprocess_code(code_to_execute)
#     # if error:
#     #     logging.error(f"Preprocessing failed: {error}")
#     #     return f"Error: {error}", 'Error'

#     # Ensure required libraries are installed before executing the code
#     ensure_libraries_installed(code_to_execute)

#     # # Prepare execution context
#     # exec_globals = {}
#     # exec_globals['__builtins__'] = __builtins__  # Include built-in functions

#     # # Execute the code dynamically
#     # try:
#     #     exec(code_to_execute, exec_globals)
#     # except Exception as e:
#     #     logging.error(f"Error executing dynamic code: {str(e)}")
#     #     logging.error(traceback.format_exc())
#     #     return f"Execution failed: {str(e)}", 'Error', code_to_execute

#     # # Retrieve logs from the execution
#     # log_stream.flush()
#     # log_messages = log_stream.getvalue()

#     # # Check if the executed code defined a `log_messages` variable
#     # if "log_messages" in exec_globals:
#     #     response_variable = exec_globals["log_messages"]
#     # elif log_messages.strip():
#     #     response_variable = log_messages.strip()
#     # else:
#     #     response_variable = "No log messages or outputs were generated."

#     # logging.debug(f"Captured log messages: {response_variable}")
#     # return response_variable, 'Success', code_to_execute

#     # Prepare execution context
#     exec_globals = {}
#     exec_globals['__builtins__'] = __builtins__  # Include built-in functions

#     # Redirect stdout and stderr to capture print statements and errors
#     original_stdout = sys.stdout
#     original_stderr = sys.stderr
#     stdout_buffer = StringIO()
#     stderr_buffer = StringIO()
#     sys.stdout = stdout_buffer
#     sys.stderr = stderr_buffer

#     try:
#         # Execute the code dynamically
#         exec(code_to_execute, exec_globals)
#     except Exception as e:
#         logging.error(f"Error executing dynamic code: {str(e)}")
#         logging.error(traceback.format_exc())
#         # Restore stdout and stderr
#         sys.stdout = original_stdout
#         sys.stderr = original_stderr
#         return f"Execution failed: {str(e)}", 'Error', code_to_execute
#     finally:
#         # Always restore stdout and stderr
#         sys.stdout = original_stdout
#         sys.stderr = original_stderr

#     # Retrieve outputs from the execution
#     stdout_output = stdout_buffer.getvalue()
#     stderr_output = stderr_buffer.getvalue()
#     log_output = log_stream.getvalue()

#     # Combine all outputs
#     outputs = ""
#     if stdout_output.strip():
#         outputs += f"Standard Output:\n{stdout_output}\n"
#     if stderr_output.strip():
#         outputs += f"Standard Error:\n{stderr_output}\n"
#     if log_output.strip():
#         outputs += f"Logs:\n{log_output}\n"

#     if not outputs.strip():
#         outputs = "No outputs were generated."

#     return outputs.strip(), 'Success', code_to_execute



def execute_code_with_retries(text_input, response_variable, latest_code, correct_errors):
    # Initialize logging
    log_stream = StringIO()
    logging.basicConfig(stream=log_stream, level=logging.DEBUG, format='%(levelname)s: %(message)s')
    
    max_attempts = 3
    attempts = 0
    success = False  # Flag to check if execution succeeded


    # Initial code generation
    print("Sending input to LLM for initial response...")
    if correct_errors:
        logging.debug("EXECUTOR.PY EXCUTE CODE WITH RETRIES: ERROR PATH ***********************************************************")
        llm_response = get_chat_response(
                    text_input=text_input,
                    correct_errors=correct_errors,
                    response_variable=response_variable,
                    latest_code=latest_code
                )
    else:
        logging.debug("EXECUTOR.PY EXCUTE CODE WITH RETRIES: SUCCESS PATH ***********************************************************")
        llm_response = get_chat_response(text_input)
        

    # llm_response = get_chat_response(text_input)
    code_to_execute = extract_python_code(llm_response)

    if not code_to_execute.strip():
        logging.error("No valid Python code found in the LLM response.")
        return "Error: No valid Python code extracted.", 'Error', code_to_execute

    while attempts < max_attempts:
        attempts += 1
        print(f"\nAttempt {attempts} in the current execution...")
        
        # Map environment variables into the code
        code_to_execute = map_env_variables(code_to_execute, extract_json_object(llm_response))
        code_to_execute = extract_python_code(code_to_execute)
        code_to_execute = env_loading_code + code_to_execute

        # Ensure required libraries are installed before executing the code
        ensure_libraries_installed(code_to_execute)

        # Prepare execution context
        exec_globals = {}
        exec_globals['__builtins__'] = __builtins__  # Include built-in functions

        # Redirect stdout and stderr to capture print statements and errors
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        stdout_buffer = StringIO()
        stderr_buffer = StringIO()
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer

        try:
            exec(code_to_execute, exec_globals) 
            success = True  # Execution succeeded

            # Capture outputs after successful execution
            sys.stdout.flush()
            sys.stderr.flush()
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()
            log_output = log_stream.getvalue()

            # Combine all outputs into response_variable
            response_variable = ""
            if stdout_output.strip():
                response_variable += f"Standard Output:\n{stdout_output}\n"
            if stderr_output.strip():
                response_variable += f"Standard Error:\n{stderr_output}\n"
            if log_output.strip():
                response_variable += f"Logs:\n{log_output}\n"
            if not response_variable.strip():
                response_variable = "The code executed successfully with no output."

            break  # Exit the loop since execution was successful

        except Exception as e:
            # Execution failed
            logging.error(f"Error executing dynamic code: {str(e)}")
            logging.error(traceback.format_exc())

            # Retrieve outputs from the execution
            sys.stdout.flush()
            sys.stderr.flush()
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()
            log_output = log_stream.getvalue()

            # Combine all outputs into response_variable
            response_variable = ""
            if stdout_output.strip():
                response_variable += f"Standard Output:\n{stdout_output}\n"
            if stderr_output.strip():
                response_variable += f"Standard Error:\n{stderr_output}\n"
            if log_output.strip():
                response_variable += f"Logs:\n{log_output}\n"
            if not response_variable.strip():
                response_variable = "No outputs were generated."

            if attempts >= max_attempts:
                # Max attempts reached, return error
                return response_variable.strip(), 'Error', code_to_execute
            else:
                # Use get_chat_response to get corrected code
                print("Execution failed. Sending outputs to LLM for error correction...")
                llm_response = get_chat_response(
                    text_input=text_input,
                    correct_errors=correct_errors,
                    response_variable=response_variable,
                    latest_code=latest_code
                )
                code_to_execute = extract_python_code(llm_response)
                if not code_to_execute.strip():
                    logging.error("No valid Python code found in the LLM response.")
                    return "Error: No valid Python code extracted.", 'Error', code_to_execute
                continue  # Retry with the corrected code

        finally:
            # Always restore stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    if success:
        # Return outputs from the successful execution
        return response_variable.strip(), 'Success', code_to_execute
    else:
        # Should not reach here, but just in case
        return "Execution failed after maximum retries.", 'Error', code_to_execute


def test_completion(text_input):
    return test_openai_connection(text_input)