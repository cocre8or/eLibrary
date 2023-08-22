# in process
import requests
import json


class client:
    def __init__(self):
      self.SERVER_NAME = "localhost:5000/v1"
      self.TOKEN = ""
      self.CARDID = ""

    # server requests
    def post_request(self, action, body, headerInfo):
        request_url= "http://{}/{}".format(self.SERVER_NAME, action)
        response = requests.post(
            url= request_url,
            data=json.dumps(body),
            headers = headerInfo
        )
        response = json.loads(response.text)
        return response

    def get_request(self, action, body, headerInfo):
        request_url= "http://{}/{}".format(self.SERVER_NAME, action)
        response = requests.get(
            url= request_url,
            data=json.dumps(body),
            headers = headerInfo
        )
        response = json.loads(response.text)
        return response


    def createAccount(self):
        username = input("Please enter username: ")
        password = input("Please enter password: ")
        email_address = input("Please enter email address: ")
        result = self.post_request("user", {}, {"Content-Type": "application/json", "username": username, "password":password, "email_address": email_address})
        if len(result) > 0:
            self.TOKEN = result["token"]
            self.CARDID = result["cardId"]
        print("Token:"+self.TOKEN, "CardId:"+self.CARDID)

    def viewBooks(self):
        result = self.get_request("books",{})
        for book in result:
            print(book)
            
    def login(self):
        username = input("Please enter username: ")
        password = input("Please enter password: ")
        result = self.post_request("login",{"username": username, "password":password}, {"Content-Type": "application/json"})
        if len(result) > 0:
            self.TOKEN = result["token"]
            self.CARDID = result["cardId"]
        print("Token:"+self.TOKEN, "CardId:"+self.CARDID)

    def getUserInfo(self):
        username = input("Please enter username: ")
        result = self.get_request("user", {"username": username}, {"Content-Type": "application/json", "Authorization": self.TOKEN})
        if len(result) > 0:
            self.TOKEN = result["token"]
            self.CARDID = result["cardId"]
        print("Token:"+self.TOKEN, "CardId:"+self.CARDID)

    def checkout(self):
        bookTitle = input("Please enter bookTitle: ")
        result = self.post_request("checkout", {"bookTitle": bookTitle, "cardId":self.CARDID, "token": self.TOKEN}, {"Content-Type": "application/json"})
        print(result)

    def checkin(self):
        bookTitle = input("Please enter bookTitle: ")
        result = self.post_request("checkin", {"bookTitle": bookTitle, "cardId":self.CARDID, "token": self.TOKEN}, {"Content-Type": "application/json"})
        print(result)

    def createOptions(self):
        try:
            print("Please choose an option:")
            option = input("1. View book inventory\n2. Create an account \n3. Get My User Information \n4. Login \n5. Check out a book\n6. Check in a book\n7. Exit eLibrary\n")
            result = int(option)
            if result > 7 or result < 1:
                raise Exception("Invalid option selected")
            return result
        except:
            print("Invalid option selected, please choose an option between 1-6.")
            return 0

    def options_loop(self):
        option = 0
        while True:
          if option == 0:
            option = self.createOptions()
          if option == 1:
            self.viewBooks()
            option = self.createOptions()
          if option == 2:
            self.createAccount()
            option = self.createOptions()
          if option == 3:
            self.getUserInfo()
            option = self.createOptions()
          if option == 4:
            self.login()
            option = self.createOptions()
          if option == 5:
            self.checkout()
            option = self.createOptions()
          if option == 6:
            self.checkin()
            option = self.createOptions()
          if option == 7:
            exit()

    def main(self):
      while True:
        self.options_loop()
   
if __name__ == "__main__":
	client().main()