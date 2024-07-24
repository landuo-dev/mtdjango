import requests
from pymongo import MongoClient
import json

from config import headers1


def delete_product(poi_id, actid):
    query_params = {
        'source': 'pc',
        # 'conflictCoverType': 0,
        'yodaReady': 'h5',
        'csecplatform': 4,
        'csecversion': '2.4.0',
    }

    data = {
        'actType': '17',
        'actIds': actid,
    }

    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/disable'

    response = requests.post(url, headers=headers1, data=data, params=query_params)
    if response.status_code == 200:
        # 创建 MongoDB 客户端
        client = MongoClient('mongodb://localhost:27017/')
        # 选择数据库和集合（相当于 SQL 中的表）
        db = client['actproduct']
        collection = db[str(poi_id)]
        collection.update_one({'actId': actid}, {"$set": {"actId": '', "errMsg": ''}})


if __name__ == '__main__':
    actid = '10100936631309'
    poi_id = 19021228
    delete_product(poi_id, actid)
