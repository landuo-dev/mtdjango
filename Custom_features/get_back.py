from pymongo import MongoClient


def get_back_log(poi_id):
    poi_id = str(poi_id)
    client = MongoClient('mongodb://localhost:27017/')
    other = client['other']
    back_up_log = other['back_up_jxlog']
    arr = []
    document = back_up_log.find_one({"poi_id": poi_id})
    if not document:
        return []
    if document["ctime_0"] != '':
        arr.append({
            "poi_id": poi_id,
            'ctime': document["ctime_0"],
            'name': f"{poi_id}_0",
            "type": "夹心"
        })

    if document["ctime_1"] != '':
        arr.append({
            "poi_id": poi_id,
            'ctime': document["ctime_1"],
            'name': f"{poi_id}_1",
            "type": "夹心"
        })

    back_up_log = other['back_up_zklog']
    document = back_up_log.find_one({"poi_id": poi_id})
    if not document:
        return arr

    if document['ctime_0'] != "":
        arr.append({
            "poi_id": poi_id,
            "ctime": document['ctime_0'],
            "name": f"{poi_id}_0",
            "type": "折扣"
        })

    if document['ctime_1'] != "":
        arr.append({
            "poi_id": poi_id,
            "ctime": document['ctime_1'],
            "name": f"{poi_id}_1",
            "type": "折扣"
        })

    return arr
