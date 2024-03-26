import datetime
import time
from uuid import uuid4
import re
import emoji

import logging
log = logging.getLogger(__name__)

class Agent():
    def __init__(self) -> None:
        pass
    
    def build_message_metadata(self, message:str, role:str, name:str) -> dict:
        timestamp = datetime.datetime.now()
        timestamp = f"{timestamp :%m/%d/%Y %H:%M}"
        uuid = str(uuid4())
        metadata = {
            "uuid4": uuid,
            "role": role,
            "name": name,
            "text": message,
            "time": timestamp
        }
        return metadata
    
    def clean_response(self, response: str) -> str:
        # Remove emojis using the emoji library
        generated_text = emoji.demojize(response)
        
        # Remove any remaining emoji characters or sequences
        generated_text = re.sub(r':[a-zA-Z0-9_]+:', '', response)

        # Remove extra token and newlines
        generated_text = generated_text.split('<|im_end|>')[0]

        if generated_text.startswith('\n '):
            generated_text = generated_text[2:]

        if generated_text.startswith(' '):
            generated_text = generated_text[1:]

        return generated_text
    
    def truncate_conversation_history(self, role, model) -> list:
        removed_conversation = []
        for i, conv in enumerate(role.conversation_history[-model.model_settings["remove_length"]:]):
            removed_conversation.append(conv)
        role.conversation_history = role.conversation_history[-model.model_settings["remove_length"]:]
        return removed_conversation

    def generate_response(self, message:str, role, model, LLM_model) -> str:

        message_metadata = self.build_message_metadata(message, 'user', role.username)
        role.conversation_history.append(message_metadata)

        instruction = role.create_instruction({'message': message})
        prompt = model.create_conversation(instruction, role.username, role.assistant_name, role.conversation_history)

        start = time.time()
        response, in_tokens, out_tokens = model.generate(prompt, LLM_model, role.role_settings)
        end = time.time()
        time_len = end - start

        response = self.clean_response(response)

        response_metadata = self.build_message_metadata(response, 'assistant', role.assistant_name)
        role.conversation_history.append(response_metadata)

        #role.conversation_db.add(message_metadata)
        #role.conversation_db.add(response_metadata)

        if len(role.conversation_history) > 250 or in_tokens+out_tokens > model.model_settings["context_length"]*0.9:
            removed_conversation = self.truncate_conversation_history(role, model)
            

        log.info(f"Response Generated - Token Length: {in_tokens+out_tokens} - Response Time: {time_len:.2f} - Tk/s: {(out_tokens)/(time_len):.2f} - In: {in_tokens} - Out: {out_tokens}")
        return response




