import requests
import json
import re
import pandas as pd
from pymongo import MongoClient
import time
import asyncio
import aiohttp
import time


def set_post_data(document, poi_id, originPrice, actPrice):
    data = {
        "startTime": document['startTime'],
        "endTime": document['endTime'],
        "autoDelayDays": document['autoDelayDays'],
        "weeksTime": document['weeksTime'],
        "period": document['period'],
        "poiUserType": 0,
        "isOpenSmartDiscount": False,
        "isAgree": 1,
        "actType": 17,
        "conflictCoverType": 0,
        "poiId": poi_id,
        "actIds": str(document['actId']),
        "settingType": 1,
        "chargeMethod": 0,
        "orderLimit": -1,
        "dayLimit": -1,
        "actInfo": [
            {
                "originPrice": originPrice,
                "actPrice": actPrice,
                "mtCharge": 0,
                "agentCharge": 0,
                "poiCharge": round(originPrice - actPrice, 2)
            }
        ]
    }
    return data


async def make_request(collection, session, url, aa, query_params, headers, data):
    try:
        async with session.post(url, json=aa, params=query_params, headers=headers) as response:
            json_data = await response.json()
            if json_data.get('msg'):
                print(json_data['msg'])
                print(data.iloc[3])
                print(data.iloc[4])
                raise '报错'
            await collection.update_one({'actId': data.iloc[0]}, {"$set": {"actPrice": data.iloc[6]}})
            return json_data
    except Exception as e:
        print(e)
        print(data.iloc[3])
        print(data.iloc[4])
        await asyncio.sleep(1)  # 注意这里使用异步sleep
        return None


async def main(df, poi_id, cookie):
    result = set()
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['actproduct']

    if not str(poi_id) in db.list_collection_names():
        return '该店没入库'
    collection = db[str(int(poi_id))]
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/update'
    # GET 查询参数
    query_params = {
        'source': 'pc',
        'conflictCoverType': 0,
        'yodaReady': 'h5',
        'csecplatform': 4,
        'csecversion': '2.4.0',
        # 'mtgsig': " %7B%22a1%22%3A%221.1%22%2C%22a2%22%3A1713577385218%2C%22a3%22%3A%221713574757862KEGIAGWfd79fef3d01d5e9aadc18ccd4d0c95072737%22%2C%22a5%22%3A%22y%2F4dvBlvKMWuqxYYNmTg2c%3D%3D%22%2C%22a6%22%3A%22hs1.4aOG4x69iuIGtADfqn9IKcXpWvblltTHUONJdukyi%2FqZmF4xdggqmwgIxb5G%2F8C8CK0M9EmvblXarNo8VohdrFg%3D%3D%22%2C%22x0%22%3A4%2C%22d1%22%3A%22caea92afaf73ca5a34165303659958d6%22%7D"
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Cookie': cookie,
        'Origin': 'https://e.waimai.meituan.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        # ... 其他 headers 字段
    }

    for i, data in df.iterrows():
        # print(data.iloc[3])
        # print(data.iloc[4])
        doc = collection.find_one({'name': data.iloc[3], 'spec': data.iloc[4]})
        aa = set_post_data(doc, data.iloc[0], data.iloc[5], data.iloc[6])
        session = aiohttp.ClientSession()
        num = 0  # 假设num的初始值是0
        while 3 > num:
            json_data = await make_request(collection, session, url, aa, query_params, headers, data)
            if json_data is not None:
                # print(json_data)
                collection.update_one({'name': data.iloc[3], 'spec': data.iloc[4]}, {"$set": {
                    "actPrice": aa['actInfo']["actPrice"],
                    "originPrice": aa['actInfo']["originPrice"],
                    "poiCharge": aa['actInfo']["poiCharge"],
                }})
                break  # 如果请求成功，则跳出循环
            num += 1  # 否则增加num的值并重试
            result.add(data.iloc[3])
        await session.close()  # 不要忘记关闭session
    return result

# Python 3.7+ 可以使用下面的方式运行异步主函数
if __name__ == '__main__':
    pass
    # asyncio.run(main())

    # cookie = input('请输入cookie\n')
    #
    # df = pd.read_excel(r'D:\updata\折扣\19021228.xlsx')
    # client = MongoClient('mongodb://localhost:27017/')
    # # 选择数据库和集合（相当于 SQL 中的表）
    # db = client['actproduct']
    #
    # url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/update'
    #
    # # GET 查询参数
    # query_params = {
    #     'source': 'pc',
    #     'conflictCoverType': 0,
    #     'yodaReady': 'h5',
    #     'csecplatform': 4,
    #     'csecversion': '2.4.0',
    #     # 'mtgsig': " %7B%22a1%22%3A%221.1%22%2C%22a2%22%3A1713577385218%2C%22a3%22%3A%221713574757862KEGIAGWfd79fef3d01d5e9aadc18ccd4d0c95072737%22%2C%22a5%22%3A%22y%2F4dvBlvKMWuqxYYNmTg2c%3D%3D%22%2C%22a6%22%3A%22hs1.4aOG4x69iuIGtADfqn9IKcXpWvblltTHUONJdukyi%2FqZmF4xdggqmwgIxb5G%2F8C8CK0M9EmvblXarNo8VohdrFg%3D%3D%22%2C%22x0%22%3A4%2C%22d1%22%3A%22caea92afaf73ca5a34165303659958d6%22%7D"
    # }
    #
    # headers1 = {
    #     'Accept': 'application/json, text/plain, */*',
    #     'Accept-Language': 'zh-CN,zh;q=0.9',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/x-www-form-urlencoded',
    #     'Cookie': cookie,
    #     'Origin': 'https://e.waimai.meituan.com',
    #     'Referer': 'https://e.waimai.meituan.com/gw/static_resource/product',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    #     'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
    #     'sec-ch-ua-mobile': '?0',
    #     'sec-ch-ua-platform': '"Windows"'
    #     # ... 其他 headers 字段
    # }
