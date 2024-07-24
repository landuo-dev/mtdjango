from pymongo import MongoClient

import redis


def save_database(poi_id, cookie, datetime_obj, type_select, file_name, uploaded_file_url):
    client = MongoClient('mongodb://localhost:27017')
    db = client['other']
    collect = db['ds']

    r = redis.Redis(db=2)

    doc = collect.find_one({'poi_id': poi_id, "file_name": file_name})
    # print(doc)
    make_an_appointment = f"{datetime_obj.year}_{datetime_obj.month}_{datetime_obj.day}_{datetime_obj.hour}_{datetime_obj.minute}"
    timestamp = datetime_obj.timestamp()
    if collect.find_one({'poi_id': poi_id, "file_name": file_name}):
        collect.update_one({'poi_id': poi_id, "file_name": file_name}, {"$set": {
            "poi_id": poi_id,
            "cookie": cookie,
            "date": timestamp,
            "type_select": int(type_select),
            "file_name": file_name,
            "file_url": uploaded_file_url
        }})

    else:
        collect.insert_one({
            "poi_id": poi_id,
            "cookie": cookie,
            "date": timestamp,
            "type_select": int(type_select),
            "file_name": file_name,
            "file_url": uploaded_file_url
        })

    r.zadd('ds', {f"{poi_id}_{make_an_appointment}_{type_select}": timestamp})
