from flask import Response, request, g
import datetime
from repository import *
from functools import wraps

def validation(repo: repository):
    def wrapper(func):
      @wraps(func)
      # Validates session tokens
      def authorize(*args, **kwargs):
        try:
          token = request.headers["Authorization"]
          query = { "token": token }
          user = repo.eLibraryUsers.find_one(query, {"_id": 0, "loginExpiration":1 })
          if user == None:
            return Response('Authorization failed', status=401)
          date_format = "%Y-%m-%d %H:%M:%S"
          date_of_expiration_str = str(datetime.datetime.strptime(user["loginExpiration"], date_format))
          date_of_expiration = datetime.datetime.strptime(date_of_expiration_str, date_format)
          if date_of_expiration > datetime.datetime.now():
            g.token = token
            return func(*args, **kwargs) 
        except:
          return Response('Authorization failed', status=401)
      return authorize
    return wrapper