from pymongo import MongoClient
from datetime import datetime


def push_ds(poi_id):
    client = MongoClient('mongodb://localhost:27017')
    db = client['other']
    collection = db['ds']
    docs = []
    for i in collection.find({"poi_id": poi_id}):
        poi_id = i['poi_id']
        timestamp = i['date']
        date = datetime.fromtimestamp(timestamp)
        filename = i['file_name'].split('_')[0]
        if i['type_select']:
            type_select = '折扣定时任务'
        else:
            type_select = '夹心定时任务'
        docs.append({
            "poi_id": poi_id,
            "date": date,
            'dsid': i['_id'],
            "type_select": type_select,
            "filename": filename
        })

    return docs
