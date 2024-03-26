from roles.script.base_role import Base_Role

import logging

log = logging.getLogger(__name__)

class Helper_Role(Base_Role):
    def __init__(self, username:str, assistant_name:str) -> None:
        super().__init__(username, assistant_name, "roles/settings/helper.yaml")

    def change_role(self, role_instruction_path:str) -> None:
        with open(role_instruction_path, 'r') as f:
            self.prompt_context = f.read()

    def create_instruction(self, data: dict) -> str:
        prompt = self.prompt_context
        return prompt