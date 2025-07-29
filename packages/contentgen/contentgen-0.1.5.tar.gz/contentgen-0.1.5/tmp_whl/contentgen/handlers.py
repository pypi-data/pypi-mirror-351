# from groq import Groq
import google.generativeai as genai
import json
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import sys
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import re  # Add import for regex
import sqlite3
from datetime import datetime, timezone

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

gemini_api_key = str(os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# set up SQLite database
db_path = os.path.join(os.path.dirname(__file__), "contentgen_logs.db")
con = sqlite3.connect(db_path)
cur = con.cursor()
print("Checking/Creating data logging table...")
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        prompt_type TEXT,
        question_type TEXT,
        notebook_name TEXT,
        notebook_dir TEXT,
        selected_cell TEXT,
        user_input TEXT,
        previous_question TEXT,
        prompt_template TEXT,
        llm_response TEXT,
        user_decision TEXT
    )
"""
)
con.commit()
con.close()

prompt_summary = """
# Task: Webpage Summarization and Notebook Integration

## Input
1. Notebook content: The Jupyter notebook that needs to be augmented with webpage information
2. Webpage text: Content extracted from the URL the user provided

## Instructions
1. Analyze the notebook content to understand its topic and structure
2. Examine the webpage text and extract the key information
3. Create a concise, well-structured summary of the webpage content
4. Determine the most logical location in the notebook to insert this summary
   - Find a contextually appropriate position based on topic relevance
   - Consider section breaks, headers, or related content

## Response Format
Return ONLY a valid JSON string with these three fields:
{
  "indexToInsert": <integer index where the summary should be inserted>,
  "title": "<title of the webpage or a descriptive headline>",
  "summary": "<your concise, formatted summary of the webpage content, this should be in one line, use \n for line breaks>"
}

## Note
Your summary should be comprehensive enough to convey the key points but brief enough to fit well within the notebook flow.
"""


# new prompt_question with notebook_structure
prompt_question = """
# Task Definition
You are an educational content generator analyzing a Jupyter notebook lecture to create related practice exercises.

# Context
I will provide you with:
- The complete notebook content including text and code cells
- The currently selected cell that should serve as a reference
- Variables and outputs from executed code cells
- The question type being requested
- A structured summary of the notebook's organization (each topic includes: concepts, functions, and datasets)

# Instructions
1. Analyze the full notebook using both `notebook_content` and `notebook_structure` to determine the context of the selected cell:
   - Use the cell index to identify which topic (from the notebook structure) the selected cell belongs to.
   - Consider the surrounding markdown and code cells to understand the educational goal, concepts being taught, and the logical scope of the topic.
   - Ensure that any generated question remains within the bounds of that topic, leveraging relevant concepts, functions, or datasets tied to the selected topic only.

2. Generate a new code example that:
   - Do not repeat the same code as the selected cell!
   - Follows a similar structure to the selected cell
   - Implements related concepts with minor but relevant differences 
   - Uses existing datasets/DataFrames from the executed variables
   - No need to import any libraries, espeically pandas or numpy!!!!!!!!!!!!
   - Assume that numpy has been imported as np
   - Check whether the user is using pandas (pd) or babypandas (bpd), and use the same library (pd or bpd) for the generated code

3. Create a concise lecture question that:
   - Is directly related to the notebook content before the insertion point
   - Has your generated code as the correct answer
   - Is appropriate for the specified question type
   
4. JSON Formatting notes:
   - The summary portion of the response should be in one line, if there should be a line break somewhere, ONLY use \n
   - In JSON, backslashes must be escaped, so each \' should be written as \\'.
   - Make sure that the JSON is valid and properly formatted to be able to be parsed

# Response Format
Respond with ONLY a valid JSON string in this exact format (DO NOT add anything extra to the response):
{{
  "indexToInsert": notebook.activeCellIndex,
  "title": "Brief descriptive title for this question",
  "summary": "Question: [Your question here]\\n\\nAnswer:\\n```python\\n[Your code here]\\n```"
}}

#Generate valid JSON only. Follow these rules strictly for escaping characters and use double quotes for all keys and string values.

Use these valid escape sequences in all JSON strings:

\\ → backslash
\" → double quote (needed because strings are enclosed in " in JSON)
\/ → forward slash (optional; rarely needed)
\n → newline
\t → tab

Do NOT use:
    1. \' (invalid — single quotes do not need escaping in JSON)
    2. \ followed by any character not listed above (will throw a JSON parse error)

Wrap all string values and object keys in double quotes only.
Do not use single quotes (') for keys or string values.


# Notebook Details
Notebook content: {notebook_content}
Current Selected Cell: {selected_cell}
Code cells: {code_cells}
Executed code variables: {executed_variables}
Question type: {question_type}
User question: {user_input}
Notebook structure: {notebook_structure}
"""


# Add a new prompt for follow-up questions
prompt_followup = """
# Task Definition
You are an educational content generator refining a previously generated practice exercise.

# Context
I will provide you with:
- The complete notebook content
- The previously generated question and answer
- The user's follow-up request for modifications
- A structured summary of the notebook's organization (each topic includes: concepts, functions, and datasets)

# Instructions
1. Analyze the user's follow-up request to understand what changes they want

2. Use the provided `notebook_structure` to determine the topic scope of the original question:
   - Match the original question's cell index to the corresponding topic using the `Range Cell` values.
   - When modifying the question or code, aim to stay within the same topic's scope whenever possible.
   - Prefer to use concepts, functions, and datasets listed under that topic in the structure.
   - If the user's request introduces content outside the original topic, you may adapt the question accordingly.

3. Modify the previously generated question and answer code to address their request
   - Implements related concepts with minor but relevant differences 
   - No need to import any libraries, especially pandas or numpy! 
   - Continue using the same dataframes and columns as in the original question unless the user specifically requests otherwise
   - Maintain consistency with the data structures used in the original question
   - Check whether the user is using pandas (pd) or babypandas (bpd), and use the same library (pd or bpd) for the generated code

4. Common requests include:
   - Making the question easier or harder
   - Focusing on a different aspect of the concept
   - Simplifying or expanding the code

5. JSON Formatting notes:
   - The summary portion of the response should be in one line, if there should be a line break somewhere, ONLY use \n
   - In JSON, backslashes must be escaped, so each \' should be written as \\'.
   - Make sure that the JSON is valid and properly formatted to be able to be parsed

# Response Format
Respond with ONLY a valid JSON string in this exact format (DO NOT add anything extra to the response):
{{
  "indexToInsert": notebook.activeCellIndex,
  "title": "Brief descriptive title for this question",
  "summary": "Question: [Your modified question here]\\n\\nAnswer:\\n```python\\n[Your modified code here]\\n```"
}}

# Details
Notebook content: {notebook_content}
Previous question and answer: {previous_question}
User follow-up request: {user_input}
Notebook structure: {notebook_structure}
"""

executed_results = {}


import os
import sys
import traceback
from io import StringIO


def clean_code(code):
    """
    Removes Jupyter magic commands (e.g., %%timeit) and any other invalid notebook syntax.
    """
    cleaned_lines = []
    for line in code.split("\n"):
        if not line.strip().startswith("%%"):  # Remove cell magic commands
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def execute_code(code, directory):
    """
    Executes Python code in the specified directory and captures both
    output (print statements) and variables defined in the execution.
    """

    # Save the original working directory
    original_directory = os.getcwd()

    # Redirect stdout and stderr to capture output
    output_buffer = StringIO()
    error_buffer = StringIO()

    # Dictionary to store the execution namespace
    local_vars = {}

    try:
        # Change to the specified directory if provided
        if directory:
            os.chdir(directory)
            if directory not in sys.path:
                sys.path.insert(0, directory)
                print("Added directory to paths")

        print("Current directory:", os.getcwd())
        print("Files in directory:", os.listdir())
        print("sys.path:", sys.path)

        print("Flushing stdout...")
        sys.stdout.flush()
        sys.stderr.flush()

        code = clean_code(code)

        # Use redirect_stdout() and redirect_stderr() to safely capture output
        with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
            print("Executing code...")
            exec(code, globals())

        print("Execution completed!")

        # Extract captured output and errors
        output = output_buffer.getvalue().strip()
        print("Output:", output)
        error = error_buffer.getvalue().strip()
        print("Error:", error)

    except Exception as e:
        print(f"Exception: {e}")
        error = traceback.format_exc()
        output = ""

    finally:
        # Restore stdout, stderr, and working directory
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        os.chdir(original_directory)

    # Remove built-in functions and modules
    executed_results = {k: v for k, v in globals().items() if not k.startswith("__")}
    # print(
    #     "To be returned:",
    #     {"output": output, "error": error, "variables": executed_results},
    # )

    print("Finished executing code cells.")

    return {"output": output, "error": error, "variables": executed_results}


def validate_url(url):
    """
    Validates if a string is a proper URL.
    Returns (is_valid, error_message)
    """
    # Simple URL validation using regex
    url_pattern = re.compile(
        r"^(?:http|https)://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # or ipv4
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        return False, "Invalid URL format"

    return True, ""


def fetch_url_content(url):
    """
    Fetches and extracts main content from a URL.
    Returns (success, content_or_error)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.decompose()

        # Extract page title
        title = soup.title.string if soup.title else url

        # Extract text from remaining tags
        text = soup.get_text(separator=" ", strip=True)

        # Clean up text: remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Get a reasonable length of text (first 8000 chars to avoid token limits)
        text = text[:8000]

        return True, {"title": title, "content": text}

    except requests.exceptions.RequestException as e:
        return False, f"Failed to fetch URL: {str(e)}"
    except Exception as e:
        return False, f"Error processing URL content: {str(e)}"


class MessageHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self):
        try:
            global prompt_summary
            global prompt_question
            global prompt_followup
            global executed_results

            # Get all variables upfront
            input_data = self.get_json_body()
            nt_content = input_data.get("notebookContent", "")
            user_notebook = str(nt_content)
            prompt_type = input_data.get("promptType", "")
            selected_cell = input_data.get("selectedCell", "")
            question_type = input_data.get("questionType", "")
            code_cells = input_data.get("notebookCodeCells", [])
            is_followup = input_data.get("isFollowup", False)
            # if is_followup:
            #     user_input += input_data.get("message", "")
            # else:
            #     user_input = input_data.get("message", "")
            # if is_followup:
            #     previous_question += input_data.get("previousQuestion", "")
            # else:
            #     previous_question = input_data.get("previousQuestion", "")
            user_input = input_data.get("message", "")
            previous_question = input_data.get("previousQuestion", "")
            notebook_directory = input_data.get("notebookDirectory", "")
            notebook_name = input_data.get("notebookName", "")
            notebook_structure = input_data.get("notebookStructure", "")

            # Create a local prompt variable - no global modification
            if prompt_type == "summary":
                current_prompt = prompt_summary
                prompt_template_name = "prompt_summary"  # for db
            elif is_followup:
                current_prompt = prompt_followup
                prompt_template_name = "prompt_followup"  # for db
            else:
                current_prompt = prompt_question
                prompt_template_name = "prompt_question"  # for db

            # insert to db
            try:
                con = sqlite3.connect(db_path)
                cur = con.cursor()
                print("Trying to insert into logs table...")
                cur.execute(
                    """
                    INSERT INTO logs (
                        timestamp,
                        prompt_type,
                        question_type,
                        notebook_name,
                        notebook_dir,
                        selected_cell,
                        user_input,
                        previous_question,
                        prompt_template,
                        llm_response,
                        user_decision
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        datetime.now(timezone.utc).isoformat(),
                        prompt_type,
                        question_type,
                        notebook_name,
                        notebook_directory,
                        selected_cell,
                        user_input,
                        previous_question,
                        prompt_template_name,
                        None,  # LLM response (to be updated later)
                        None,  # user_decision (to be updated later)
                    ),
                )

                row_id = cur.lastrowid
                print("Current last row ID is", row_id)
                con.commit()
                con.close()
            except Exception as e:
                print("Initial DB insert failed:", e)
                row_id = None

            # Handle URL validation and content fetching for summary mode
            webpage_content = None
            if prompt_type == "summary":
                # Validate URL
                is_valid, error_msg = validate_url(user_input)
                if not is_valid:
                    self.set_status(400)
                    self.finish(json.dumps({"error": error_msg}))
                    return

                # Fetch URL content
                success, result = fetch_url_content(user_input)
                if not success:
                    self.set_status(400)
                    self.finish(json.dumps({"error": result}))
                    return

                webpage_content = result
                print(
                    f"Successfully fetched URL content. Title: {webpage_content['title']}"
                )
                print(f"Content length: {len(webpage_content['content'])} characters")

            if current_prompt == prompt_question:
                try:
                    # Handle code execution for questions
                    if question_type != "conceptual":

                        print(f"Notebook directory: {notebook_directory}")

                        notebook_code_cells = input_data.get("notebookCodeCells", [])
                        print(f"Number of code cells: {len(notebook_code_cells)}")

                        if notebook_code_cells:
                            execution_result = execute_code(
                                "\n\n".join(
                                    cell["content"] for cell in notebook_code_cells
                                ),
                                notebook_directory,
                            )
                            # print("Code execution result:", execution_result)
                            executed_results = execution_result.get("variables", {})
                        else:
                            executed_results = {}
                except Exception as e:
                    print("Error during code execution:", e)
                    traceback.print_exc()  # Print full stack trace
                    self.set_status(500)
                    self.finish(
                        json.dumps({"error": f"Code execution failed: {str(e)}"})
                    )
                    return

                try:
                    # Construct question prompt without truncation
                    current_prompt = prompt_question.format(
                        notebook_content=user_notebook,
                        selected_cell=selected_cell,
                        code_cells=str(code_cells),
                        executed_variables=str(executed_results),
                        question_type=question_type,
                        user_input=user_input,
                        notebook_structure=notebook_structure,
                    )
                except Exception as e:
                    print("Error constructing question prompt:", e)
                    traceback.print_exc()
                    self.set_status(500)
                    self.finish(
                        json.dumps({"error": f"Failed to construct prompt: {str(e)}"})
                    )
                    return

            try:
                # Construct prompt based on type
                if is_followup:
                    # When handling multiple follow-ups, append all previous questions and user inputs to the prompt to preserve context, rather than overwriting it.
                    current_prompt = prompt_followup.format(
                        notebook_content=user_notebook,
                        previous_question=previous_question,
                        user_input=user_input,
                        notebook_structure=notebook_structure,
                    )
                elif current_prompt == prompt_question:
                    current_prompt = prompt_question.format(
                        notebook_content=user_notebook,
                        selected_cell=selected_cell,
                        code_cells=str(code_cells),
                        executed_variables=str(executed_results),
                        question_type=question_type,
                        user_input=user_input,
                        notebook_structure=notebook_structure,
                    )
                # For summary prompt, add the webpage content
                elif prompt_type == "summary":
                    # Append the webpage content to the prompt
                    current_prompt = f"{current_prompt}\n\nWebpage URL: {user_input}\nWebpage Title: {webpage_content['title']}\nWebpage Content: {webpage_content['content']}"

                # print("Final prompt:", current_prompt)

                # Make API call
                print("\n=== LLM Request Details ===")
                print(f"Prompt Type: {prompt_type}")
                print(
                    f"Question Type: {question_type if prompt_type == 'question' else 'N/A'}"
                )
                print(
                    f"Using Selected Cells: {input_data.get('useSelectedCells', False)}"
                )
                print(f"User Input: {user_input}")
                # print("\nFull Prompt being sent to LLM:")
                # print("------------------------")
                # print(current_prompt)
                # print("------------------------\n")

                print("Getting LLM response...")
                llm_response = model.generate_content(current_prompt)
                # print("\n=== LLM Response ===")
                # print(llm_response.text)
                # print("------------------------\n")

                print("Reading LLM response...")
                output = llm_response.text

                if row_id is not None:
                    try:
                        con = sqlite3.connect(db_path)
                        cur = con.cursor()
                        print("Updating LLM response for last row in database...")
                        cur.execute(
                            "UPDATE logs SET llm_response = ? WHERE id = ?",
                            (output, row_id),
                        )
                        con.commit()
                        con.close()
                        print(f"Logged LLM response to row {row_id}")
                    except Exception as e:
                        print("Failed to update llm_response in DB:", e)

                # Construct and send response

                response_data = {"reply": output, "status": "success", "row_id": row_id}
                print("Sending LLM response back to client...")
                self.finish(json.dumps(response_data))

            except Exception as e:
                print("Error during API call or response handling:", e)
                traceback.print_exc()
                self.set_status(500)
                self.finish(
                    json.dumps(
                        {
                            "error": f"API or response handling failed: {str(e)}",
                            "prompt_length": len(current_prompt),
                        }
                    )
                )
                return

        except Exception as e:
            print("Outer most layer exception:", e)
            traceback.print_exc()
            self.set_status(500)
            self.finish(json.dumps({"error": f"Request failed: {str(e)}"}))

    @tornado.web.authenticated
    def get(self):
        self.finish(json.dumps({"status": "Message service is running"}))


class LogUsageHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            input_data = self.get_json_body()
            row_id = input_data.get("row_id")
            decision = input_data.get("user_decision")

            print(f"row_id: {row_id}")
            print(f"decision: {decision}")
            print("About to insert user decision...")

            if row_id is None or decision not in ["applied", "canceled", "followed_up"]:
                self.set_status(400)
                self.finish(json.dumps({"error": "Invalid input"}))
                return

            con = sqlite3.connect(db_path)
            cur = con.cursor()
            cur.execute(
                "UPDATE logs SET user_decision = ? WHERE id = ?", (decision, row_id)
            )
            con.commit()
            con.close()

            print(f"Added user decision ({decision}) for row {row_id}.")

            self.finish(json.dumps({"status": "logged", "row_id": row_id}))
        except Exception as e:
            print("Error in LogUsageHandler:", e)
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))


class ProcessNotebookHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self):
        try:
            input_data = self.get_json_body()
            notebook_content = input_data.get("notebookContent", [])
            print("Received notebook content to be processed...")
            # print("Notebook content:", notebook_content)

            # # Construct the prompt for summarizing notebook content
            # prompt = "Summarize the following notebook content:\n\n"
            # for cell in notebook_content:
            #     prompt += f"Cell {cell['index']}:\n{cell['content']}\n\n"
            # prompt += "Provide a summary for each section."

            # Build notebook content for prompt
            notebook_cells_content = ""
            for cell in notebook_content:
                notebook_cells_content += (
                    f"Cell {cell['index']}:\n{cell['content']}\n\n"
                )

            # Build the prompt
            prompt_notebook = """
                # Task: 
                You are a notebook structure analyzer. Your job is to read the provided notebook content and extract the topics, concepts, functions, and datasets into a structured JSON format.

                ## Goal
                Analyze the provided notebook content carefully and extract its underlying structure.

                ## Instructions
                1. Read all **markdown cells** and identify:
                - Major **topics** (e.g., lecture sections, key headings).
                - Important **concepts** introduced or discussed.
                2. Read all **code cells** and extract:
                - **Functions** that are defined (`def function_name`) or heavily used.
                - **Datasets** that are loaded or created (e.g., variables storing datasets like DataFrames).
                3. For each topic:
                - Indicate the **range of cell indices** that relate to this topic as `"start_index-end_index"`.
                - Group associated **concepts**, **functions**, and **datasets** under that topic.
                4. Summarize the entire notebook by including:
                - The notebook's **title** (if known; otherwise use a placeholder).
                - The **total number of cells**.
                5. If a concept, function, or dataset is not clearly associated with a specific topic, group them under a topic called `"Other"`.

                Make sure the output strictly follows the requested JSON format without adding any extra explanation text.


                ## Output Format
                Return ONLY a valid JSON object with the following structure:

                {{
                "Notebook": {{
                    "Title": "<Title of the notebook>",
                    "TotalCell": <Number of total cells>,
                    "Structure": [
                    {{
                        "Topic": "<Topic name>",
                        "Range Cell": "<Starting cell index>-<Ending cell index>",
                        "concepts": [
                        "<Concept 1>",
                        "<Concept 2>"
                        ],
                        "functions": [
                        "<Function name 1>",
                        "<Function name 2>"
                        ],
                        "datasets": [
                        "<Dataset name 1>",
                        "<Dataset name 2>"
                        ]
                    }},
                    ...
                    ]
                }}
                }}

                - The field `Range Cell` should be a string like `"0-5"`, indicating the range of cells related to the topic.
                - If no concepts, functions, or datasets are found for a topic, return an empty list [] for that field.
                - Make sure the output is a valid, parsable JSON object.
                - Do NOT add any extra text or explanations outside the JSON object.

                
                ## Notebook Content
                {notebook_cells_content}
                """

            prompt_notebook = prompt_notebook.format(
                notebook_cells_content=notebook_cells_content
            )

            # print("Prompt for processing notebook:", prompt_notebook)

            # Make API call to Gemini model
            llm_response = model.generate_content(prompt_notebook)
            # print("Gemini processed notebook:", llm_response.text)

            print("Parsing LLM response for notebook structure...")
            # Parse the response
            response_data = {"response": llm_response.text}

            print("Sending notebook structure back...")
            self.finish(json.dumps(response_data))
        except Exception as e:
            print("Error processing notebook content:", e)
            traceback.print_exc()
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))


class APIKeyCheckHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
        load_dotenv(dotenv_path)
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            self.finish(json.dumps({"hasKey": False}))
            return

        print("Existing API key:", api_key)

        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")  # Use a real model
            response = model.generate_content(
                "Hello"
            )  # Minimal content generation request

            self.finish(json.dumps({"hasKey": True}))
            return
        except Exception as e:
            print(f"API Key validation failed: {e}")
            self.finish(json.dumps({"hasKey": False}))
            return

        # if api_key:
        #     self.finish(json.dumps({"hasKey": True}))
        # else:
        #     self.finish(json.dumps({"hasKey": False}))


class SaveApiKeyHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        global model, api_key_is_valid
        try:
            input_data = self.get_json_body()
            api_key = input_data.get("api_key")

            # Validate the API key first before saving
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.0-flash")
                _ = model.generate_content("Hello")  # Force real validation
                api_key_is_valid = True
            except Exception as e:
                print(f"API Key validation failed: {e}")
                api_key_is_valid = False

            if api_key_is_valid:
                # Save only if the key is valid
                env_path = os.path.join(os.path.dirname(__file__), ".env")
                with open(env_path, "w") as f:
                    f.write(f"GEMINI_API_KEY={api_key}")

            self.finish(json.dumps({"status": "success", "valid": api_key_is_valid}))

        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    message_pattern = url_path_join(base_url, "contentgen", "message")
    log_pattern = url_path_join(base_url, "contentgen", "log-usage")
    process_notebook_pattern = url_path_join(base_url, "contentgen", "process_notebook")
    check_api_key_pattern = url_path_join(base_url, "contentgen", "check-api-key")
    save_api_key_pattern = url_path_join(base_url, "contentgen", "save-api-key")

    handlers = [
        (message_pattern, MessageHandler),
        (log_pattern, LogUsageHandler),
        (process_notebook_pattern, ProcessNotebookHandler),
        (check_api_key_pattern, APIKeyCheckHandler),
        (save_api_key_pattern, SaveApiKeyHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
