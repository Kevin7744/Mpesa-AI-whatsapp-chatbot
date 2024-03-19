"""Wrapper class for open AI API bot which accesses information from airtable"""
from config import Config
from openai import OpenAI

import tiktoken
import datetime
from dateparser import parse
import requests




MEMORY_SIZE = 30 #number of previous messages to store


class AIBot:
    def __init__(self):
        self.memory = ''
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
            
        #measure the number of tokens in memory to avoid exceeding context length
        self.encoder = tiktoken.get_encoding('cl100k_base')
        self.max_memory_tokens = 4000
        
    
    def list_to_string(self, lst):
        output = '['
        
        for el in lst:
            output += f'"{el}"'
            
            if el != lst[-1]:
                output += ", "
        
        output += ']'
        return output
        
            
    def add_memory(self, data, isUser):
        """
        Store last message in memory 

        Args:
            data (str): message
            isUser (bool): true if user sent the last message, false otherwise
        """
        if isUser:
            self.memory += f'USER: {data}'
        else:
            self.memory += f'BOT: {data}'
        
        #ensure that the number of tokens in memory never exceeds the maximum context length
        tokens = self.encoder.encode(self.memory)
        self.memory = self.encoder.decode(tokens[-self.max_memory_tokens:])
    

      
    def chit_chat_fn(self, message):
        """Function to handle normal human interaction workflow

        Args:
            message (string): The message sent by the user

        Returns:
            String: The response from the bot
        """

        #general chat abilities using memory from the conversation
        completions = self.client.chat.completions.create(
            messages=[
                    {
                        'role': 'system', 
                        'content': f'''
                                        You are a helpful and smart internal assistant for a business called {Config.BUSINESS_NAME}
                                        Your goal is to help the people in the business manage inventory and their schedules. 
                                        You should also talk to the users like a human and answer any general questions that they have. 
                                        If the user wants to end the conversation say goodbye in a formal manner.
                                        You must remember that you are capable of accessing the inventory and the invoices of the business. 
                                        
                                        Here is a transcript of the conversation with the user up to now:
                                        ```{self.memory}```
                                        Reply to the user's message appropriately, using the transcript to get the context.
                                    '''    
                    }, 
                    {
                        'role': 'user', 
                        'content': message
                    }
            ], 
            model='gpt-4-0125-preview', 
            temperature=0.3
        )
        
        return completions.choices[0].message.content
    
        
    def classify_intent(self, message):
        """Function used to classify the user's intent based on the message, to decide the correct worflow

        Args:
            message (string): The message sent by the user

        Returns:
            string: The response from the bot
        """


        completions = self.client.chat.completions.create(
            messages=[
                {
                    'role': 'system', 
                    'content': f'''
                                As a dedicated assistant, you are here to assist with any inquiries.

                                Start by asking: "How can I assist you today?"

                                Based on the user's input, categorize their request into one of the following:

                                Respond with the corresponding category number only.

                                Context:
                                {';'.join(self.memory)}
                                '''      
                }, 
                {
                    'role': 'user', 
                    'content': message
                }
            ], 
            model='gpt-4-0125-preview', 
            temperature=0
        )
        
        response = completions.choices[0].message.content
        
        #try to parse integer from response
        #if output is not valid, default with 5 (other)
        try:
            choice = int(response.replace(')', ''))
        except Exception as e:
            print(f'Classification output parsing error: {e}')
            choice = 5
            
        return choice
      

    def handle_message(self, message):
        """Function to generate the bot's response to a given message. 
           This function starts by adding the user's message to the memory, then calls the correct workflow function and
           finally stores the bot's response in memory

        Args:
            message (string): The message received by the user

        Returns:
            string: the response generated by the bot
        """
        
        #special command to clear memory
        if message == 'CLEAR MEMORY':
            self.memory = ''
            return 'OK, I just cleared my memory'
        
        
        self.add_memory(message, True) #add the new message from the user to memory
        
        #get the function to excute based on the intent
        intent_to_function = [
                              self.chit_chat_fn,
                             ]        
        response = ''        
        intent = self.classify_intent(message)

        #get function to execute from the intent number, which gets mapped to a bot state
        fn = intent_to_function[intent - 1]
        response = fn(message)
        
        self.add_memory(response, False)
        
        return response
            
        
        
            
if __name__ == '__main__':
    bot = AIBot()
    
    while True:
        msg = input('User: ')
        print(f'BOT: {bot.handle_message(msg)}')