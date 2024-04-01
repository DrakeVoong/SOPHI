from flask import Flask, render_template, request, jsonify
from flask.logging import default_handler
import json
from llama_cpp import Llama
import time
import inspect
import re
import os

from LLM.scripts.mistral import Mistral_OpenOrca
from roles.script.sophi import Sophi
from roles.script.tool import Tool
from roles.script.helper_roles import Helper_Role
from agent import Agent

from modules.google_search.google_search import google_search

app = Flask(__name__,
            template_folder='interface/templates',
            static_folder='interface/static')

import logging


format = "[%(asctime).19s] | %(levelname)-9s | %(name)-30s | %(funcName)-20s | %(lineno)-3d | %(message)s"
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w", format=format)

log = logging.getLogger(__name__)

flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.INFO)
app.logger.disabled = False
flask_log.disabled = False

conversation_history = []

tool_functions = [google_search]

tool_function_status = False
helper_agent_status = False
helper_agent_chain = ''

username = None
assistant_name = None

role = None
helper_agent = None
tool = None
mistral = None
mistral_model = None
sophi_agent = None

def call_functions(tool_function, *args):
    for function in tool_functions:
        if function.__name__ == tool_function:
            function_params = inspect.signature(function).parameters
            
            if len(args) != len(function_params):
                log.error(f"Error: Incorrect number of arguments for function '{tool_function}'")
                return None
    
            return function(*args)
    return None

def chat_response(message):
    global tool_function_status
    global helper_agent_status
    global helper_agent_chain
    global helper_agent

    if tool_function_status:
        tool_message = sophi_agent.generate_response(message, tool, mistral, mistral_model)
        if not tool_message.startswith("None"):
            #convert str to json
            tool_call_pattern = r"<tool_call>(.*?)</tool_call>"
            matches = re.findall(tool_call_pattern, tool_message, flags=re.DOTALL)  # re.DOTALL makes the '.' match newlines
            match = matches[0].replace("'", '"')

            tool_message = json.loads(match)
            tool_function = tool_message['name']
            tool_args = tool_message['arguments']

            tool_value = []
            # Get every value in tool_args
            for key, value in tool_args.items():
                tool_value.append(value)

            # Run function
            tool_response = call_functions(tool_function, *tool_value)

            message = f"{message}\n\nInformation from tool functions:\n{tool_response}"


    if helper_agent_status and helper_agent_chain != '':
        helper_message = message
        phases = helper_agent_chain.split('\n')
        message += "\n\nThe following information is from various AI agents and not from the user."
        for phase in phases:
            if len(phase) == 0:
                continue
            helper_agent.change_role(f'roles/prompt/helper_roles/{phase}.txt')
            helper_message = sophi_agent.generate_response(helper_message, helper_agent, mistral, mistral_model)

            message += f"\nInformation from {phase} agent:\n\n{helper_message}"

    sophi_response = sophi_agent.generate_response(message, role, mistral, mistral_model)

    return sophi_response


@app.route('/')
def index():
    return render_template('index.html')

MODEL_SETTINGS_PATH = "LLM/settings/"

@app.route('/get_model_options')
def get_model_options():
    dir_list = os.listdir(MODEL_SETTINGS_PATH)
    dir_list.reverse()
    return jsonify({'options': dir_list})

ROLE_SETTINGS_PATH = "roles/settings/"

@app.route('/get_role_options')
def get_role_options():
    dir_list = os.listdir(ROLE_SETTINGS_PATH)
    dir_list.reverse()

    # Remove tool.yaml
    dir_list.remove('tool.yaml')

    return jsonify({'options': dir_list})

@app.route('/submit_model_selection', methods=['POST'])
def submit_model_selection():
    global mistral
    global mistral_model

    selected_model = request.form.get('value')

    mistral = None
    mistral_model = None

    mistral = Mistral_OpenOrca(MODEL_SETTINGS_PATH + selected_model)
    mistral_model = mistral.create_model()
    return jsonify({'text': 'Model selection successful!'})

@app.route('/submit_role_selection', methods=['POST'])
def submit_role_selection():
    global role
    global sophi_agent
    global username
    global assistant_name

    selected_role = request.form.get('value')
    username = request.form.get('username')
    assistant_name = request.form.get('assistant_name')

    role = None
    sophi_agent = None

    role = Sophi(username, assistant_name)
    sophi_agent = Agent()

    return jsonify({'text': 'Role selection successful!'})


@app.route('/check_agent_loaded', methods=['GET'])
def check_agent_loaded():
    if role is None or mistral is None or mistral_model is None or sophi_agent is None:
        return jsonify({'loaded': False})

    return jsonify({'loaded': True})

@app.route('/tool_function_status', methods=['POST'])
def on_tool_function_change():
    global tool_function_status
    global helper_agent_status
    global helper_agent_chain
    global helper_agent

    data = request.get_json()

    tool_function_status = data.get('isToolFunctionChecked')
    helper_agent_status = data.get('isHelperAgentsChecked')
    helper_agent_chain = data.get('helperAgentsChain')

    if helper_agent_status:
        helper_agent = Helper_Role('user', 'assistant')

    response = {'message': 'Data received successfully!'}
    return jsonify(response)

HELPER_AGENT_PATH = 'roles/prompt/helper_roles/'

@app.route('/get_helper_agents', methods=['GET', 'POST'])
def get_helper_agents():
    dir_list = os.listdir(HELPER_AGENT_PATH)
    dir_list = [agent.replace('.txt', '') for agent in dir_list]

    
    buttons_html = ""
    for agent in dir_list:
        button_html = f'<button name="{agent}" onclick="callHelperAgent(\'{agent}\')">{agent}</button>'
        buttons_html += button_html

    return jsonify({'helper_agents': buttons_html})

@app.route('/unload_model')
def unload_model():
    global mistral
    global mistral_model

    mistral = None
    mistral_model = None

    return jsonify({'text': 'Model unloaded successfully!'})

@app.route('/process_message', methods=['POST'])
def process_message():
    message = request.form['message']

    response = chat_response(message)

    response = response.replace('\n', '<br>')

    user_message = f"<div class='user-message'>You: {message}</div>"
    bot_message = f"<div class='bot-message'>Sophi: {response}</div>"

    conversation_history.append(user_message)
    conversation_history.append(bot_message)

    response = {'messages': conversation_history}
    return json.dumps(response)

if __name__ == '__main__':
    print("Starting Flask server...on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)