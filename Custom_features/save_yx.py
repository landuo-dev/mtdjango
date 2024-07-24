from pymongo import MongoClient


def save_jz(poi_id, limit_price, price, day, cookie, type_select, time_select):
    limit_price = int(limit_price)
    price = int(price)
    day = int(day)
    type_select = int(type_select)

    client = MongoClient('mongodb://localhost:27017/')
    db = client['other']
    collect = db[f'jzyx_{time_select}']

    if collect.find_one({"poi_id": poi_id}):
        collect.update_one({"poi_id": poi_id}, {"$set": {
            "poi_id": poi_id,
            "limit_price": limit_price,
            "price": price,
            "day": day,
            "type_select": type_select,

        }})
    else:
        document = {
            "poi_id": poi_id,
            "limit_price": limit_price,
            "price": price,
            "day": day,
            "type_select": type_select,
        }

        collect.insert_one(document)
