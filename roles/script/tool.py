from roles.script.base_role import Base_Role

import json
from tool_convert import get_all_function_info_json

class Tool(Base_Role):
    def __init__(self, username:str, assistant_name:str, functions) -> None:
        super().__init__(username, assistant_name, "roles/settings/tool.yaml")
        self.functions = functions

    def get_tools(self) -> str:
        tools = get_all_function_info_json(self.functions)
        tools_instruct = json.dumps(tools, indent=4)
        return tools_instruct

    def create_instruction(self, data: dict) -> str:
        message = data['message']
        tools = self.get_tools()

        self.load_prompt()
        prompt = self.prompt_context

        prompt = prompt.replace("<FUNCTIONS>", tools)

        return prompt