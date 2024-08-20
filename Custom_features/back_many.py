from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
back_up = client['back_up']
test = client['test']
other = client['other']
back_up_log = other['back_up_log']


def back(poi_id):
    poi_id = str(poi_id)
    collection = test[poi_id]
    documents = []
    for i in collection.find():
        documents.append(i)

    back_log = back_up_log.find_one({"poi_id": poi_id})
    if back_log:
        back_names = back_log['back_names']
        back_name = poi_id + "_" + str(len(back_names))
        back_collect = back_up[back_name]
        back_collect.insert_many(documents)
        back_names.append(back_name)
    else:
        back_name = poi_id + "_" + str(0)
        back_collect = back_up[back_name]
        back_collect.insert_many(documents)
        back_up_log.insert_one({"poi_id": poi_id, "back_names": [back_name]})




if __name__ == '__main__':
    back('16402295')
