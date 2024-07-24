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


def save_database(poi_id, data, collection):
    lists = data['list']
    documents = []
    for i in lists:
        if collection.find_one({"name": i['food']['wmSkuName'], 'spec': i['food']['spec'].split('(')[0]}):
            print(f"添加失败 已有商品{i['food']['wmSkuName']}")
            return 0
        dicts = {
            'weeksTime': i['weeksTime'],
            'period': i['period'],
            'poiId': poi_id,
            'poiName': i['poiName'],
            'actId': i['actId'],
            'autoDelayDays': i['autoDelayDays'],
            'name': i['food']['wmSkuName'],
            'spec': i['food']['spec'].split('(')[0],
            'poiCharge': i['actInfo'][0]['poiCharge'],
            'originPrice': i['actInfo'][0]['originPrice'],
            'actPrice': i['actInfo'][0]['actPrice'],
            'startTime': i['startTime'],
            'endTime': i['endTime'],
        }
        documents.append(dicts)
    if len(documents):
        collection.insert_many(documents)


def main1(poi_id, cookie):
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/list'

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
        'Cookie':cookie,
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

    client = MongoClient('mongodb://localhost:27017/')
    db = client['test']
    collection = db[str(poi_id)]

    db_act = client['actproduct']
    collection_act = db_act[str(poi_id)]
    for i in collection.find():
        # print(i['name'])
        num = 0
        while 3 > num:
            response = requests.post(url, headers=headers, data=set_post_data(i['name'], poi_id),
                                     params=query_params)
            if response.status_code == 200:
                json_data = response.json()['data']
                if len(json_data['list']):
                    save_database(poi_id, json_data, collection_act)
                break
            else:
                print(f'连接失败， 正在重新尝试第{num}次')
                num += 1
                time.sleep(1)


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
            print(e)
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
                                       "spec": spec.split('(')[0]
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
                        # if k['skuName'] == "放个屁都是爱你的形状手绘生日蛋糕":
                        #     print('1'*100)
                        if not collection.find_one(
                                {"name": k['skuName'], "spec": k['spec'].split('(')[0]}) and not actid:
                            document.append({
                                "spuId": j['spuId'],
                                "skuId": k['id'],
                                'poiId': poid,
                                'name': k['skuName'],
                                'spec': k['spec'].split('(')[0],
                                'originPrice': int(k['price']),
                                'tagName': i['name'],
                                'errMsg': '',
                            })
                        else:
                            # pass
                            updata_data(collection, k['skuName'], k['spec'], actid, k['errMsg'], j['spuId'], k['id'],
                                        i['name'])
    if len(document):
        collection.insert_many(document)
        collection.create_index([("name", 1), ("spce", -1)])


if __name__ == '__main__':
    poi_id = 19021228
    cookie = "_lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; _lxsdk=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; acctId=97786666; token=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=rbAzQ0FErd8OINAT34hV7Qd4dhEeLPTSYalMD3CsvtDc4jcw_4QgBIJyu8LGpNlRLJCSpNy7sGhVki1h8xZ_kA; city_location_id=0; location_id=0; cityId=440300; provinceId=440000; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; wmPoiId=19021228; isOfflineSelfOpen=0; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; logistics_support=; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=eh9p2wr26vdygzc3vi56; _lxsdk_s=18f275bd034-1fa-d3-97%7C%7C725"
    # main1(poi_id, cookie)
    print('任务1完成')
    main02(poi_id, cookie)
    print('完成')
