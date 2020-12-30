import unittest
import pymongo

DB_CONNECTION_STRING = "mongodb+srv://charles:0QyVtWs73CMc6DHe@flask-mongo.qfh5r.mongodb.net/test_crd?retryWrites=true&w=majority"
client = pymongo.MongoClient(DB_CONNECTION_STRING) # Connect to Mongo DB

db = client['test_crd']['crd']
user_db = client['test_crd']['users']

class AppTest(unittest.TestCase):
    '''
        Class to test DB operations in Mongo DB.
    '''
    def setUp(self):
        pass

    def test_user_db(self):
        '''
            Test insertion in the user db
        '''