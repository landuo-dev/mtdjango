import pandas as pd
import requests
from pymongo import MongoClient
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from config import headers2, headers1


def get_time():
    # 获取当前日期和时间的datetime对象
    now = datetime.now()

    # 设置时间为0时0分0秒
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today + relativedelta(months=1)
    # 转换为时间戳
    starttime = today.timestamp()
    endtime = next_month.timestamp()

    return (int(starttime), int(endtime))


def set_post_data(startTime, endTime, poiId, wmSkuId, wmSpuId, originPrice, actPrice):
    data = {
        "startTime": startTime,
        "endTime": endTime,
        "autoDelayDays": 30,
        "weeksTime": "1,2,3,4,5,6,7",
        "period": "00:00-23:59",
        "poiUserType": 0,
        "isOpenSmartDiscount": False,
        "isAgree": 1,
        "actType": 17,
        "conflictCoverType": 0,
        "poiId": poiId,
        "foods": [
            {
                "wmSkuId": wmSkuId,
                "wmSpuId": wmSpuId,
                "settingType": 1,
                "chargeMethod": 0,
                "orderLimit": -1,
                "dayLimit": -1,
                "actInfo": [
                    {
                        # "discount": 4.47,
                        "originPrice": originPrice,
                        "actPrice": actPrice,
                        "mtCharge": 0,
                        "agentCharge": 0,
                        "poiCharge": round(originPrice - actPrice, 2)
                    }
                ]
            },
        ]
    }
    return data


def get_actdata(poiId, tagId, startTime, endTime, tagname):
    quer_data = {
        'source': 'pc',
        'actType': '17',
        'poiId': poiId,
        'startTime': str(startTime),
        'endTime': str(endTime),
        'tagId': tagId,
        'yodaReady': 'h5',
        'csecplatform': '4',
        'csecversion': ' 2.4.0',

    }
    url = "https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/query/queryProductByWmPoiIdAndTagId?weeksTime=1,2,3,4,5,6,7&period=00:00-23:59"
    response = requests.get(url, params=quer_data, headers=headers1, timeout=5)
    if response.status_code == 200:
        json_data = response.json()
        # print(f'获取{tagname}数据成功')
        return json_data
    return None

    # fileName = os.path.join(f'./product_data/', '折扣活动.json')
    # with open(fileName, 'w', encoding='utf-8') as file:
    #     json.dump(json_data, file, ensure_ascii=False, indent=4)
    # print("JSON 数据已成功保存到 output.json 文件中。")


def updata_data(collection, name, spec, actid, errMsg, spuId, skuId, tagName):
    result = collection.update_one({"name": name, "spec": spec},
                                   {"$set": {
                                       "actId": actid,
                                       "errMsg": errMsg,
                                       'spuId': spuId,
                                       "skuId": skuId,
                                       "tagName": tagName,
                                   }})
    return result.modified_count


query_params = {
    'source': 'pc',
    # 'conflictCoverType': 0,
    'yodaReady': 'h5',
    'csecplatform': 4,
    'csecversion': '2.4.0',
}


def main(poid, name, spec, price):
    # 创建 MongoDB 客户端
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['actproduct']
    collection = db[str(poid)]

    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/create'
    document = collection.find_one({"name": name, "spec": spec})
    # print(document)
    starttime, endtime = get_time()
    post_data = set_post_data(starttime, endtime, document['poiId'], document['skuId'], document['spuId'],
                              document['originPrice'], price)

    response = requests.post(url, params=query_params, json=post_data, headers=headers2)
    print(response.text)
    if response.status_code == 200:
        db01 = client['test']
        collection01 = db01[str(poid)]
        doc = collection01.find_one({'name': name})
        # 获取当前日期和时间的datetime对象
        now = datetime.now()

        # 设置时间为0时0分0秒
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        next_month = today + relativedelta(months=1)
        # 转换为时间戳
        startTime = int(today.timestamp())
        endTime = int(next_month.timestamp())

        act_data = get_actdata(poid, doc['tagId'], startTime, endTime, doc['tagName'])
        if act_data:
            for j in act_data['data']:
                for k in j['skuList']:
                    if k['skuName'] == name and k['spec'] == spec:
                        actid = k['mutexActId']
                        updata_data(collection, k['skuName'], k['spec'], actid, k['errMsg'], j['spuId'], k['id'],
                                    doc['tagName'])




if __name__ == '__main__':
    df = pd.read_excel(r'G:\updata\折扣\test.xlsx')

    for i, data in df.iterrows():
        main(data.iloc[0], data.iloc[1], data.iloc[2], data.iloc[4])
