from .base_model import Base_Model

import logging
log = logging.getLogger(__name__)

"""
TODO: Dynamic context length limit from total context length left
TODO: Add ability to disable or enable filters on text
"""

class Mistral_OpenOrca(Base_Model):
    def __init__(self, config_path) -> None:
        super().__init__(config_path)


    def create_conversation(self, username, assistant_name, conversation_history) -> str:
        
        conversation = ''

        # Structure the conversation history into user to assistant messages
        for i, message in enumerate(conversation_history):
            if message['role'] == 'user':
                message = f'{username}:{message["text"]}'
                conversation += self.model_settings['template']['user'].replace("<CONV>", message)
            elif message['role'] == 'assistant':
                message = f'{assistant_name}:{message["text"]}'
                conversation += self.model_settings['template']['assistant'].replace("<CONV>", message)
            else:
                log.error(f"Error: Invalid role '{message['role']}'")
                
        conversation += self.model_settings['template']['next'] + f"\n{assistant_name}:"
        
        return conversation
    
    def truncate_conversation_history(self) -> list:
        removed_conversation = []
        for i, conv in enumerate(self.role.conversation_history[-self.model_settings["remove_length"]:]):
            removed_conversation.append(conv)
        self.role.conversation_history = self.role.conversation_history[-self.model_settings["remove_length"]:]
        return removed_conversation