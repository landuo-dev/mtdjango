import re
import time

import requests
import json
from pymongo import MongoClient
import os
import urllib.parse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def set_post_data(name, poi_id):
    post_data = {
        "skuName": name,
        'creatorRoleType': '-1',
        'pageNum': '1',
        'poiId': poi_id,
        'pageSize': 30,
        'status': '1',
    }
    return post_data


def getdata(i, poi_id):
    spec = re.sub(' ', '', i['food']['spec'].split('(')[0])
    dicts = {
        'weeksTime': i['weeksTime'],
        'period': i['period'],
        'poiId': str(poi_id),
        'poiName': i['poiName'],
        'actId': i['actId'],
        'autoDelayDays': i['autoDelayDays'],
        'name': i['food']['wmSkuName'],
        'spec': spec,
        'poiCharge': i['actInfo'][0]['poiCharge'],
        'originPrice': i['actInfo'][0]['originPrice'],
        'actPrice': i['actInfo'][0]['actPrice'],
        'startTime': i['startTime'],
        'endTime': i['endTime'],
    }
    return dicts


def save_database(poi_id, data, collection, result):
    lists = data['list']
    documents = []
    for i in lists:
        dicts = getdata(i, poi_id)
        spec = re.sub(' ', '', i['food']['spec'].split('(')[0])
        if collection.find_one({"name": i['food']['wmSkuName'], 'spec': spec}):
            collection.update_one({"name": i['food']['wmSkuName'], 'spec': spec},
                                  {'$set': dicts})
            result.add(f"已有商品{i['food']['wmSkuName']}, 更新数据{i['food']['wmSkuName']}--->")
            continue
        documents.append(dicts)
    if len(documents):
        collection.insert_many(documents)


def main1(poi_id, df, cookie):
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/list'
    result = set()
    # GET 查询参数
    query_params = {
        'actType': '17',
        'source': 'pc',
        'yodaReady': 'h5',
        'csecplatform': '4',
        'csecversion': ' 2.4.0',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie,
        'Origin': 'https://e.waimai.meituan.com',
        'Referer': 'https://e.waimai.meituan.com/gw/static_resource/product',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        # ... 其他 headers 字段
    }

    sess = requests.session()
    sess.headers = headers
    sess.cookie = cookie
    sess.params = query_params

    client = MongoClient('mongodb://localhost:27017/')
    db_act = client['actproduct']
    collection_act = db_act[str(poi_id)]

    arr = df.iloc[:, 3].to_list()

    arr = set([i.split('-')[0] for i in arr])

    for name in arr:
        num = 0
        while 3 > num:
            try:
                response = sess.post(url, data=set_post_data(name, poi_id))
                if response.status_code == 200:
                    json_data = response.json()['data']
                    if len(json_data['list']):
                        save_database(poi_id, json_data, collection_act, result)
                    break
                else:
                    print(f'连接失败， 正在重新尝试第{num}次', name)
                    num += 1
                    time.sleep(1)
            except Exception as e:
                print(e, name)
                print(f'连接失败， 正在重新尝试第{num}次')
                num += 1
                time.sleep(1)
    return result


def get_tag(poi_id, headers):
    data = {
        'tabStatus': '-1',
        'inRecycleBin': '0',
        'wmPoiId': poi_id,
        'appType': '3'
    }

    # 发送 POST 请求
    url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/tag/r/tagList?ignoreSetRouterProxy=true'
    num = 0
    while 3 > num:
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                print('获取标签成功')
                return response.json()
        except Exception as e:
            print(e, poi_id)
    return None


def get_actdata(poiId, tagId, startTime, endTime, tagname, headers):
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
    num = 0
    while 3 > num:
        try:
            response = requests.get(url, params=quer_data, headers=headers, timeout=5)
            if response.status_code == 200:
                json_data = response.json()
                # print(f'获取{tagname}数据成功')
                return json_data
            return None
        except Exception as e:
            print(e, tagname)
            num += 1
            time.sleep(1)

    # fileName = os.path.join(f'./product_data/', '折扣活动.json')
    # with open(fileName, 'w', encoding='utf-8') as file:
    #     json.dump(json_data, file, ensure_ascii=False, indent=4)
    # print("JSON 数据已成功保存到 output.json 文件中。")


def updata_data(collection, name, spec, actid, errMsg, spuId, skuId, tagName):
    result = collection.update_one({"actId": actid},
                                   {"$set": {
                                       "actId": actid,
                                       "errMsg": errMsg,
                                       'spuId': spuId,
                                       "skuId": skuId,
                                       "tagName": tagName,
                                       "spec": spec
                                   }})
    return result.modified_count


def main02(poid, cookie):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie,
        'Origin': 'https://e.waimai.meituan.com',
        'Referer': 'https://e.waimai.meituan.com/gw/static_resource/product',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        # ... 其他 headers 字段
    }
    result = ''

    # 获取当前日期和时间的datetime对象
    now = datetime.now()
    # 设置时间为0时0分0秒
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today + relativedelta(months=1)
    # 转换为时间戳
    startTime = int(today.timestamp())
    endTime = int(next_month.timestamp())
    tag_data = get_tag(poid, headers)
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['actproduct']
    collection = db[str(poid)]
    document = []
    if tag_data:
        for i in tag_data['data']:
            act_data = get_actdata(poid, i['id'], startTime, endTime, i['name'], headers)
            # print(i['name'])
            # if i['name'] == '网红热卖🎉🎉🎉':
            #     print(act_data)
            if act_data:
                for j in act_data['data']:
                    for k in j['skuList']:
                        actid = k['mutexActId']
                        spec = re.sub(' ', '', k['spec'].split('(')[0])
                        # if k['skuName'] == "放个屁都是爱你的形状手绘生日蛋糕":
                        #     print('1'*100)
                        if not collection.find_one(
                                {"name": k['skuName'], "spec": spec}) and not actid:
                            document.append({
                                "spuId": j['spuId'],
                                "skuId": k['id'],
                                'poiId': poid,
                                'name': k['skuName'],
                                'spec': spec,
                                'originPrice': int(k['price']),
                                'tagName': i['name'],
                                'errMsg': '',
                            })
                        else:
                            # pass
                            updata_data(collection, k['skuName'], spec, actid, k['errMsg'], j['spuId'], k['id'],
                                        i['name'])
    else:
        print('店铺标签获取失败')

    if len(document):
        collection.insert_many(document)
        collection.create_index([("name", 1), ("spce", -1)])

    return result





if __name__ == '__main__':
    poi_id = ''
    df = ''
    cookie = ['']
    main1(poi_id, df, cookie)
    main02(poi_id, cookie)