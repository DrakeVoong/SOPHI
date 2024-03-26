from modules.google_search.google_search import google_search
import inspect
import json


def get_function_info(function):
    """
    This function gets information about a function and returns it as a JSON dictionary.
    """
    function_info = {
    "type": "function",
    "function": {
        "name": function.__name__,
        "description": function.__doc__ or "",  # Handle missing docstrings
        "parameters": {}
    }
    }

    # Get function parameters using inspect
    params = inspect.signature(function).parameters
    function_info["function"]["parameters"] = {
    "type": "object",
    "properties": {},
    "required": []
    }

    for name, param in params.items():
        # Extract parameter information
        param_info = {
            "type": param.annotation.__name__ if param.annotation else "any"
        }
        function_info["function"]["parameters"]["properties"][name] = param_info

        # Add required parameters
        if param.default is inspect.Parameter.empty:
            function_info["function"]["parameters"]["required"].append(name)

    return function_info

def get_all_function_info_json(functions):
    """
    This function gets information about all functions in a list and returns a list of JSON dictionaries.
    """
    function_infos = []
    for function in functions:
        function_info = get_function_info(function)
        function_infos.append(function_info)
    return function_infos