from flask import Flask,render_template,request,redirect,url_for,session
from flask_pymongo import pymongo
from cryptography.fernet import Fernet

key = Fernet.generate_key()
salt = key.decode('utf8')

app = Flask(__name__)
CONNECTION_STRING = "mongodb+srv://charles:0QyVtWs73CMc6DHe@flask-mongo.qfh5r.mongodb.net/test_crd?retryWrites=true&w=majority"
#CONNECTION_STRING = "mongodb://localhost:27018/test_crd"

client = pymongo.MongoClient(CONNECTION_STRING)

user_db = client['test_crd']['users']

@app.route("/", methods = ["POST", "GET"])
def log():
    return render_template("login.html")
    
@app.route("/signup", methods = ["POST", "GET"])
def signup():
    return render_template("register.html")

@app.route("/register", methods = ["POST","GET"])
def reg():
  message = ''

  if request.method == 'POST':

    userid = request.form['id']
    email = request.form['mail']
    password = request.form['pwd']
    r_password = request.form['repwd']

    em = str(email).lower()
    ur = str(userid).lower()
    obj = password.encode()

    instance = salt.encode()
    crypter = Fernet(instance)
    bush = crypter.encrypt(obj)
    k = str(bush, 'utf8')

    users = user_db.find({})
  
    for x in users:
        usr = x['username']

        if usr == ur:
            message = "Username already exists"
            return render_template("register.html", msg = message)

        if password != r_password:
            message = "Password doesn't match"
            return render_template("register.html", msg = message)

    user_db.insert_one({"username" : ur, "email" : em, "password" : k, "salt" : salt}) #Indent issue here. Now ok when bringing it backward

    return render_template("login.html") 
  
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



if __name__ == "__main__":
    app.run(debug=True)