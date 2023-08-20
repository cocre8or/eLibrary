# in process
import requests
import json



# server requests
def post_request(action, body, headerInfo):
    SERVER_NAME = 'localhost:5000/v1'
    request_url= 'http://{}/{}'.format(SERVER_NAME, action)
    request_headers =  headerInfo
    response = requests.post(
		url= request_url,
		data=json.dumps(body),
		headers = request_headers
	)
    response = json.loads(response.text)
    return response

def get_request(action, body, headerInfo):
    SERVER_NAME = 'localhost:5000/v1'
    request_url= 'http://{}/{}'.format(SERVER_NAME, action)
    request_headers =  headerInfo
    response = requests.get(
		url= request_url,
		data=json.dumps(body),
		headers = request_headers
	)
    response = json.loads(response.text)
    return response


def createAccount():
    username = input("Please enter username: ")
    password = input("Please enter password: ")
    email_address = input("Please enter email address: ")
    print(post_request('user',{}, {'Content-Type': 'application/json', 'username': username, 'password':password, 'email_address': email_address})[0]['token'])

def viewBooks():
    result = get_request('books',{},{})
    for book in result:
        print(book)
    

def login():
    username = input("Please enter username: ")
    password = input("Please enter password: ")
    token = input("Please enter token: ")
    print(post_request('login',{}, {'Content-Type': 'application/json', 'username': username, 'password':password, 'token': token}))

def checkout():
    bookTitle = input("Please enter bookTitle: ")
    cardId = input("Please enter cardId: ")
    token = input("Please enter token: ")
    print(post_request('checkout',{}, {'Content-Type': 'application/json', 'title': bookTitle, 'cardId':cardId, 'token': token}))

def checkin():
    bookTitle = input("Please enter bookTitle: ")
    cardId = input("Please enter cardId: ")
    token = input("Please enter token: ")
    print(post_request('checkin',{}, {'Content-Type': 'application/json', 'title': bookTitle, 'cardId':cardId, 'token': token}))

def createOptions():
    try:
        print("Please choose an option:")
        option = input("1. View book inventory\n2. Create an account \n3. Login \n4. Check out a book \n5. Check in a book\n6. Exit eLibrary\n")
        result = int(option)
        if result > 6 or result < 1:
            raise Exception("Invalid option selected")
        return result
    except:
        print("Invalid option selected, please choose an option between 1-6.")
        return 0

def options_loop():
	option = 0
	while True:
		if option == 0:
			option = createOptions()
		if option == 1:
			viewBooks()
			option = createOptions()
		if option == 2:
			createAccount()
			option = createOptions()
		if option == 3:
			login()
			option = createOptions()
		if option == 4:
			checkout()
			option = createOptions()
		if option == 5:
			checkin()
			option = createOptions()
		if option == 6:
			exit()

def main():
  while True:
    options_loop()
   
if __name__ == '__main__':
	main()