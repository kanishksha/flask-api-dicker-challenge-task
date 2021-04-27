import requests
import os
from datetime import datetime
from flask import Flask, json, request
from flask_sqlalchemy import SQLAlchemy
from requests.exceptions import HTTPError
from dotenv import load_dotenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.sqlite3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

#db schema for nasa near by objects
class Neo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    nasa_jpl_url = db.Column(db.String(120), unique=True, nullable=False)
    is_potentially_hazardous_asteroid = db.Column(db.String(20), nullable=False)

#retrieving api key from .env file 

# Add an endpoint that responds with HTTP Status Code 200 once the server is ready to serve traffic.
@app.route("/", methods=['GET'])
def run():
    return "{\"message\":\"The container is up and running\"}", 200


#api endpoint that gets data from api.nasa.gov and supply to the client
@app.route("/api/v1/neo", methods=['GET'])
def get_neo():
    try:
      response = requests.get('https://api.nasa.gov/neo/rest/v1/neo/browse?api_key='+os.getenv("API_KEY"))
      responsejson = response.json()
      objects=[] 
      db.create_all()
      for obj in responsejson["near_earth_objects"]:
#add each near by object in Neo model to create a row with unique id 
        neo_obj = Neo(id=obj['id'], name=obj['name'], nasa_jpl_url=obj['nasa_jpl_url'], 
                           is_potentially_hazardous_asteroid=obj['is_potentially_hazardous_asteroid'])

#checks if neo is already present in the db or not
#if present it will not addd the neo in the array
        check_duplicate=db.session.query(Neo.id).filter_by(id=obj['id']).scalar() is not None
        if(check_duplicate is False):
          objects.append(neo_obj) 

#add the array in the db and commit in db
      db.session.add_all(objects)
      db.session.commit()

#to see the neo model
# Neo.query.all()

# If the response was successful, no Exception will be raised    
      response.raise_for_status() 
      return responsejson, 200
    except HTTPError as http_err:
        return {"message": "An error occurred"}, 400  
    except Exception as err:
        return {"message": "server error occurred"}, 500

#api endpoint that that counts how many NEOs will happen this week.

def same_week(date1, date2):
      d1 = datetime.strptime(date1,'%Y%m%d')
      d2 = datetime.strptime(date2,'%Y%m%d')
      return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year

#steps 1. get ur date from system 2. convert epoch to standadrd date 3. calculate the date difference, same week=>show
@app.route("/api/v1/neo/week", methods=['GET'])
def get_neo_week_count():
    try:
      response = requests.get('https://api.nasa.gov/neo/rest/v1/neo/browse?api_key='+os.getenv("API_KEY"))
      responsejson = response.json()
      neo=[] #for storing the list for close approach date
      countneo=[] #count the neo that will happen this week

#gets all the dates and place in the neo array
      for obj in responsejson["near_earth_objects"]:
        for date in obj["close_approach_data"]:
          neo.append(date["close_approach_date"])
      
      # takes current date and convert into a string in format 20210421
      currentdate=datetime.now()
      currentdateconverted=str(currentdate.strftime("%Y%m%d"))
      
      for date in neo:
        neodate=date.replace("-","")
        checkweek=same_week(currentdateconverted, neodate) #compares the current date with dates of neos and return true if date is a part of the same week
        if(checkweek is True): #if checkweek is true, append the array with True
          countneo.append(True)

# If the response was successful, no Exception will be raised    
      response.raise_for_status() 
      return {"neo_this_week": len(countneo)} , 200
    except HTTPError as http_err:
        return {"message": "An error occurred"}, 400  
    except Exception as err:
        return {"message": "server error occurred"}, 500

#Add an endpoint on /neo/next?hazardous=true shows the next NEO. It should accept a hazardous query parameter to show the next hazardous NEO.
@app.route("/api/v1/neo/week/next", methods=['GET'])
def get_neo_next():
    try:
      response = requests.get('https://api.nasa.gov/neo/rest/v1/neo/browse?api_key='+os.getenv("API_KEY"))
      responsejson = response.json()
      ishazardous=[]
      hazardous = request.args.get('hazardous')
#return hazardous query paramete is true return only the objects with hazardous value true
#else return all the near by objects
      if hazardous=="true" or hazardous=="True" :
        for x in responsejson["near_earth_objects"]:
          if x['is_potentially_hazardous_asteroid']==True:
             ishazardous.append(({"id":x["id"],"name":x['name']}))
        return json.dumps(ishazardous), 200
      else:
         for x in responsejson["near_earth_objects"]:
            return json.dumps(x), 200
    except HTTPError as http_err:
        return {"message": "An error occurred"}, 400  
    except Exception as err:
        return {"message": "server error occurred"}, 500


if __name__ == "__main__":
    app.run(debug=True)


    