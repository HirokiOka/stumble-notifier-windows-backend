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
    db = client.development
    collection = db[collection_name]
    return collection


def get_latest_document(client, collection, user_name):
    documents = list(collection.find({"userName": user_name}))
    return documents[-1]


def get_latest_codeparams(client, collection, user_name):
    doc = get_latest_document(client, collection, user_name)
    executed_at = doc['executedAt']
    sloc = doc['sloc']
    ted = doc['ted']
    return [executed_at, sloc, ted]


def insert_processed(client, collection, data_list):
    post = {'multi': data_list[0], 'code': data_list[1]}
    return collection.insert_one(post)


def test():
    client = connect_db()
    collection = get_collection(client, 'codeparams')
    doc = get_latest_codeparams(client, collection, 'nishida')
    print(doc)
