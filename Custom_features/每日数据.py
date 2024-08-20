from datetime import datetime, timedelta
from pymongo import MongoClient


def get_data(user_name, ws):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["jt_log"]

    db_user = client['other']
    collection_user = db_user['jt_all']

    date = datetime.now() - timedelta(days=1)
    # date = datetime(2024, 7, k)
    yestarday = datetime(date.year, date.month, date.day, 0, 0, 0)
    ctime = f'{date.year}-{date.month:02}-{date.day:02}'
    stime = int(yestarday.timestamp())
    settime = f"{date.year}{date.month:02}{date.day:02}"
    print(stime)
    # 查询所有文档
    documents = []
    result = collection_user.find({"店铺对接负责人": user_name})
    # 遍历结果并打印每个文档
    for doc in result:
        poi_id = str(doc['ID号码'])
        user_log = db[poi_id]
        dc = user_log.find_one({"stime": stime})
        if dc:
            ws.append([ctime, poi_id, doc['店铺名称'], dc['validOrders'], dc['revenue'], dc['debit'] / 100, "",
                       doc['店铺对接负责人'], "美团"])


if __name__ == '__main__':
    get_data('彭淑娜')
