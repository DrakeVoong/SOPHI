import datetime
import pandas as pd
import yaml

from modules.vectordb.conv_db import ConvDB
import logging

log = logging.getLogger(__name__)

class Base_Role:
    def __init__(self, username:str, assistant_name:str, role_config_path:str) -> None:
        self.username = username
        self.assistant_name = assistant_name
        self.role_config_path = role_config_path
        self.load_role_settings()
        
        try:
            with open(self.role_settings["prompt_path"], "r") as f:
                self.prompt_context = f.read()
                log.info(f"Prompt loaded from '{self.role_settings['prompt_path']}'")
        except FileNotFoundError:
            log.error(f"Error: Prompt file not found at '{self.role_settings['prompt_path']}'")
        except Exception as e:
            log.error(f"Error: {e}")
        
            
        self.conversation_history = []
        
        if self.role_settings["database_path"] is not None:
            log.info(f"Loading conversation database from '{self.role_settings['database_path']}'")
            self.conversation_db = ConvDB(self.role_settings["database_path"])
        else:
            log.warning("No conversation database path provided")
            self.conversation_db = None
            
    def load_prompt(self):
        try:
            with open(self.role_settings["prompt_path"], "r") as f:
                self.prompt_context = f.read()
                log.info(f"Prompt loaded from '{self.role_settings['prompt_path']}'")
        except FileNotFoundError:
            log.error(f"Error: Prompt file not found at '{self.role_settings['prompt_path']}'")
        except Exception as e:
            log.error(f"Error: {e}")
            
    def load_role_settings(self) -> dict:
        try:
            with open(self.role_config_path, 'r') as f:
                self.role_settings = yaml.load(f, Loader=yaml.FullLoader)
                log.info(f"Role settings loaded from '{self.role_config_path}'")
                return self.role_settings
        except FileNotFoundError:
            log.error(f"Error: Config file not found at '{self.role_config_path}'")
        except Exception as e:
            log.error(f"Error: {e}")