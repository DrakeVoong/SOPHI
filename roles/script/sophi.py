import datetime
from roles.script.base_role import Base_Role

import logging

log = logging.getLogger(__name__)

class Sophi(Base_Role):
    def __init__(self, username:str, assistant_name:str) -> None:
        super().__init__(username, assistant_name, "roles/settings/sophi.yaml")
        
    def get_memory(self, message: str) -> str:
        memory = ''
        closest_conversation = self.conversation_db.query(message)

        closest_conversation = closest_conversation[:5]
        for convo in closest_conversation:
            memory += f"`{convo}`\n"
        return memory
    
    def get_time(self) -> str:
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        time = datetime.datetime.now()
        weekday = weekday_names[datetime.date.today().weekday()]
        time = f'{time :%m/%d/%Y %H:%M} Day of the Week - {weekday}'
        return time
    
    def create_instruction(self, data: dict) -> str:
        
        message = data['message']
        memory = self.get_memory(message)
        time = self.get_time()
        #weather = self.get_weather()
        
        self.load_prompt()
        prompt = self.prompt_context
        prompt = prompt.replace("<MEMORY>", memory)
        prompt = prompt.replace("<DATETIME>", time)
        #prompt = prompt.replace("<WEATHER>", weather)
        
        return prompt