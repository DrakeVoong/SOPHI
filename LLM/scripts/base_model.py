from llama_cpp import Llama
from huggingface_hub import hf_hub_download
import yaml
import os
from dotenv import load_dotenv

import logging
log = logging.getLogger(__name__)

load_dotenv()
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')


class Base_Model():
    def __init__(self, config_path) -> None:
        self.config_path = config_path
        self.load_model_settings()

    def load_model_settings(self) -> None:
        try:
            with open(self.config_path, 'r') as f:
                self.model_settings = yaml.load(f, Loader=yaml.FullLoader)
                log.info(f"Model settings loaded from {self.config_path}")
        except FileNotFoundError:
            log.error(f"Model settings not found at {self.config_path}")
        except Exception as e:
            log.error(f"Error loading model settings: {e}")

    def search_file(self, start_path, target_file):
        for root, dirs, files in os.walk(start_path):
            if target_file in files:
                file_path = os.path.join(root, target_file)
                log.info(f"Model file {target_file} found at: {file_path}")
                return file_path
        
        log.warning(f"Model file {target_file} not found in {start_path}")
        return None
    
    def check_model(self) -> bool:
        directory = "LLM/models/"
        target_file_name = self.model_settings['model_file']
        
        file_path = self.search_file(directory, target_file_name)
        return file_path
    
    def download_model(self) -> None:
        log.warning(f"Downloading model from HuggingFace Hub")
        hf_hub_download(repo_id=self.model_settings['repo_id'],
                repo_type=self.model_settings['repo_type'],
                filename=self.model_settings['model_file'],
                cache_dir="LLM/models/",
                token=HUGGINGFACE_TOKEN
                )
        
    def create_model(self) -> Llama:
        model_path= self.check_model()
        if model_path is None:
            self.download_model()
            model_path = self.check_model()

            
        model = Llama(model_path=model_path, 
                    n_gpu_layers=self.model_settings['gpu_layers'],
                    n_ctx=self.model_settings['context_length'],
                    n_batch=self.model_settings['batch_size'],
                    n_threads=self.model_settings['threads'],
                    n_threads_batch=self.model_settings['threads_batch'],
                    rope_freq_scale=self.model_settings['rope_freq_scale'],
                    rope_freq_base=self.model_settings['rope_freq_base'],
                    verbose=True,
                    use_mlock=True
                    )
        
        log.info(f"Model created from '{model_path}'")
        return model
    
    
    def generate(self, prompt:str, model: Llama, role_settings: list) -> str:
        results = model.create_completion(prompt, 
                                        max_tokens=role_settings['max_new_tokens'],
                                        temperature=role_settings['temperature'],
                                        top_p=role_settings['top_p'],
                                        min_p=role_settings['min_p'],
                                        top_k=role_settings['top_k'],
                                        repeat_penalty=role_settings['repetition_penality'],
                                        stop=self.model_settings['template']['stop_tokens'],
                                        tfs_z=100,
                                        )
        
        generated_text = results['choices'][0]['text']
        in_tokens = results['usage']['prompt_tokens']
        out_tokens = results['usage']['completion_tokens']
        
        return generated_text, in_tokens, out_tokens