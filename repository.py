# python -m pip install pymongo
import pymongo
import hashlib
import databaseconfig as cfg
import json
import datetime
import uuid
from bson.json_util import dumps

"""
Mongo DB
"""
class repository:
  def __init__(self):
    self.db_connection = cfg.dbConfig["connectionString"]
    self.createDb("eLibrary")
    self.createUserCollection("eLibrary.users")
    self.createELibraryBookCollection("eLibrary.books")
    self.seedTheDatabase()
    
  #region database set up
  def createDb(self, db_name):
    # establist a mongo db connection with default settings
    myclient = pymongo.MongoClient(self.db_connection)
    self.db_name = db_name
    # create a database
    self.myDb = myclient[self.db_name]
    return self.myDb
  
  def createUserCollection(self, collection):
    # create a collection
    self.eLibraryUsers = self.myDb[collection]
  
  def createELibraryBookCollection(self, collection):
    # create a collection
    self.eLibraryBooks = self.myDb[collection]
    
  def seedTheDatabase(self):
    if self.eLibraryBooks.count_documents({}) == 0:
      with open("seedDBBooks.json") as f:
        content = json.load(f)
        self.eLibraryBooks.insert_many(content)
  #endregion
  
  #region User transactions
  def createELibraryUserAccount(self, username, email_address, password):
    myquery = { "username": username }
    user = self.eLibraryUsers.find_one(myquery, {"_id": 0 })
    if user == None:
      return self.CreateUser(username, password, email_address)
    else:
      return None

  # Get a new session token, helper function
  def GetToken(self, pwd):
    try:

      # Adding the salt to password
      salt = str(uuid.uuid4())
      mix = str(pwd+salt)
      # Hashing the password
      hashedPwd = hashlib.md5(mix.encode()).hexdigest()
      
      # generate token
      token = uuid.uuid4().hex
      return (salt, hashedPwd, token)
    except:
      return ()
  
  # Create a user account
  def CreateUser(self, username, pwd, email_address):
    try:
      results = self.GetToken(pwd)
      if len(results) > 0:
        cardId = uuid.uuid4().hex
        date_format = "%Y-%m-%d %H:%M:%S"
        expiration = str((datetime.datetime.now() + datetime.timedelta(hours=12)).strftime(date_format))
        self.eLibraryUsers.insert_one({"cardId": cardId, "username":username, "email_address":email_address, "salt": results[0], "pwd": results[1], "token": results[2], "loginExpiration":expiration })
        result = self.eLibraryUsers.find_one({"token": results[2]}, {"_id": 0, "token": 1, "cardId": 1})
        return dumps(result)
      else:
        return {}
    except:
      raise Exception("Server error.")
  
  # Get a single user's information
  def GetUserInfo(self, username, token):
      try:
        query = { "username":username,"token": token }
        user = self.eLibraryUsers.find_one(query, {"_id": 0, "username": 1, "cardId":1, "token":1 })
        if user != None:
          return dumps(user)
        else:
          return {}
      except:
        raise Exception("Server error.")
  
  # Login 
  def LoginForNewToken(self, username, pwd):
    try:
      userInfo = self.eLibraryUsers.find_one({"username": username}, {"_id": 0})
      salt = userInfo["salt"]
      mix = str(pwd+salt)
      hashedPwd = hashlib.md5(mix.encode()).hexdigest()
      storedPwd = userInfo["pwd"]
      if storedPwd == hashedPwd:
        results = self.GetToken(pwd)
        if len(results) > 0:
          date_format = "%Y-%m-%d %H:%M:%S"
          expiration = str((datetime.datetime.now() + datetime.timedelta(hours=12)).strftime(date_format))
          query = { "username":username }
          newvalues = { "$set": { "salt": results[0], "pwd": results[1], "token": results[2], "loginExpiration":expiration } }
          self.eLibraryUsers.update_one(query, newvalues)
          result = self.eLibraryUsers.find_one({"token": results[2]},{"_id": 0})
          return dumps(result)
        else:
          return {}
      else:
        return {}
    except:
      raise Exception("Server error.")
  
  #endregion
  
  #region BOOK Transactions
  def viewBooks(self):
    books = {};
    books['books'] = self.eLibraryBooks.find({}, {"_id": 0});
    return dumps(books)
  
  # check out a book
  def checkOut(self, bookTitle, cardId):
    try:
      query = {"title": bookTitle, "checkedOut": 0}
      updates = {"$set": {"checkedOutBy": cardId, "checkedOut": 1, "lastCheckedOutDate": str((datetime.datetime.now()).strftime(" %Y-%m-%d %H:%M:%S")) }}
      alreadyCheckedOut = self.eLibraryBooks.find_one({"title": bookTitle, "checkedOut": 1}, {"_id": 0})
      if alreadyCheckedOut == None:
        self.eLibraryBooks.update_one(query, updates)
      else:
        return {}
      return dumps(self.eLibraryBooks.find_one({"title": bookTitle, "checkedOut": 1}, {"_id": 0}))
    except:
      raise Exception("Server error.")
  
  # check in a book
  def checkIn(self, bookTitle, cardId):
    try:
      query = {"title": bookTitle, "checkedOutBy": cardId, "checkedOut": 1}
      updates = {"$set": {"checkedOutBy": "", "checkedOut": 0 }}
      alreadyCheckedIn = self.eLibraryBooks.find_one({"title": bookTitle, "checkedOut": 0}, {"_id": 0})
      if alreadyCheckedIn == None:
        self.eLibraryBooks.update_one(query, updates)
      else:
        return {}
      return dumps(self.eLibraryBooks.find_one({"title": bookTitle}, {"_id": 0}))
    except:
      raise Exception("Server error.")
  
  #endregion
