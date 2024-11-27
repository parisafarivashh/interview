from zibal_project.settings import mongo_uri, mongo_db
from pymongo import MongoClient


def create_connection_db():
    print(mongo_uri, mongo_db)
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    return db

