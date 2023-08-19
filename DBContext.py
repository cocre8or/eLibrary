# python -m pip install pymongo
import pymongo
import bcrypt
import databaseconfig as cfg
import json
import datetime
import uuid
from bson.json_util import dumps

'''
Mongo DB
'''
class DBContext:
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
      with open('seedDBBooks.json') as f:
        content = json.load(f)
        self.eLibraryBooks.insert_many(content)
  #endregion
  
  #region User Login transactions
  def createELibraryUserAccount(self, username, email_address, password):
    myquery = { "username": username }
    mydoc = self.eLibraryUsers.find(myquery)
    result = list(mydoc)
    if len(result) == 0:
      return self.CreateUser(username, password, email_address)
    else:
      return None

  def Validate(self, token):
    try:
      query = {"token": token }
      for user in self.eLibraryUsers.find(query, {"_id": 0, "username": 1, "salt":1, "pwd":1,"loginExpiration":1 }):
        date_format = '%Y-%m-%d %H:%M:%S'
        date_of_expiration_str = str(datetime.datetime.strptime(user['loginExpiration'], date_format))
        date_of_expiration = datetime.datetime.strptime(date_of_expiration_str, date_format)
        if date_of_expiration > datetime.datetime.now():
          return True 
    except:
      return False
  
  def GetToken(self, pwd):
    try:
      # Declaring our password
      password = bytes(pwd, 'utf-8')
      # Adding the salt to password
      salt = bcrypt.gensalt()
      # Hashing the password
      hashedPwd = bcrypt.hashpw(password, salt)
      
      # generate token
      token = uuid.uuid4().hex
      return (salt, hashedPwd, token)
    except:
      return ()
  
  def CreateUser(self, username, pwd, email_address):
    try:
      results = self.GetToken(pwd)
      if len(results) > 0:
        cardId = uuid.uuid4().hex
        expiration = str( (datetime.datetime.now() + datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S") )
        self.eLibraryUsers.insert_one({'cardId': cardId, 'username':username, 'email_address':email_address, 'salt': results[0], 'pwd': results[1], 'token': results[2], 'loginExpiration':expiration })
        mydoc = self.eLibraryUsers.find({'token': results[2]}, {"_id": 0, 'token': 1})
        result = list(mydoc)
        return dumps(result).replace("\"","'")
      else:
        return None
    except:
      return None
  
  def GetUserInfo(self, username, token):
      try:
        query = { 'username':username,'token': token }
        user = self.eLibraryUsers.find(query, {"_id": 0, 'username': 1, 'cardId':1, 'token':1 })
        user = list(user)
        if len(user) > 0:
          return dumps(user)
        else:
          return None
      except:
        return None
    
  def LoginForNewToken(self, username, pwd, oldToken):
    try:
      results = self.GetToken(pwd)
      if len(results) > 0:
        expiration = str((datetime.datetime.now() + datetime.timedelta(hours=12)).strftime(" %Y-%m-%d %H:%M:%S"))
        query = { 'username':username, 'token': oldToken }
        newvalues = { "$set": { 'salt': results[0], 'pwd': results[1], 'token': results[2], 'loginExpiration':expiration } }
        self.eLibraryUsers.update_one(query, newvalues)
        mydoc = self.eLibraryUsers.find({'token': results[2]},{"_id": 0})
        result = list(mydoc)
        return dumps(result)
      else:
        return None
    except:
      return None
  
  #endregion
  
  #region BOOK Transactions
  def viewBooks(self):
    return dumps(self.eLibraryBooks.find({}, {"_id": 0})).replace("\"","'")
  
  def checkOut(self, bookTitle, cardId):
    try:
      query = {'title': bookTitle, 'checkedOut': 0}
      updates = {"$set": {'checkedOutBy': cardId, 'checkedOut': 1, 'lastCheckedOutDate': str((datetime.datetime.now()).strftime(" %Y-%m-%d %H:%M:%S")) }}
      self.eLibraryBooks.update_one(query, updates)
      return dumps(self.eLibraryBooks.find({'title': bookTitle}, {"_id": 0})).replace("\"","'")
    except:
      return None
        
  def checkIn(self, bookTitle, cardId):
    try:
      query = {'title': bookTitle, 'checkedOutBy': cardId, 'checkedOut': 1}
      updates = {"$set": {'checkedOutBy': '', 'checkedOut': 0 }}
      self.eLibraryBooks.update_one(query, updates)
      return dumps(self.eLibraryBooks.find({'title': bookTitle}, {"_id": 0})).replace("\"","'")
    except:
      return None
  
  #endregion
