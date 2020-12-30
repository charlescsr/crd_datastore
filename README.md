# CRD Key-Value Data Store

This is a simple Key-Value Data Store using Python and Mongo DB.

The program is set in the form of a web application using the Flask web framework in Python.

The main packages used in this application include:

* Flask - For web application 
* PyMongo - To connect to Mongo DB

Full list can be found in ```requirements.txt```

To set up the application:<br><br>
First install Virtualenv package with either
```
$ pip install virtualenv
```

OR:
```
$ python -m pip install virtualenv
```

1. Create Virtual Environment

```
$ virtualenv venv
$ source venv/bin/activate
```

2. Install packages

```
$ pip install requirements.txt
```

3. Start app

```
$ python app.py
```

The app can be found at http://127.0.0.1:5000/

Mongo DB is used for storing the data and the file can be got as a JSON to the user.

The operations involved in this data store include:

* Create - Creates a Key-Value pair with an optional TTL(Time-To-Live). Value is a JSON object
* Read - Read a Value that is created by the user
* Delete - Delete a Key-Value pair that the user created.

Testing proved to be a bit comprehensive with Flask, hence the excel file is added to show what kind of tests were carried out.

The word document describes the objective and flow of the application.

Code Score of ```app.py``` using Pylint: 9.91

Code Quality can be checked by running ```python lint.py```
