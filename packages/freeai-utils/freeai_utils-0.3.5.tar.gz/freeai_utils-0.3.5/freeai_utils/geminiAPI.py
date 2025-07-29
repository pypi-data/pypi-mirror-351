import google.generativeai as genai #need pip install google-generativeai
import pyperclip #need pip install pyperclip
from dotenv import load_dotenv #need pip install python-dotenv
import os
import logging
from typing import Optional
from freeai_utils.log_set_up import setup_logging

class GeminiClient:
    def __init__(self, model_name : str ='models/gemini-2.0-flash-lite', api_key : Optional[str] = None, memories_length : int = 4, limit_word_per_respond : int = 150):
        #check data type
        self.__enforce_type(memories_length, int, "memories_length")
        self.__enforce_type(limit_word_per_respond, int, "limit_word_per_respond")
        
        env_path = os.path.join(os.getcwd(), ".env")
        load_dotenv(env_path) # load if there is env file
        self.__api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.__api_key:
            raise ValueError("API key was not provided or found in the 'GEMINI_API_KEY' environment variable.")
        
        #check data type before proceed further into connecting
        self.__enforce_type(model_name, str, "model_name")
        self.__enforce_type(self.__api_key, str, "api_key")
        
        #logging
        self.logger = setup_logging(self.__class__.__name__)
        
        try:
            genai.configure(api_key=self.__api_key)
            self.logger.info("Gemini API configured successfully.")
        except Exception as e:
            self.logger.critical(f"Error configuring Gemini API: {e}")
            raise

        self._model_name = model_name
        try:
            self._model = genai.GenerativeModel(self._model_name)
            self.logger.info(f"Successfully initialized model: {self._model_name}") 
            self.logger.info(f"Using endpoint: {self._model.model_name}") 
        except Exception as e:
            self.logger.critical(f"ERROR: Error initializing model {self._model_name}: {e}")
            raise
        
        self._history = []
        self._max_length = memories_length
        self._word_prompt = f"Please remember to answer with less than {limit_word_per_respond} words."
    
    @property
    def model_name(self):
        return self._model_name

    @property
    def gemini_model(self):
        return self._model

    @property
    def history(self):
        # Returns the conversation history as a tuple.
        return tuple(self._history)

    @property
    def max_memory_length(self):
        # Returns the maximum length of the conversation history.
        return self._max_length

    @property
    def word_prompt(self):
        # Returns the word limit prompt.
        return self._word_prompt

    @max_memory_length.setter
    def max_memory_length(self, value) -> None:
        # able to change the max_memory_length
        if isinstance(value, int) and value > 0:
            self._max_length = value
        else:
            raise ValueError("Memory length must be a positive integer.")
    
    def ask(self, prompt : str) -> str:
        #not str, return...
        self.__enforce_type(prompt, str, "prompt")
        
        if not prompt:
            self.logger.warning("WARNING: Empty prompt provided, skipping API call.")
            return None
        
        try:
            response = self._model.generate_content(self._word_prompt + prompt)

            if response.parts:
                answer = response.text
                self.logger.info("INFO: Received response successfully.") # Replaced logging.info
                return answer
            else:
                self.logger.info("No response received. This could be due to safety filters or other reasons.") 
                return ""

        except Exception as e:
            print(f"ERROR: An error occurred during the API call: {e}") # Replaced logging.error
            return None   
        
    def list_models(self) -> None:
        #List model available base on your api_key
        print("Retrieve available models...")
        try:
            print("-" * 40)
            for model in genai.list_models():
                # List model with 'generateContent' only
                if 'generateContent' in model.supported_generation_methods:
                    print(f"Model: {model.name}")
                    print(f"  Name: {model.display_name}")
                    print(f"  Description: {model.description}")
                    print("-" * 40)
        except Exception as e:
            self.logger.error(f"Error retrieving: {e}")
   
    def ask_and_copy_to_clipboard(self, prompt : str) -> str:
        answer = self.ask(prompt)
        if answer:
            try:
                pyperclip.copy(answer)
                self.logger.info("Copy to clipboard the answer")
            except Exception as e:
                self.logger.error(f"CANT COPY TO CLIPBOARD, {e}")
        return answer

    def ask_with_memories(self, prompt : str) -> str: # use if you want to store history to ask again (cap with memories_length)
        line = "Here's our previous conversation:\n"
        if self._history:
            for turn in self._history:
                line += f"User: {turn['question']}\nAI: {turn['answer']}\n"
        line += "Now, continue the conversation:\n"
        line += prompt
        answer = self.ask(line)
        self.__add_turn(prompt, answer)
        return answer
    
    def _clear_history(self) -> None:
        if self._history:
            self._history.clear()
    
    def __enforce_type(self, value, expected_type, arg_name):
        if not isinstance(value, expected_type):
            raise TypeError(f"Argument '{arg_name}' must be of type {expected_type.__name__}, but received {type(value).__name__}")
    
    def __add_turn(self, question, answer) -> None:
        self.__enforce_type(question, str, "question")
        self.__enforce_type(answer, str, answer)

        while len(self._history) >= self._max_length: #change from if to while because the memories could now be modified
            self._history.pop(0)  # Remove the oldest turn
        self._history.append({"question": question, "answer": answer})