# """Wrapper class for open AI API bot which accesses information from airtable"""
# from config import Config
# from openai import OpenAI

# import tiktoken
# import datetime
# from dateparser import parse
# import requests

# from agent_tools.Mpesa.till_payment import process_till_payment

# MEMORY_SIZE = 30 #number of previous messages to store


# class AIBot:
#     def __init__(self):
#         self.memory = ''
#         self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
            
#         #measure the number of tokens in memory to avoid exceeding context length
#         self.encoder = tiktoken.get_encoding('cl100k_base')
#         self.max_memory_tokens = 4000
#         self.process_till_payment = process_till_payment
        
    
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
#                                 You are a helpful assistant capable of initiating MPESA transactions.
#                                 You are capable of initiating transactions to paybill, till number and send money to individual accounts

#                                 Your goal is to identify and extract key information needed for the payment

#                                 For till payments make sure the user provides the following:
#                                 1) The amount the user wants to send.
#                                 2) The phone number of the user making the payment. This can be also {Config.RECIPIENT_WAID} which is represented as party_a
#                                 3) The amount the user wants to send
#                                 4) The till number the user sends money to which is represented as the business_short_code

#                                 Example:
#                                     -> User input: "nadai kutuma 100 kwa hii till 174379"
#                                         Extracted information:
#                                             - amount: 100
#                                             - business_short_code: 174379
#                                             - party_a: {Config.RECIPIENT_WAID}
#                                             - transaction_type: CustomerBuyGoodsOnline [default value for Till payment transactions]
#                                             - account_reference: Till [default value for CustomerBuyGoodsOnline transactions]

#                                             Output the extracted information in the following order
#                                             TILL:[amount], [business_short_code], [party_a], [transaction_type], [account_reference] 
                                            

#                                 NOTE: Make sure to ask the user to provide any missing values


#                                 Here is a transcript of the conversation with the user up to now:
#                                 ```{self.memory}```
#                                 Reply to the user's message appropriately, using the transcript to get the context and when saving the user's information.                                
#                                 '''
#                     },
#                     {
#                         'role': 'user', 
#                         'content': message
#                     }
#             ], 
#             model='gpt-4-0125-preview', 
#             temperature=0,
#         )

#         response = completions.choices[0].message.content

#         # agent has issued TILL command which indicates a till payment
#         if response.startswith('TILL'):
#             _, amount, business_short_code, party_a, transaction_type, account_reference = response.split(',')
            
#             # Assume process_till_payment is a function that handles the till payment logic.
#             # You need to implement this function based on your specific requirements.
#             result = self.process_till_payment(
#                 amount=float(amount.strip()), 
#                 business_short_code=business_short_code.strip(), 
#                 party_a=party_a.strip(), 
#                 transaction_type=transaction_type.strip(), 
#                 account_reference=account_reference.strip()
#             )

#             return f"Till payment initiated successfully for {business_short_code.strip()}. {result}"

#         # Future extension for PAYBILL and SEND_MONEY can follow a similar pattern
#         elif response.startswith('PAYBILL'):
#             # Extract necessary information and call corresponding function
#             pass

#         elif response.startswith('SEND_MONEY'):
#             # Extract necessary information and call corresponding function
#             pass

#         else:
#             return response

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