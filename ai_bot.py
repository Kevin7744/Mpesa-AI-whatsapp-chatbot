# """Wrapper class for open AI API bot which accesses information from airtable"""
# from config import Config
# from openai import OpenAI

# import tiktoken
# import datetime
# from dateparser import parse
# import requests




# MEMORY_SIZE = 30 #number of previous messages to store


# class AIBot:
#     def __init__(self):
#         self.memory = ''
#         self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
            
#         #measure the number of tokens in memory to avoid exceeding context length
#         self.encoder = tiktoken.get_encoding('cl100k_base')
#         self.max_memory_tokens = 4000
        
    
#     def list_to_string(self, lst):
#         output = '['
        
#         for el in lst:
#             output += f'"{el}"'
            
#             if el != lst[-1]:
#                 output += ", "
        
#         output += ']'
#         return output
        
            
#     def add_memory(self, data, isUser):
#         """
#         Store last message in memory 

#         Args:
#             data (str): message
#             isUser (bool): true if user sent the last message, false otherwise
#         """
#         if isUser:
#             self.memory += f'USER: {data}'
#         else:
#             self.memory += f'BOT: {data}'
        
#         #ensure that the number of tokens in memory never exceeds the maximum context length
#         tokens = self.encoder.encode(self.memory)
#         self.memory = self.encoder.decode(tokens[-self.max_memory_tokens:])
    

      
#     def chit_chat_fn(self, message):
#         """Function to handle normal human interaction workflow

#         Args:
#             message (string): The message sent by the user

#         Returns:
#             String: The response from the bot
#         """

#         #general chat abilities using memory from the conversation
#         completions = self.client.chat.completions.create(
#             messages=[
#                     {
#                         'role': 'system', 
#                         'content': f'''
#                                         You are a helpful assistant
#                                         Replying to users queries in joking and funny way but also helping them
#                                         Include emojis in you replies

#                                         You are fluent on speaking modern sheng.

#                                         Here is a transcript of the conversation with the user up to now:
#                                         ```{self.memory}```
#                                         Reply to the user's message appropriately, using the transcript to get the context.
#                                     '''    
#                     }, 
#                     {
#                         'role': 'user', 
#                         'content': message
#                     }
#             ], 
#             model='gpt-4-0125-preview', 
#             temperature=0.3
#         )
        
#         return completions.choices[0].message.content
    
#     def mpesa_payments_fn(self, message):
#         """Function to handle questions from the conversation related to mpesa payemnts and initiate transaction on behalf of the user
        
#         Args:
#             message (string): The message containing the answers from the user

#         Returns:
#             String: The response from the bot
#         """
#         completions = self.client.chat.completions.create(
#             messages=[
#                 {
#                     'role': 'system',
#                     'content': f'''
#                                 You are a helpful assistant, specializing in cleaning services. Your task is to assist users by understanding their cleaning needs through a series of questions and capturing their responses for services such as one-time cleaning, regular cleaning, post-construction cleaning, window washing, carpet cleaning, and sofa cleaning. 

#                                 For each service request, you will ask the following questions to gather the necessary details:

#                                 One-Time Cleaning:
#                                 1. Which standard cleaning tasks do you require?
#                                 2. What is the total square footage (m²) of the space that needs to be cleaned?
#                                 3. Are there specific spots or details that need extra attention?
#                                 4. Are there specific cleaning products we should use, for instance, for a certain type of floor?
#                                 5. Do you also wish the windows to be washed?

#                                 Regular Cleaning:
#                                 1. Desired cleaning frequency
#                                 2. How often per week do you want cleaning to be done?
#                                 3. What is the total square footage (m²) of the space that needs to be cleaned?
#                                 4. What standard cleaning tasks do you expect from us?
#                                 5. Are there specific focus points or additional tasks you want to be executed?

#                                 Post-Construction Cleaning:
#                                 1. Which standard cleaning tasks do you require?
#                                 2. What is the current condition of the spaces?
#                                 3. Are there specific spots or details that need extra attention?
#                                 4. What is the total square footage (m²) of the space that needs to be cleaned?
#                                 5. Are there specific cleaning products we should use, for instance, for a certain type of floor?
#                                 6. Are there any traces of cement grout haze?

#                                 Window Washing:
#                                 1. What is the total square footage (m²) of the space that needs to be cleaned?
#                                 2. How many windows approximately need to be washed?
#                                 3. How dirty are the windows currently?
#                                 4. Are they mostly large or small windows?
#                                 5. Are there specific cleaning products we should use for the windows?

#                                 Carpet Cleaning:
#                                 1. What is the width of the carpet you want to be cleaned? (in meters)
#                                 2. What is the length of the carpet you want to be cleaned? (in meters)
#                                 3. If you wish to have multiple carpets cleaned, please specify the total number of carpets to be cleaned here.
#                                 4. If you have multiple carpets with different dimensions that need cleaning, please specify the dimensions of each carpet here.

#                                 Sofa Cleaning:
#                                 1. How many sofas do you want to be cleaned?
#                                 2. How many seating places do the sofa(s) you want to be cleaned have?
#                                 3. If you have multiple sofas with different seating arrangements to be cleaned, please specify the details of each sofa here.
#                                 4. Is it a corner sofa?

#                                 Based on the user's responses, capture the necessary details like full name, phone, email, street name, zip code, city, service_type and other cleaning service details. Use the function to save these details and respond to the user confirming the capture of their cleaning service request.
                                
#                                 Here is more infomation about our cleaning service business. Use where necessary.

#                                 Here is a transcript of the conversation with the user up to now:
#                                 ```{self.memory}```
#                                 Reply to the user's message appropriately, using the transcript to get the context and when saving the user's information.                                
#                                 '''
#                     },
#                 {
#                     'role': 'user', 
#                     'content': message
#                 }
#             ], 
#             model='gpt-4-0125-preview', 
#             temperature=0
#         )

#         response = completions.choices[0].message.content

#         return response  

#     def classify_intent(self, message):
#         """Function used to classify the user's intent based on the message, to decide the correct worflow

#         Args:
#             message (string): The message sent by the user

#         Returns:
#             string: The response from the bot
#         """


#         completions = self.client.chat.completions.create(
#             messages=[
#                 {
#                     'role': 'system', 
#                     'content': f'''
#                                 As a dedicated assistant, fluent in modern sheng.

#                                 Start by asking: "Rada buda?"

#                                 You have access to different tools that are capable of different functionalaties

#                                 Based on the user's input, categorize their request into one of the following:

#                                 1) When the user just want to have a chitchat
#                                 2) When the user wants to make a payment to a till number, paybill or send money
#                                 3) When the user asks questions that need searching the web

#                                 Respond with the corresponding category number only.

#                                 Context:
#                                 {';'.join(self.memory)}
#                                 '''      
#                 }, 
#                 {
#                     'role': 'user', 
#                     'content': message
#                 }
#             ], 
#             model='gpt-4-0125-preview', 
#             temperature=0
#         )
        
#         response = completions.choices[0].message.content
        
#         #try to parse integer from response
#         #if output is not valid, default with 5 (other)
#         try:
#             choice = int(response.replace(')', ''))
#         except Exception as e:
#             print(f'Classification output parsing error: {e}')
#             choice = 5
            
#         return choice
      

#     def handle_message(self, message):
#         """Function to generate the bot's response to a given message. 
#            This function starts by adding the user's message to the memory, then calls the correct workflow function and
#            finally stores the bot's response in memory

#         Args:
#             message (string): The message received by the user

#         Returns:
#             string: the response generated by the bot
#         """
        
#         #special command to clear memory
#         if message == 'CLEAR MEMORY':
#             self.memory = ''
#             return 'OK, I just cleared my memory'
        
        
#         self.add_memory(message, True) #add the new message from the user to memory
        
#         #get the function to excute based on the intent
#         intent_to_function = [
#                               self.chit_chat_fn,
#                               self.mpesa_payments_fn
#                              ]        
#         response = ''        
#         intent = self.classify_intent(message)

#         #get function to execute from the intent number, which gets mapped to a bot state
#         fn = intent_to_function[intent - 1]
#         response = fn(message)
        
#         self.add_memory(response, False)
        
#         return response
            
        
        
            
# if __name__ == '__main__':
#     bot = AIBot()
    
#     while True:
#         msg = input('User: ')
#         print(f'BOT: {bot.handle_message(msg)}')