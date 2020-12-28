from flask import Flask,render_template,request,redirect,url_for,session, send_file
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
from flask_pymongo import pymongo
from bson.json_util import dumps, loads
from pathlib import Path 
from cryptography.fernet import Fernet

key = Fernet.generate_key()
salt = key.decode('utf8')

app = Flask(__name__)
CONNECTION_STRING = "mongodb+srv://charles:0QyVtWs73CMc6DHe@flask-mongo.qfh5r.mongodb.net/test_crd?retryWrites=true&w=majority"
#CONNECTION_STRING = "mongodb://localhost:27018/test_crd"

client = pymongo.MongoClient(CONNECTION_STRING)

user_db = client['test_crd']['users']
db = client['test_crd']['crd']

@app.route("/", methods = ["POST", "GET"])
def index():
    return render_template("index.html")
    
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
        if ttl != 0:
            cur = db.find({"key": k})
            if cur.count() == 0:
                fin_value = {"key": k, "value": data, "createdAt": datetime.now()}
                db.insert_one(fin_value)
                db.create_index({"createdAt": 1}, { "expireAfterSeconds": ttl})
            else:
                return "Key already exists"

        fin_value = {"key": k, "value": data}
        db.insert_one(fin_value)

        return "Key created"

    return "Wrong file format"

@app.route("/read", methods=["GET", "POST"])
def read():
    k = str(request.form.get("key"))
    v = None 
    cur = db.find({"key": k})
    if cur.count() == 0:
        return "Key not found"
    
    for x in cur:
        v = x['value']

    return "Value is "+str(v)

@app.route("/delete", methods=["GET", "POST"])
def delete():
    k = str(request.form.get("key"))
    cur = db.find({"key": k})
    if cur.count() == 0:
        return "Key not found"
    
    db.delete_one({"key": k})

    return "Key deleted successfully"

@app.route("/download", methods=["GET", "POST"])
def download():
    cur = db.find({}, {"_id":0})
    f = 'data.json'
    list_cur = list(cur) 
  
    json_data = dumps(list_cur, indent = 4)  

    with open('data.json', 'w') as file: 
        file.write(json_data) 
    
    return send_file(Path('data.json'), attachment_filename=f, as_attachment=True)
    

if __name__ == "__main__":
    app.run(debug=True)