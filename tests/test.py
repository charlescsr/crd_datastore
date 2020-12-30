import unittest
from flask_pymongo import pymongo
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

CONNECTION_STRING = "mongodb+srv://charles:0QyVtWs73CMc6DHe@flask-mongo.qfh5r.mongodb.net/test_crd?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING) # Connect to Mongo DB

db = client['test_crd']['crd']
user_db = client['user_info']['users']

class AppTest(unittest.TestCase):
    '''
        Class to test DB operations in Mongo DB.
    '''
    def setUp(self):
        pass

    def test010_user_db(self):
        '''
            Test insertion in the User DB
        '''
        user_db.insert_one({"username": "dummy"})

        self.assertTrue(user_db.find({"username": "dummy"}).count() != 0)

    def test050_remove_user_db(self):
        '''
            Remove Document from User DB
        '''
        user_db.delete_one({"username": "dummy"})

        self.assertEqual(user_db.find({"username": "dummy"}).count(), 0)

    def test020_create_crd(self):
        '''
            Create Key-Value Pair and test out DB
        '''
        data = {"id": "1", "value": "lorem"}
        now = datetime.now()

        fin_value = {"key": "test", "value": data, "Time Stamp": now,
                    "TTL": 0, "createdBy": "dummy"}
        
        db.insert_one(fin_value)

        self.assertNotEqual(db.find({"key": "test", "createdBy": "dummy"}).count(), 0)

    def test030_read_crd(self):
        '''
            Function to test Read of the data store
        '''
        cur = db.find({"key": "test", "createdBy": "dummy"})

        self.assertNotEqual(cur.count(), 0)

    def test040_delete_crd(self):
        '''
            Function to test Delete function of the data store
        '''
        db.delete_one({"key": "test", "createdBy": "dummy"})
        self.assertEqual(db.find({"key": "test", "createdBy": "dummy"}).count(), 0)

if __name__ == '__main__': 
    unittest.main()