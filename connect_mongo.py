import os
from dotenv import load_dotenv
import pymongo

load_dotenv()
password = os.getenv('DBPWD')
driver = os.getenv('DBDRIVER')
user = os.getenv('DBUSER')
host = os.getenv('DBHOST')


def connect_db():
    print('connecting to MongoDB...')
    client = pymongo.MongoClient(f'{driver}://{user}:{password}@{host}/?retryWrites=true&w=majority')
    return client


def get_collection(client, collection_name):
    db = client.test
    collection = db[collection_name]
    return collection


def get_latest_document(client, collection, user_id):
    documents = list(collection.find({"id": user_id}))
    return documents[-1]


def get_latest_codeparams(client, collection, user_id):
    doc = get_latest_document(client, collection, user_id)
    executed_at = doc['savedAt']
    sloc = doc['sloc']
    ted = doc['ted']
    return [executed_at, sloc, ted]


def test():
    client = connect_db()
    collection = get_collection(client, 'codeparams')
    doc = get_latest_codeparams(client, collection, 'nishida')
    print(doc)
