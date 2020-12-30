'''Procedure for creating a file based key-data store, developed for Freshworks

Author: Charles Samuel R, Final Year CSE - St Joseph's College of Engineering
Email: rcharles.samuel99@gmail.com

Date: 28/Dec/2020                  Version: 1.0
'''

#---------------------------------------------------------------------------------------------------
#PACKAGES IMPORTED
# This section contains the packages used to implement the solution
from pathlib import Path #Get path of file to send to client
import os #To Remove temporary file to save storage
import json #To handle JSON value
from datetime import datetime, timedelta
from flask import Flask,render_template,request, session, send_file #The base for the application
from werkzeug.utils import secure_filename #Save the file to write to the DB
from flask_pymongo import pymongo #To interact with Mongo DB
from bson.json_util import dumps #To get final Data Store

#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
# MAIN VARIABLES
# These are the main variables that will be used throughout the program
# These first two are for sessions
SESSION_PRE = "data_"
SESSION_POST = "_store"
app = Flask(__name__) # To initialise the app
app.secret_key = '?A7_`a?^k=9+1k6Z@XX0vFpDasd"pQ' # Secret key provides security for sessions
CONNECTION_STRING = "mongodb+srv://charles:0QyVtWs73CMc6DHe@flask-mongo.qfh5r.mongodb.net/test_crd?retryWrites=true&w=majority" #Connect to Mongo DB
#CONNECTION_STRING = "mongodb://localhost:27018/test_crd" #Localhost connection string
#---------------------------------------------------------------------------------------------------
client = pymongo.MongoClient(CONNECTION_STRING) # Connect to Mongo DB

db = client['test_crd']['crd']
user_db = client['test_crd']['users']

#---------------------------------------------------------------------------------------------------
# USER FUNCTIONS
# This section contains functions declared for use in the application
def validate_user(username):
    '''
        Function to return string with username for session
    '''
    return SESSION_PRE + str(username) + SESSION_POST

def db_size():
    '''
        Function to check Main DB size and prevent create if size is at 1GB
    '''
    cmd = db.runCommand({
        "dbStats": 1,
    })
    return cmd["size"]
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
# ROUTES
# This section contains all the routes of the web application
@app.route("/", methods = ["POST", "GET"])
def index():
    '''
        Main page of the app
    '''
    return render_template("main.html")

@app.route("/enter", methods=["GET", "POST"])
def enter():
    '''
        Page to show the operations possible

    '''
    name = request.form["user"]
    if user_db.find({"username": name}).count() == 0:
        user_db.insert_one({"username": name})
        sid = validate_user(name)
        if sid:
            session['sid'] = sid
            session['name'] = name
    else:
        return "Name is already in use"

    return render_template("create.html")

@app.route("/create", methods = ["POST", "GET"])
def create():
    '''
        Endpoint for the create operation
    '''
    if db_size() >= 1024 * 1024 * 1024:
        return render_template("create.html", msg1="Create not possible. Space exceeded")

    k = request.form['key']
    value = request.files['value']
    ttl = request.form['ttl']
    now = datetime.now()
    value.save(secure_filename(value.filename))
    file = open(value.filename,)
    data = json.load(file)
    os.remove(value.filename)
    if ttl != 0:
        cur = db.find({"key": k})
        if cur.count() == 0:
            fin_value = {"key": k, "value": data, "Time Stamp": now,
                        "TTL": ttl, "createdBy": session['name']}
            db.insert_one(fin_value)
            return render_template("create.html", msg1="Key created")

        if cur.count() != 0:
            return "Key already exists"

    fin_value = fin_value = {"key": k, "value": data, "Time Stamp": now,
                            "TTL": ttl, "createdBy": session['name']}
    db.insert_one(fin_value)

    return render_template("create.html", msg1="Key created")

@app.route("/read", methods=["GET", "POST"])
def read():
    '''
        Endpoint for the read operation
    '''
    k = str(request.form.get("key"))
    value = None
    now = datetime.now()
    ttl = None
    time = None
    cur = db.find({"key": k, "createdBy": session['name']})
    cur1 = db.find({"key": k})
    cur2 = db.find({"createdBy": session['name']})
    for val in cur:
        ttl = val['TTL']
        time = val['Time Stamp']
        value = val['value']

    exp = time + timedelta(seconds=int(ttl))
    exp = exp.strftime("%X")

    if ttl != 0 and now.strftime("%X") >= exp:
        return  render_template("read.html", msg2="Key expired")

    if ttl != 0 and exp < now.strftime("%X"):
        return render_template("read.html", msg2="Value is "+str(value))

    if cur1.count() == 0:
        return render_template("read.html", msg2="Key not found")

    if cur2.count() == 0:
        return render_template("read.html", msg2="Someone else has that key")

    if value is None:
        return render_template("read.html", msg2="Someone else has that key")

    return render_template("read.html", msg2="Value is "+str(value))

@app.route("/delete", methods=["GET", "POST"])
def delete():
    '''
        Endpoint for the Delete operation
    '''
    k = str(request.form.get("key"))
    now = datetime.now()
    ttl = None
    time = None
    cur = db.find({"key": k, "createdBy": session['name']})
    cur1 = db.find({"key": k})
    cur2 = db.find({"createdBy": session['name']})

    for val in cur:
        ttl = val['TTL']
        time = val['Time Stamp']

    exp = time + timedelta(seconds=int(ttl))
    exp = exp.strftime("%X")

    if ttl != 0 and now.strftime("%X") >= exp:
        return  render_template("delete.html", msg2="Key expired")

    if ttl != 0 and exp < now.strftime("%X"):
        db.delete_one({"key": k})
        return render_template("delete.html", msg3="Key deleted successfully")

    if cur1.count() == 0:
        return render_template("delete.html", msg3="Key not found")

    if cur2.count() == 0:
        return render_template("delete.html", msg3="Someone else has that key")

    db.delete_one({"key": k})

    return render_template("delete.html", msg3="Key deleted successfully")

@app.route("/download", methods=["GET", "POST"])
def download():
    '''
        Endpoint to download the Data Store
    '''
    cur = db.find({"createdBy":session['name']}, {"_id":0, "createdBy": 0})
    final_file = 'data.json'
    list_cur = list(cur)

    json_data = dumps(list_cur, indent = 4)

    with open('data.json', 'w') as file:
        file.write(json_data)

    user_db.delete_one({"username": session['name']})

    return send_file(Path('data.json'), attachment_filename=final_file, as_attachment=True)
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
# MAIN BLOCK
# This is the block that initialises the web application
if __name__ == "__main__":
    app.run(debug=True)
#---------------------------------------------------------------------------------------------------
