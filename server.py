# server.py
# https://pythonbasics.org/flask-rest-api/
# eLibrary Project with Login, Checkout, and Checking functionality. This functionality can be done via Postman and eventually
# a client application or more. The tech used is Mongo DB, Python and Flask, and an attached Postman collection.
import json
from DBContext import *
from flask import Flask, jsonify, request
import sys

# adding MongoDB to the system path
sys.path.insert(0, './mongoDB')

#flask --app hello run
app = Flask(__name__)
db = DBContext()

@app.route('/ping',methods=['GET'])
def ping():
    return 'Pong'

@app.route('/health',methods=['GET'])
def health():
    return 'Todo'

# create a user
@app.route('/v1/user', methods=['POST'])
def add_user():
  try:
    record = request.headers
    result = db.createELibraryUserAccount(record['username'], record['email_address'], record['password'])
    if result == None:
      return jsonify({'result': 'failed'})
    else:
      return jsonify({'result':json.loads(result)[0]['token']})
  except:
    return jsonify({'result': 'Failed'})
  
#get user info
@app.route('/v1/user', methods=['GET'])
def get_user_info(): 
    try:
      token  = request.form.get('token')
      if db.Validate(token):
        return db.GetUserInfo(request.form.get('username'), token)
      else:
        return jsonify({'result':'Session expired'})
    except:
      return jsonify({'result':'Session expired'})

# login
@app.route('/v1/login', methods=['POST'])
def login():
    try:
      token  = request.form.get('token')
      if db.Validate(token):
        return db.LoginForNewToken(request.form.get('username'), request.form.get('password'), token)
      else:
        return jsonify({'result':'Bad Request'})
    except:
      return jsonify({'result':'Bad Request'})

@app.route('/v1/books', methods=['GET'])
def get_books(): 
    try:
      return jsonify({'result': db.viewBooks()})
    except:
      return jsonify({'result':'No books...'})
    
@app.route('/v1/checkin', methods=['POST'])
def checkin():
    try:
      if db.Validate(request.form.get('token')):
        return db.checkIn(request.form.get('bookTitle'), request.form.get('cardId'))
      else:
        return jsonify({'result':'Unsuccessful'})
    except:
      return jsonify({'result':'Unsuccessful'})
    
@app.route('/v1/checkout', methods=['POST'])
def checkout(): 
    try:
      if db.Validate(request.form.get('token')):
        return jsonify({'result':db.checkOut(request.form.get('bookTitle'), request.form.get('cardId'))})
      else:
        return jsonify({'result':'Unsuccessful'})
    except:
      return jsonify({'result':'Unsuccessful'})

if __name__ == '__main__':
    app.run(host='localhost', port=5000,debug=True)
    