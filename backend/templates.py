example_connection = """
from sp_api.api import Reports
from sp_api.base import SellingApiException, Marketplaces, Credentials
import json
import time

# Define variables for the connection
aws_access_key = "your-aws-access-key"           # Replace with your AWS access key
aws_secret_key = "your-aws-secret-key"           # Replace with your AWS secret key
role_arn = "your-role-arn"                       # Replace with your IAM role ARN
refresh_token = "your-refresh-token"             # Replace with your SP-API refresh token
client_id = "your-client-id"                     # Replace with your LWA client ID
client_secret = "your-client-secret"             # Replace with your LWA client secret
marketplace = Marketplaces.US                    # Replace with appropriate marketplace

# Initialize the SP-API connection
def connect_to_amazon():
    try:
        credentials = Credentials(
            refresh_token=refresh_token,
            lwa_app_id=client_id,
            lwa_client_secret=client_secret,
            aws_secret_key=aws_secret_key,
            aws_access_key=aws_access_key,
            role_arn=role_arn
        )
        reports = Reports(credentials=credentials, marketplace=marketplace)
        return reports
    except SellingApiException as e:
        print("Failed to connect to Amazon SP-API:", str(e))
        return None

# Fetch sales performance data
def get_sales_performance_data(reports):
    try:
        # Request a report
        report_response = reports.create_report(
            reportType='GET_FLAT_FILE_OPEN_LISTINGS_DATA'
        )
        report_id = report_response.payload.get('reportId')

        # Poll until the report is ready
        while True:
            report_status = reports.get_report(report_id)
            if report_status.payload.get('processingStatus') == 'DONE':
                break
            print("Waiting for report to be ready...")
            time.sleep(10)  # Wait 10 seconds before checking again

        # Fetch the report document
        document_response = reports.get_report_document(reportId=report_id)
        document = document_response.payload

        # Print the document data in JSON format
        print(json.dumps(document, indent=2))

    except SellingApiException as e:
        print("Failed to fetch sales performance data:", str(e))

# Main workflow
amazon_client = connect_to_amazon()
if amazon_client:
    get_sales_performance_data(amazon_client)
else:
    print("Amazon SP-API connection could not be established.")

"""

example_json_object = """
{
  "jira_server": "string",
  "jira_username": "string",
  "jira_api_token": "string",
  "project_key": "string"
}
"""

example_logging = """
# Set up a string stream to capture log messages
log_stream = StringIO()
logging.basicConfig(level=logging.INFO, stream=log_stream, format='%(levelname)s:%(message)s', force=True)

{{code}}

# Flush the log stream to ensure all messages are captured
log_stream.flush()

# Return the log messages
log_messages = log_stream.getvalue()
print(log_messages)
"""

example_logging_old = """
Add detailed logging to every key step in the code, including:
1. The values of critical variables such as `jira_server`, `jira_username`, and `jira_api_token` after they are read from the environment.
2. Entry and exit points of each function.
3. Error handling that includes the state of variables and any relevant context.
4. Capture and flush all logs to ensure all information is available for debugging.

# Set up a string stream to capture log messages
log_stream = StringIO()
logging.basicConfig(level=logging.DEBUG, stream=log_stream, format='%(asctime)s %(levelname)s:%(message)s', force=True)

{{code}}

# Flush the log stream to ensure all messages are captured
log_stream.flush()

# Return the log messages
log_messages = log_stream.getvalue()
print(log_messages)
"""

template_freeform_to_code = """
You must act as an experienced Python developer with deep API integration knowledge. You must be able to process text_input which is an ad-hoc request from an user to connect to a specific tool or application in order to retrieve data from it. 

Given the text_input:

**Think**, what type of authentication the tool supports!
**Think**, which are the variable or unknown elements at this point which are needed to enable successful connection, authentication and data retrieval!
***Check the {example_connection}***

1. Write Python code to connect to the specified tool to get the specified data following the below rules: 
   - First check for dedicated Python library, for the toop specified in the text_input, to make API requests and retrieve data. If there is available library then you must use it to generate the code.
   - If no dedicated library exists, then use Python's "requests" library to interact with the tool's API.
   - All required parameter for successful authentication with the API must be included.
   - Extract all variable elements in the code as variables to be populated.
   - Wrap the code in a custom logging handler to capture the log messages into a variable. See how to do it in {example_logging}
   - Include error handling
   - **Stric rule** Produce only working code. It must include all necessary functions for successful connection, authentication and data retrieval. It must be able to authenticate from the beginning asuming no prior authentication steps have been done.

Output: produced code

2. Extract all variable elements that are still to be specified from the produced code and output them as a JSON object. Follow this example output: {example_json_object}

Output as a JSON object:
   "variable" : "variable_type" 

text_input: {text_input}
"""


example_mapping = """
jira_server = os.getenv('JIRA_URL')  # Replace with your Jira server URL
jira_username = os.getenv('JIRA_EMAIL')  # Replace with your Jira username (usually an email)
jira_api_token = os.getenv('JIRA_API_TOKEN')  # Replace with your Jira API token
"""

template_map_env_variables = """
Given {produced_python_code} and {produced_variables_json}, look up the variable keys from {produced_variables_json}
in the {produced_python_code} and *substitute ONLY* the connection authentication related ones with the corresponding value from the {environment_variables}.

The environment variables in {produced_variables_json} and {environment_variables} may not match one-to-one,
and you must do the mapping based on tool and common context.

Check this example how the code should look like after the variables are mapped: {example_mapping}

Output: updated code
"""

template_unit_test = """
Check if the {execute_python_code_updated_env_vars} code is working correctly given the response it produces {response_variable} and 
the original user free form request {text_input}. Fix the code if needed and check again that it is working as expected.

Output: fixed python code
"""

template_code_validation = """
You are provided with the original user input: "{text_input}".
The latest code that was executed and resulted in an error is as follows:

```python
{latest_code}
```

The execution resulted in the following outputs:

{response_variable}

Please analyze the code and the outputs to identify any errors. Provide a corrected version of the code that addresses the issues. Only provide the code in your response, enclosed within triple backticks like this:

```python
# Corrected code here
```

Extract all variable elements from the produced code and output them as a JSON object. Follow this example output: 

```json_object
{{
  "jira_server": "string",
  "jira_username": "string",
  "jira_api_token": "string",
  "project_key": "string"
}}
```
"""

template_code_validation_old = """
Given {formatted_prompt1}

Review the provided code for errors and suggest any corrections. Ensure all required libraries are imported, and that the authentication and request processes are correct for the API.

{produced_python_code1}

Output: corrected code
Output as a JSON object:
   - "variable" : "variable_type" 

"""