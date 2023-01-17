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


def insert_one_processed(client, collection, user_name, data_list):
    post = {'userName': user_name, 'multi': data_list[0], 'code': data_list[1]}
    return collection.insert_one(post)


def insert_many_processed(client, collection, user_name, processed_data):
    post = [{'userName': user_name, 'multi': v[0], 'code': v[1]} for v in processed_data]
    return collection.insert_many(post)


def test():
    client = connect_db()
    collection = get_collection(client, 'codeparams')
    doc = get_latest_codeparams(client, collection, 'nishida')
    print(doc)
