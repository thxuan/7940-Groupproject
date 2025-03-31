import configparser
import requests
import pathlib
import json
import ast

from my_firebase import users


class HKBU_ChatGPT():

    def __init__(self,config=None):
        if config is None:
            current_dir = pathlib.Path(__file__).parent
            config = current_dir / "config.ini"
        if isinstance(config, str):
            self.config = configparser.ConfigParser()
            self.config.read(config)
        elif isinstance(config, configparser.ConfigParser):
            self.config = config
        self.state = "intro"
        self.last_keyword = None
        self.chat_history = []


    def call_chatgpt(self, messages):
        url = (self.config['CHATGPT']['BASICURL']) +\
              "/deployments/" + (self.config['CHATGPT']['MODELNAME']) +\
              "/chat/completions/?api-version=" +\
              (self.config['CHATGPT']['APIVERSION'])

        headers = {
            'Content-Type': 'application/json',
            'api-key': (self.config['CHATGPT']['ACCESS_TOKEN'])
        }

        payload = {'messages': messages}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            return 'Error:', response.text


    def extract_keywords(self, user_input):
        conversation = [
            {"role": "system", 
             "content": "You are an interest extraction assistant.\
              Please extract the following three types of keywords\
                    from the user input:\
              Game, VR experience (VR), Social platform (Social). \
                    Output in JSON format\
e.g. {\"Game\": \"Elden Ring\", \"VR\": \"Beat Saber\", \"Social\": \"Discord\"}  "
            },
            {"role": "user", "content": user_input}
        ]        
        response = self.call_chatgpt(conversation)
        try:
            keywords = json.loads(response)
            return keywords
        except Exception as e:
            return {}
   

    def detect_intent(self, user_input):
        conversation = [
            {"role": "system",
              "content": "Please determine the user's intent from this text. \
                If the user is describing their interests in Online Game\
                    (e.g basket is not online game,but online basket ball is) or \
                    VR experience or Social media, reply only 'interest'.\
                    If the user is asking about your functions or other things, \
                        reply only 'intro'.Do not explain."},                          
            {"role": "user", "content": user_input}
        ]
        reply = self.call_chatgpt(conversation).strip().lower()
        return reply if reply in ["intro", "interest"] else "unknown"


#This method is for command /add,extract user name and interests in user input
    def config_user(self, user_input):
        conversation = [
            {"role": "system",
              "content": "Please extract the following four types of keywords \
                    from the user input:\
               Name, Game, VR experience (VR), Social platform (Social). \
                    Output in the following format\
    e.g. {'Name':'Leon','Game':'Elden Ring','VR':'Beat Saber','Social':'Discord'} "},
            {"role": "user", "content": user_input}
        ]
        response = self.call_chatgpt(conversation)
        response_dict = ast.literal_eval(response) #Transofrm String into dictionary
        try:
            users.add_user(response_dict)
            return response_dict
        except Exception as e:
            return {}


    def submit(self,message):
        if self.state == "intro":
            intent = self.detect_intent(message)
            if intent == "intro":              
                return ("Hello! I can help you with these two things:\n"
                        " 1.Recommend online activities, communities,or platforms based on your interests\n"
                        " 2.Match you with users who share similar interests\n"
                        " Please tell me about your favorite games, VR experiences, or commonly used social platforms")
            elif intent == "interest":
                keywords = self.extract_keywords(message)
                if not keywords:
                    return "Unable to recognize interest keywords. Please provide a clearer description of your interests."
                self.last_keywords = keywords
                self.state = "awaiting_choice"
                return (f"I extracted the following interest keywords from your input:\n{json.dumps(keywords, ensure_ascii=False)}\n\n"
                        "Would you like 1. to match with people of similar interests or 2. get online activity recommendations? \n\n"
                        "Please enter 1 or 2")                
        
        elif self.state == "awaiting_choice":
            if message.strip() == '1':
                matched_users = users.match_similiar_users(self.last_keywords)
                self.state = "intro"
                return "Users with similar interests include:\n" + "\n".join(matched_users)
            else:
                self.state = "conversation"        
                conversation = [
                    {"role": "system", 
                        "content": "You are a virtual event expert. Your tasks are:\
                        1. Extract interest keywords from user input \
                            (e.g., game names, VR experiences, social groups)\
                        2. Recommend relevant online activities, communities, \
                            or similar games based on the keywords\
                        3. Return suggestions in natural language, \
                            e.g., 'You can join this Discord server: [link]'\
                        4. If no specific link is available, provide general advice\
                        5. Tell people they can continue conversation if they like\
                            or they can use 'quit' to restart  a conversation."
                    },
                    {"role": "user", "content": json.dumps(self.last_keywords, ensure_ascii=False)}
                ]
                reply = self.call_chatgpt(conversation)
                self.chat_history.append({"role": "assistant", "content": reply})#use assistant add conversation to history
                return reply
            
        elif self.state == "conversation":
            if message.lower().strip() == "quit":
                self.state = "intro"
                self.chat_history = []
                self.last_keywords = None
                return "You can start a new question. \
                        Please tell me about your interests!"
            else:
                self.chat_history.append({"role": "user", "content": message})#add to history
                reply = self.call_chatgpt(self.chat_history)#send all conversation include history to GPT
                self.chat_history.append({"role": "assistant", "content": reply})
                return reply                
            
        
if __name__ == '__main__':
    ChatGPT_test = HKBU_ChatGPT()

    while True:
        user_input = input("Typing anything to ChatGPT:\t")
        response = ChatGPT_test.submit(user_input)
        print(response)
