from flask import Flask,render_template,request,redirect,url_for,session
from werkzeug.utils import secure_filename
import json
from flask_pymongo import pymongo
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
def log():
    return render_template("success.html")
    
'''    
@app.route("/allow", methods = ["POST", "GET"])
def allow():
    message=''
    flag=0
    if request.method == "POST":
        u = request.form["id"]
        pas = request.form["key"]
        name = str(u).lower()
        users = user_db.find({})
        for x in users:
            n = x['username']
            if n == name:
                flag = 1
            
        if flag == 0:
            message = "Invalid Username"  
            return render_template("login.html",msg=message) 
        user = user_db.find({"username":name})
        for x in user:
            pwd = x['password']
            sss = x['salt']
            s = pwd.encode()
            instance = sss.encode()
            crypter = Fernet(instance)
            decryptpw = crypter.decrypt(s)
            returned = decryptpw.decode('utf8')
            if returned == pas:
                return render_template("success.html")
            else:
                message="Invalid Password"  
                return render_template("login.html",msg=message) 
'''
@app.route("/create", methods = ["POST", "GET"])
def create():
    k = request.form['key']
    value = request.files['value']
    if value.filename.split('.')[1] == 'json':
        value.save(secure_filename(value.filename))
        f = open(value.filename,)
        data = json.load(f)
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
    v = None 
    cur = db.find({"key": k})
    if cur.count() == 0:
        return "Key not found"
    
    db.delete_one({"key": k})

    return "Key deleted successfully"

if __name__ == "__main__":
    app.run(debug=True)