from pymongo import MongoClient
import json
from datetime import datetime, timedelta


def fenleirank(collection, start_time, end_time):
    pipeline = [
        {"$match": {
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time  # 注意这里应该是 end_time，而不是 timestamp
            }
        }},

        {'$group': {
            "_id": "$prodGroupName",  # 替换为你的分组字段
            "sum": {"$sum": "$prodGroupClickUv"},  # 计算每个分组的数量
            "prodGroupName": {"$first": "$prodGroupName"}  # 选择每个分组中的第一个prodGroupDescription值
        }},
        {"$sort": {
            "sum": -1  # 根据'sum'字段降序排序
        }},
        {"$limit": 10}  # 限制返回的结果数量为10
    ]
    cursor = collection.aggregate(pipeline)
    return [{k: v for k, v in d.items() if k != '_id'} for d in list(cursor)]


def productsales(collection, start_time, end_time):
    print(start_time, end_time)
    pipeline = [
        {"$match": {
            "stime": {
                "$gte": start_time,
                "$lte": end_time  # 注意这里应该是 end_time，而不是 timestamp
            }
        }},

        {'$group': {
            "_id": "$name",  # 替换为你的分组字段
            "sales": {"$sum": "$sales"},  # 计算每个分组的数量 spuScaleClickUv
            "orders": {"$sum": "$orders"},  # 计算每个分组的数量
            "prodName": {"$first": "$name"},  # 选择每个分组中的第一个prodGroupDescription值
        }},
    ]
    cursor = collection.aggregate(pipeline)

    arr = [{k: v for k, v in d.items() if k != '_id'} for d in list(cursor)]
    dic = {}

    for i in arr:
        dic[i['prodName']] = (i['sales'], i['orders'])

    return dic


def productrank(collection, sales_data, start_time, end_time):
    pipeline = [
        {"$match": {
            "timestamp": {
                "$gte": start_time,
                "$lte": end_time  # 注意这里应该是 end_time，而不是 timestamp
            }
        }},

        {'$group': {
            "_id": "$wmSpuName",  # 替换为你的分组字段
            "sum1": {"$sum": "$spuScaleClickUv"},  # 计算每个分组的数量 spuScaleClickUv
            "sum2": {"$sum": "$spuSegmentExposeUv"},  # 计算每个分组的数量
            "prodName": {"$first": "$wmSpuName"},  # 选择每个分组中的第一个prodGroupDescription值

            "imgurl": {"$first": "$picLargeUrl"},
            "prodGroupName": {"$first": "$prodGroupName"}
        }},
        {"$sort": {
            "sum2": -1  # 根据'sum'字段降序排序
        }},
    ]
    cursor = collection.aggregate(pipeline)

    arr = [{k: v for k, v in d.items() if k != '_id'} for d in list(cursor)]

    for i, data in enumerate(arr):
        name = data["prodName"]
        sales, orders = sales_data.get(name, (0, 0))
        arr[i]["sales"] = sales
        arr[i]["orders"] = orders

    return arr


def fenlei_json(collection):
    temp = datetime.now() - timedelta(days=1)
    yesterday = datetime(temp.year, temp.month, temp.day, 0, 0, 0)
    timestamp = int(yesterday.timestamp())
    cursor = collection.find({"timestamp": timestamp}).sort("prodGroupClickUv", -1).limit(10)
    yesterday_data = [{k: v for k, v in d.items() if k != '_id'} for d in list(cursor)]

    temp = datetime.now() - timedelta(days=8)
    start_time = datetime(temp.year, temp.month, temp.day, 0, 0, 0).timestamp()

    seven_days_data = fenleirank(collection, start_time, timestamp)

    temp = datetime.now() - timedelta(days=31)
    start_time = datetime(temp.year, temp.month, temp.day, 0, 0, 0).timestamp()

    # 使用聚合框架进行分组聚合计算
    one_month_data = fenleirank(collection, start_time, timestamp)

    return yesterday_data, seven_days_data, one_month_data


def hangye_json(poi_id, startTime, endTime):
    # 连接MongoDB数据库
    client = MongoClient('mongodb://localhost:27017/')
    db = client[str(poi_id)]
    # 获取数据库下所有的集合
    json_data = {}
    yesterday_data, seven_days_data, one_month_data = fenlei_json(db['1分类总表'])

    # 将数据转换为JSON格式
    json_data['yesterday_data'] = yesterday_data
    json_data['seven_days_data'] = seven_days_data
    json_data['one_month_data'] = one_month_data
    json_data["product"] = []

    ten_rank = fenleirank(db['1分类总表'], startTime, endTime)
    sales_data = productsales(db['clickSell'], startTime, endTime)
    # print(ten_rank)
    # print(sales_data)
    arr = []
    for i, data in enumerate(ten_rank):
        prodGroupName = data['prodGroupName']
        arr += productrank(db[prodGroupName], sales_data, startTime, endTime)

    arr.sort(key=lambda x: x['sum2'], reverse=True)
    json_data['product'] = arr
    # print(arr)
    return json_data


if __name__ == '__main__':
    hangye_json("20339389", "1719936000", "1722528000")
# Roaming
