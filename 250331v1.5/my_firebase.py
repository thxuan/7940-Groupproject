import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()
from firebase_admin import db
import firebase_admin
cred_obj = firebase_admin.credentials.Certificate('D:/Hk Baptist Sem2 HW/7940/Group-project/7940-Groupproject/250331v1.5/24436011test.json')

firebase_admin.initialize_app(cred_obj, {
	''
	})
ref = db.reference("Users")
global users_firebase
users_firebase = ref.get()
#Since data in fiebase is not in order,e.g user1,user11,user2
#Extracts from the 5th character to the end and transofrom them into int then sort them
#e.g user1 = int("1"),user11 = int("11")
users_firebase = dict(sorted(users_firebase.items(), key=lambda item: int(item[0][4:])))

class User:

    def match_similiar_users(self, user_keywords):
        scores = []
        for user_id, user_info in users_firebase.items():
            score = 0
            if user_keywords.get("Game","").lower() == user_info["Game"].lower():
                score += 1
            if user_keywords.get("VR","").lower() == user_info["VR"].lower():
                score += 1
            if user_keywords.get("Social","").lower() == user_info["Social"].lower():
                score += 1           
            if score > 0 :
                scores.append((user_info["Name"],score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_users = [name for name, score in scores[:3]] #find no more than three users
        return top_users if top_users else ["Can't find user with similiar interest"]

    def add_user(self,user_info):
        global users_firebase
        user_id = "user" + str(len(users_firebase) + 1)
        user_info = {user_id:user_info}
        ref.update(user_info)
        #update user_firebase after added a new user
        users_firebase = ref.get()
        users_firebase = dict(sorted(users_firebase.items(), key=lambda item: int(item[0][4:])))          

    def list_users(self):
        global users_firebase
        all_users = ""
        for user_id, user_info in users_firebase.items():
            all_users += f"{user_id}: {user_info}\n"
        return all_users
    
    def delete_user(self,name):
        global users_firebase
        delete_flag = 0
        for user_id, user_info in users_firebase.items():
            user_name = user_info["Name"]
            if user_name == name:
                ref.child(user_id).delete()
                delete_flag = 1
        if(delete_flag):
            #update user_firebase after delete a user
            users_firebase = ref.get()
            users_firebase = dict(sorted(users_firebase.items(), key=lambda item: int(item[0][4:])))        
            return ("Delete successfully!")
        else:
            return ("Can't find")   
           

users = User()