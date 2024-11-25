from flask import Flask, request, jsonify, send_from_directory
from executor import execute_code_with_retries, test_completion
import os
import logging
from dotenv import load_dotenv

# Load environment variables from the .env file
env_file_path = '../oneConnection.env'
load_dotenv(env_file_path)

# Verify environment variables are loaded
# print("Environment Variables:")
# for key, value in os.environ.items():
#     print(f"{key}: {value}")

# Initialize Flask app
app = Flask(__name__, static_folder='../Public')

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def serve_index():
    # Serve the index.html file from the Public folder
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # Serve other static files (e.g., CSS, images) from the Public folder
    return send_from_directory(app.static_folder, path)


@app.route('/process', methods=['POST'])
def process_request():
    try:
        # Get the plain text input from the request body
        text_input = request.get_json().get('prompt', '').strip()
        
        if not text_input:
            logging.error("Received empty request body.")
            return jsonify({'status': 'Error', 'response': 'Invalid request. Empty input provided.'}), 400
        
        logging.debug(f"Received plain text input: {text_input}")

        # Execute the code and handle responses
        response, status, executed_code = execute_code_with_retries(text_input, response_variable=None, latest_code=None, correct_errors=False)

        logging.debug(f"Initial execution response: {response}")
        print(f"APP.PY EXCUTION COMPLETED ***********************************************************")
        
        # Retry logic if errors are detected
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            attempts += 1
            # Check if errors are present in the response logs
            error_detected = any(line.startswith("ERROR:") for line in response.strip().splitlines())
            if error_detected:
                print(f"APP.PY EXCUTION COMPLETED: ERROR ***********************************************************\n{text_input}\n{response}\n{executed_code}")
                print(f"Error detected on attempt {attempts}. Retrying...")
                response, status, executed_code = execute_code_with_retries(
                    text_input, response_variable=response, latest_code=executed_code, correct_errors=True
                )
            else:
                # Successful execution
                print(f"APP.PY EXCUTION COMPLETED: SUCCESS ***********************************************************")
                return jsonify({
                    'status': status,
                    'response': response,
                    'code': executed_code
                })

        # Max retries exceeded
        print(f"APP.PY MAX EXCUTION ATTEMPTS REACHED :: EXCUTION COMPLETED: ERROR ***********************************************************")
        return jsonify({
            'status': 'Error',
            'response': 'Execution failed after multiple attempts.',
            'code': executed_code
        }), 500

    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("An error occurred while processing the request.")
        return jsonify({'status': 'Error', 'response': 'Internal Server Error. Please try again later.'}), 500



@app.route('/test_openai', methods=['POST'])
def test_openai_endpoint():
    try:
        # Get the plain text input from the request body
        text_input = request.data.decode('utf-8').strip()  # Decode and remove extra whitespace
        
        if not text_input:
            logging.error("Received empty request body.")
            return jsonify({'status': 'Error', 'response': 'Invalid request. Empty input provided.'}), 400
        
        logging.debug("Testing OpenAI connection with input: %s", text_input)

        # Call the test_completion function to send the input to OpenAI
        response = test_completion(text_input)

        # Return the response from OpenAI
        return jsonify({'status': 'Success', 'response': response})
    except Exception as e:
        # Log the exception and return a 500 error
        logging.exception("An error occurred while testing OpenAI connection.")
        return jsonify({'status': 'Error', 'response': 'Internal Server Error. Please try again later.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
