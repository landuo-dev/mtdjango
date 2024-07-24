import json
import os
import urllib.parse
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import headers1
from pymongo import MongoClient


def get_tag(poi_id, headers):
    data = {
        'tabStatus': '-1',
        'inRecycleBin': '0',
        'wmPoiId': poi_id,
        'appType': '3'
    }

    # 发送 POST 请求
    url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/tag/r/tagList?ignoreSetRouterProxy=true'
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print('获取标签成功')
        return response.json()
    return None


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
        print(f'获取{tagname}数据成功')
        return json_data
    return None

    # fileName = os.path.join(f'./product_data/', '折扣活动.json')
    # with open(fileName, 'w', encoding='utf-8') as file:
    #     json.dump(json_data, file, ensure_ascii=False, indent=4)
    # print("JSON 数据已成功保存到 output.json 文件中。")


def updata_data(collection, actid, errMsg, spuId, skuId, tagName):
    result = collection.update_one({"actId": actid},
                                   {"$set": {
                                       "errMsg": errMsg,
                                       'spuId': spuId,
                                       "skuId": skuId,
                                       "tagName": tagName,
                                   }})
    return result.modified_count


def main(poid):
    # 获取当前日期和时间的datetime对象
    now = datetime.now()

    # 设置时间为0时0分0秒
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today + relativedelta(months=1)
    # 转换为时间戳
    startTime = int(today.timestamp())
    endTime = int(next_month.timestamp())

    tag_data = get_tag(poid, headers1)
    client = MongoClient('mongodb://localhost:27017/')

    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['actproduct']
    collection = db[str(poid)]
    document = []
    if tag_data:
        for i in tag_data['data']:
            act_data = get_actdata(poid, i['id'], startTime, endTime, i['name'])
            if act_data:
                for j in act_data['data']:
                    for k in j['skuList']:
                        actid = k['mutexActId']
                        if not actid:
                            # staus = collection.find_one({"name": k['skuName'], "spec": k})
                            document.append({
                                "spuId": j['spuId'],
                                "skuId": k['id'],
                                'poiId': poid,
                                'name': k['skuName'],
                                'spec': k['spec'],
                                'originPrice': int(k['price']),
                            })
                        else:
                            pass
                            # updata_data(collection, actid, k['errMsg'], j['spuId'], k['id'], i['name'])

    # collection.insert_many(document)


if __name__ == '__main__':
    poi_id = 19021228
    main(poi_id)
    print('完成')