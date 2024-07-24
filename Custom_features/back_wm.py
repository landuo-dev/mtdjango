from pymongo import MongoClient
from datetime import datetime




def back(poi_id):
    client = MongoClient('mongodb://localhost:27017/')
    back_up = client['back_up_jx']
    test = client['test']
    other = client['other']
    back_up_log = other['back_up_jxlog']

    poi_id = str(poi_id)
    collection = test[poi_id]
    documents = []
    for i in collection.find():
        documents.append(i)

    now = datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    back_log = back_up_log.find_one({"poi_id": poi_id})
    if back_log:

        back_name_len = (back_log['length'] + 1) % 2
        back_name = poi_id + "_" + str(back_name_len)

        back_collect = back_up[back_name]
        back_collect.drop()

        back_collect.insert_many(documents)
        back_up_log.update_one({"poi_id": poi_id},
                               {
                                   "$set": {
                                       "length": back_name_len,
                                       f"ctime_{back_name_len}": date,  # 使用动态生成的字段名
                                   }
                               })


    else:
        back_name_len = 0
        back_name = poi_id + "_" + str(back_name_len)

        back_collect = back_up[back_name]

        back_collect.insert_many(documents)
        back_up_log.insert_one(
            {"poi_id": poi_id, f"ctime_0": date, f"ctime_1": '', "length": back_name_len,
             "names": [f"{poi_id}_0", f"{poi_id}_1"]})


if __name__ == '__main__':
    back('21807579')
    # pass