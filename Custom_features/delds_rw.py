import os

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import redis


def delds_rw(dsid):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['other']
    collection = db['ds']

    r = redis.Redis(db=2)

    doc = collection.find_one({'_id': ObjectId(dsid)})
    # print(doc)
    fileurl = doc['file_url']
    timestamp = doc['date']
    datetime_obj = datetime.fromtimestamp(timestamp)
    poi_id = doc['poi_id']
    make_an_appointment = f"{datetime_obj.year}_{datetime_obj.month}_{datetime_obj.day}_{datetime_obj.hour}_{datetime_obj.minute}"
    type_select = doc['type_select']
    rname = f"{poi_id}_{make_an_appointment}_{type_select}"

    print(fileurl)
    print(rname)
    r.zrem("ds", rname)
    os.remove(fileurl)
    collection.delete_one({'_id': ObjectId(dsid)})

