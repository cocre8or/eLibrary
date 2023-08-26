# main.py
# main controller
# https://pythonbasics.org/flask-rest-api/
# eLibrary Project with Login, Checkout, and Checking functionality. This functionality can be done via Postman and eventually
# a client application or more. The tech used is Mongo repo, Python and Flask, and an attached Postman collection.
from repository import *
from flask import Flask, request, Response, g
import sys
from functools import wraps
from validation import validation

# adding Mongorepo to the system path
sys.path.insert(0, "./mongorepo")

#flask --app hello run
app = Flask(__name__)
repo = repository()

@app.route("/ping",methods=["GET"])
def ping():
    return Response(response="Pong", status = 200)

@app.route("/health",methods=["GET"])
def health():
    return Response(response="healthy", status = 200)

'''
Create a user
Endpoint: v1/user
Request body keys: username, email_address, password
'''
@app.route("/v1/user", methods=["POST"])
def add_user():
  try:
    record = request.headers
    result = repo.createELibraryUserAccount(record["username"], record["email_address"], record["password"])
    if result == None:
      return Response(response="failed", status=400)
    else:
      return result
  except:
    return Response(response="Server error", status=500)
  
'''
Get user information
Endpoint: v1/user
Request body keys: token, username
'''
@app.route("/v1/user", methods=["GET"])
@validation(repo)
def get_user_info(): 
    try:
      return repo.GetUserInfo(request.json["username"], g.token)
    except:
      return Response(response="Server error", status=500)

'''
Endpoint: v1/login
Request body keys: token, username, password
'''
@app.route("/v1/login", methods=["POST"])
def login():
    try:
      username = request.json["username"]
      password = request.json["password"]
      return repo.LoginForNewToken(username, password)
    except:
      return Response(response="Server error", status=500)

'''
Get books information
Endpoint: v1/books
Request body keys: empty
'''
@app.route("/v1/books", methods=["GET"])
def get_books(): 
    try:
      return repo.viewBooks()
    except:
      return Response(response="No books...",status=400)
'''
Checkin a book
Endpoint: v1/checkin
Request body keys: token, bookTitle, cardId
'''
@app.route("/v1/checkin", methods=["POST"])
@validation(repo)
def checkin():
    try:
      book = repo.checkIn(request.json["bookTitle"], request.json["cardId"])
      if len(book) == 0:
        return Response(response="Already checked in.", status=400)
      else:
        return book
    except:
      return Response(response="Server error", status=500)

'''
Checkout a book
Endpoint: v1/checkout
Request body keys: token, bookTitle, cardId
'''
@app.route("/v1/checkout", methods=["POST"])
@validation(repo)
def checkout():
    try:
      title = request.json['bookTitle']
      cardId = request.json['cardId']
      book = repo.checkOut(title, cardId)
      if len(book) == 0:
        return Response(response="Already checked out.", status=400)
      else:
        return book
    except:
      return Response(response="Server error", status=500)


# Start up the server call
if __name__ == "__main__":
    app.run(host="localhost", port=5000,debug=True)
    