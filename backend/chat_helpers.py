from langchain.prompts import ChatPromptTemplate
import os
from langchain_openai import ChatOpenAI
import openai
from dotenv import load_dotenv, dotenv_values

# Import the templates from the template module
from templates import (
    template_freeform_to_code,
    example_json_object,
    example_logging,
    example_connection,
    example_mapping,
    template_map_env_variables,
    template_code_validation
)

# Define the path to the .env file
env_file_path = '../oneConnection.env'

# Load environment variables from the .env file into the process environment
load_dotenv(env_file_path)

# Fetch the OpenAI API key from the environment
openai.api_key = os.getenv('OPENAI_API_KEY')

# Get the environment variables from the .env file as a dictionary
env_vars = dotenv_values(env_file_path)

# Print and return the list of environment variable keys
environment_variables = list(env_vars.keys())
print("Environment Variables in oneConnection.env:")
print(environment_variables)

chat = ChatOpenAI(
    temperature=0.2,
    model="gpt-4o",
    top_p=1.0,
    presence_penalty=0
)

# chat = ChatOpenAI(
#     temperature=1,
#     model="o1-mini",
#     top_p=1.0,  # Specify directly as a parameter
#     presence_penalty=0  # Specify directly as a parameter
# )

def get_chat_response(text_input, correct_errors=False, response_variable=None, latest_code=None):
    if correct_errors:
        try:
            # Generate prompt for correcting code errors
            print("CHAT_HELPERS.PY GET CHAT RESPONSE :: ERROR PATH ***********************************************************")
            prompt_template = ChatPromptTemplate.from_template(template_code_validation)
            formatted_prompt = prompt_template.format_prompt(
                text_input=text_input,
                latest_code=latest_code,
                response_variable=response_variable
            )
        except Exception as e:
            print(f"Error creating or formatting prompt: {e}")
            return None  # Or handle appropriately
    else:
        # Initial prompt for generating Python code
        print("CHAT_HELPERS.PY GET CHAT RESPONSE :: SUCCESS PATH ***********************************************************")
        prompt_template = ChatPromptTemplate.from_template(template_freeform_to_code)
        formatted_prompt = prompt_template.format_prompt(
            text_input=text_input,
            example_connection=example_connection,
            example_logging=example_logging,
            example_json_object=example_json_object
        )
    
    response = chat.invoke(formatted_prompt)
    print(F"CHAT_HELPERS.PY GET CHAT RESPONSE :: LLM RESPONSE ***********************************************************\n{response.content}")
    return response.content


def map_env_variables(produced_code, variables_json):
    print("Mapping environment variables into the code...")
    prompt_template = ChatPromptTemplate.from_template(template_map_env_variables)
    formatted_prompt = prompt_template.format_prompt(
        produced_python_code=produced_code, 
        produced_variables_json=variables_json, 
        environment_variables=environment_variables, 
        example_mapping=example_mapping
    )

    response = chat.invoke(formatted_prompt)
    print(response.content)
    return response.content


def test_openai_connection(text_input):
    response = chat.invoke(text_input)
    return response.content
