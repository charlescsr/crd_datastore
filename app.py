'''Procedure for creating a file based key-data store
This is documentation on my code in implementing a file based key-data store using Python.

This is done in the form of a web application using the Flask Framework

Author: Charles Samuel R, Final Year CSE - St Joseph's College of Engineering
Date: 28/Dec/2020                  Version: 1.0
'''

#-------------------------------------------------------------------------------------------------------------
#PACKAGES IMPORTED
# This section contains the packages I used to implement the solution
from flask import Flask,render_template,request, session, send_file #The base for the application
from werkzeug.utils import secure_filename #Save the file to write to the DB
import json #To handle JSON value
import os #To Remove temporary file to save storage
from flask_pymongo import pymongo #To interact with Mongo DB
from bson.json_util import dumps, loads #To get final Data Store
from pathlib import Path #Get path of file to send to client
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------
# MAIN VARIABLES
# This is the main variables that will be used throughout the program
# These first three are for sessions
SAMPLE_USERID = 1
SESSION_PRE = "data_"
SESSION_POST = "_store" 
app = Flask(__name__) # To initialise the app 
app.secret_key = '?A7_`a?^k=9+1k6Z@XX0vFpDasd"pQ' # Secret key provides security for sessions
CONNECTION_STRING = "mongodb+srv://charles:0QyVtWs73CMc6DHe@flask-mongo.qfh5r.mongodb.net/test_crd?retryWrites=true&w=majority" #Connect to Mongo DB
#CONNECTION_STRING = "mongodb://localhost:27018/test_crd" #Localhost connection string
#-------------------------------------------------------------------------------------------------------------
client = pymongo.MongoClient(CONNECTION_STRING)

db = client['test_crd']['crd']
user_db = client['test_crd']['users']

def validate_user(username):
    return SESSION_PRE+str(SAMPLE_USERID) + SESSION_POST

@app.route("/", methods = ["POST", "GET"])
def index():
    return render_template("main.html")

@app.route("/enter", methods=["GET", "POST"])
def enter():
    name = request.form["user"]
    if user_db.find({"username": name}).count() == 0:
        user_db.insert_one({"username": name})
        sid = validate_user(name)
        if(sid):
            global SAMPLE_USERID
            session['sid'] = sid
            session['name'] = name
            SAMPLE_USERID += 1
    else:
        return "Name is already in use"

    return render_template("create.html")
    
@app.route("/create", methods = ["POST", "GET"])
def create():
    k = request.form['key']
    value = request.files['value']
    ttl = request.form['ttl']
    if value.filename.split('.')[1] == 'json':
        value.save(secure_filename(value.filename))
        f = open(value.filename,)
        data = json.load(f)
        os.remove(value.filename)
        #if ttl != 0:
        #    cur = db.find({"key": k})
        #    if cur.count() == 0:
        #        fin_value = {"key": k, "value": data, "createdAt": datetime.now()}
        #        db.insert_one(fin_value)
                #db.create_index({"createdAt": 1}, { "expireAfterSeconds": ttl})
        #    else:
        #        return "Key already exists"

        fin_value = {"key": k, "value": data, "createdBy": session['name']}
        db.insert_one(fin_value)

        return render_template("create.html", msg1="Key created")

    return render_template("create.html", msg1="Wrong File Format")

@app.route("/read", methods=["GET", "POST"])
def read():
    k = str(request.form.get("key"))
    v = None
    cur = db.find({"key": k, "createdBy": session['name']})
    cur1 = db.find({"key": k})
    cur2 = db.find({"createdBy": session['name']})
    if cur1.count() == 0:
        return render_template("read.html", msg2="Key not found")
    elif cur2.count() == 0:
        return render_template("read.html", msg2="Someone else has that key")
    
    for x in cur:
        v = x['value']
    if v == None:
        return render_template("read.html", msg2="Someone else has that key")

    return render_template("read.html", msg2="Value is "+str(v))

@app.route("/delete", methods=["GET", "POST"])
def delete():
    k = str(request.form.get("key"))
    cur1 = db.find({"key": k})
    cur2 = db.find({"createdBy": session['name']})
    if cur1.count() == 0:
        return render_template("delete.html", msg3="Key not found")
    elif cur2.count() == 0:
        return render_template("delete.html", msg3="Someone else has that key")
    
    db.delete_one({"key": k})

    return render_template("delete.html", msg3="Key deleted successfully")

@app.route("/download", methods=["GET", "POST"])
def download():
    cur = db.find({"createdBy":session['name']}, {"_id":0, "createdBy": 0})
    f = 'data.json'
    list_cur = list(cur) 
  
    json_data = dumps(list_cur, indent = 4)  

    with open('data.json', 'w') as file: 
        file.write(json_data)

    user_db.delete_one({"username": session['name']}) 
    
    return send_file(Path('data.json'), attachment_filename=f, as_attachment=True)
    

if __name__ == "__main__":
    app.run(debug=True)