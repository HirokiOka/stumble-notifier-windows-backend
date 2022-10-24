import os
from dotenv import load_dotenv
from requests import request
import json


load_dotenv()
api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")


def get_codeparams_from_std_id(std_id):
    payload = json.dumps({
        "collection": "codeparams",
        "database": "test",
        "dataSource": "Cluster0",
        "filter": {
            "id": std_id
        }
    })
    headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': api_key
    }
    action = 'action/find'
    url = api_url + action
    response = request("POST", url, headers=headers, data=payload)
    res_json = json.loads(response.text)
    return res_json['documents']


def post_all_data_from_id(std_id, saved_at, source_code, features, multi_pred, code_pred):
    payload = json.dumps({
        "collection": "features_and_predictions",
        "database": "test",
        "dataSource": "Cluster0",
        "document": {
            "std_id": std_id,
            "code": source_code,
            "saved_at": saved_at,
            "lfhf": features['lfhf'][0],
            "pnn50": features['pnn50'][0],
            "sloc": features['sloc'][0],
            "ted": features['ted'][0],
            "elapsed_seconds": features['elapsed-seconds'][0],
            "multi_prediction": multi_pred,
            "code_prediction": code_pred
        }
    })
    headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': api_key
    }
    action = 'action/insertOne'
    url = api_url + action
    response = request("POST", url, headers=headers, data=payload)
    res_json = json.loads(response.text)
    return res_json


def get_codeparams_from_time(saved_at):
    payload = json.dumps({
        "collection": "codeparams",
        "database": "test",
        "dataSource": "Cluster0",
        "filter": {
            "savedAt": saved_at
        }
    })
    headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': api_key
    }
    action = 'action/findOne'
    url = api_url + action
    response = request("POST", url, headers=headers, data=payload)
    res_json = json.loads(response.text)
    return res_json['document']


def get_unique_ids():
    payload = json.dumps({
        "collection": "codeparams",
        "database": "test",
        "dataSource": "Cluster0"
    })
    headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': api_key
    }
    action = 'action/find'
    url = api_url + action
    response = request("POST", url, headers=headers, data=payload)
    res_json = json.loads(response.text)
    result = []
    for v in res_json["documents"]:
        if ('id' in v):
            result.append(v['id'])
    return list(set(result))


"""
ids = get_unique_ids()
ids.sort()
print(ids)
"""
