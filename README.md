# OneConnection

This application processes free-form user queries and uses a Large Language Model (LLM) to dynamically generate Python code that connects to specified tools and extracts user-requested data. It features a JavaScript-based frontend and a Python backend built with Flask.

## Key Features

### Dynamic Code Generation
The application forwards user input to an LLM, which generates Python code to handle data extraction tasks.

### Iterative Debugging
The application executes the generated code and retrieves the requested data. The result is displayed in the frontend UI for the user.
The execution output is stored in a response_variable for debugging and further refinement.

### Error Handling and Code Refinement
If the code fails to execute (e.g., due to errors), the application sends the user input, generated code, and execution response back to the LLM.
The LLM analyzes the errors and attempts to fix the code. This process is repeated up to 3 times until a working solution is produced.
This approach ensures robust, adaptive handling of user queries, leveraging the LLM’s reasoning capabilities to improve code accuracy and execution success.

## Intallation Guide

```
ONECONNECTION
│
├── Public
│   ├── index.html
│   ├── style.css
│
├── backend
│   ├── app.py                     # Main Flask app for handling requests from the frontend
│   ├── executor.py                # Module to execute Python code and handle retries
│   ├── chat_helpers.py            # Helper functions for interacting with the Large Langiage Model (LLM) 
│   ├── templates.py               # Template strings for prompt templates
│   ├── utils.py                   # Utility functions (e.g., extract Python code)
│   └── requirements.txt           # Dependencies for the backend
│
└── oneConnection.env              # Environment variables file
```

Follow the steps below to set up and run the OneConnection application on your local environment.

<b>Prerequisites</b>
Before installing, ensure you have the following:

* <b>Python 3.8+</b> installed on your system.
* <b>Node.js</b> (if additional frontend functionality is required in the future).
* A package manager like pip for Python dependencies.
* <b>Brew</b> (if you are on macOS) for managing system dependencies.

### Step 1: Clone the Repository

Clone this repository to your local machine
<code>
git clone <REPOSITORY_URL>
cd <PROJECT_FOLDER>
</code>

### Step 2: Backend Setup (Flask Application)

<b>1. Update System Packages (macOS-specific)</b><br>
If you are on macOS, update brew and ensure Python and OpenSSL are correctly installed:
<code>
brew update
brew install openssl
brew reinstall python
</code>

<b>2. Create a Virtual Environment</b><br>
Navigate to the backend folder and create a virtual environment:
<code>
cd backend
python3 -m venv venv
</code>

<b>3. Activate the Virtual Environment</b><br>
Activate the virtual environment:
* On macOS/Linux
    <code>
    source venv/bin/activate
    </code>
* On Windows (Command Prompt)
    <code>
    venv\Scripts\activate
    </code>

<b>4. Install Backend Dependencies</b><br>
Install the required dependencies listed in <b>requirements.txt</b>
<code>
pip install -r requirements.txt
</code>

<b>5. Configure Environment Variables</b><br>
Create <code>oneConnection.env</code> in your root project folder and add your environment-specific variables (e.g., API keys, tokens).

<b>5. Set-up LLM Connection</b><br>
TODO: in chat_helpers.py

### Step 3: Frontend Setup (HTML/CSS)

The static frontend files are located in the <code>Public</code> folder:

* index.html: The main UI.
* style.css: Contains all styles for the application.

There is no need for additional setup for the frontend unless changes or additional functionality are required.

### Step 4: Run the Application

<b>1. Start the Backend</b><br>
Run the Flask application from the <code>backend</code> folder!
<code>
python3 app.py
</code>

Alternatively, you can use:
<code>
python app.py
</code>

<b>2. Access the Application</b><br>
Once the backend starts, you can access the application at the port configured in <b>app.py</b> e.g. if:
<code>
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
</code>

then
<code>
http://localhost:3001/
</code>




