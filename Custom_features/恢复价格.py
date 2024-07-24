from pymongo import MongoClient
import time
import traceback
import pandas as pd
import requests
from pymongo import MongoClient
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from requests.exceptions import InvalidHeader

from Custom_features.setting import while_fun


def get_time():
    # 获取当前日期和时间的datetime对象
    now = datetime.now()

    # 设置时间为0时0分0秒
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today + relativedelta(years=1)
    # 转换为时间戳
    starttime = today.timestamp()
    endtime = next_month.timestamp()
    return (int(starttime), int(endtime))


def set_post_data(startTime, endTime, poiId, foods):
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
        "conflictCoverType": 1,
        "poiId": poiId,
        "foods": foods,
    }
    return data


def set_foods(wmSkuId, wmSpuId, originPrice, actPrice):
    food = {
        "wmSkuId": wmSkuId,
        "wmSpuId": wmSpuId,
        "settingType": 1,
        "chargeMethod": 0,
        "orderLimit": -1,
        "dayLimit": -1,
        "actInfo": [
            {
                # "discount": 4.47,
                "originPrice": round(originPrice, 2),
                "actPrice": round(actPrice, 2),
                "mtCharge": 0,
                "agentCharge": 0,
                "poiCharge": round(originPrice - actPrice, 2)
            }
        ]
    }

    return food


def set_post_data2(name, poi_id):
    post_data = {
        "skuName": name,
        'creatorRoleType': '-1',
        'pageNum': '1',
        'poiId': poi_id,
        'pageSize': 30,
        'status': '1',
    }
    return post_data


def get_actdata(poiId, tagId, startTime, endTime, headers):
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
    response = while_fun(requests.get, url=url, params=quer_data, headers=headers, timeout=5)
    json_data = response.json()
    return json_data

    # fileName = os.path.join(f'./product_data/', '折扣活动.json')
    # with open(fileName, 'w', encoding='utf-8') as file:
    #     json.dump(json_data, file, ensure_ascii=False, indent=4)
    # print("JSON 数据已成功保存到 output.json 文件中。")


def getdata(i, poi_id):
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
    return dicts


def get_actdata1(name, spec, poi_id, headers, collection):
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/list'
    query_params = {
        'actType': '17',
        'source': 'pc',
        'yodaReady': 'h5',
        'csecplatform': '4',
        'csecversion': ' 2.4.0',
    }
    response = while_fun(requests.post, url=url, headers=headers, data=set_post_data2(name, poi_id),
                         params=query_params)

    if response.status_code == 200 and response.json()['data']:
        actproduct = response.json()['data']['list']
        for i in actproduct:
            # print(i)
            if i['food']['wmSkuName'] == name and i['food']['spec'].split('(')[0] == spec:
                datas = getdata(i, poi_id)
                collection.update_one({"name": name, "spec": spec},
                                      {"$set": datas})
    return response.json()


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


def add_act(session, poi_id, actlist, url):
    starttime, endtime = get_time()
    post_data = set_post_data(starttime, endtime, poi_id, actlist)
    response = while_fun(session.post, url=url, json=post_data)

    if response and response.status_code == 200:
        json_data = response.json()
        print(json_data)
        if json_data['msg']:
            if json_data['msg'] == '系统异常，请稍后重试':
                print(post_data)
            print(json_data['msg'])

            time.sleep(1)

        return 1
    return 0


def Recover_jg(back_poid, poi_id, cookie):
    result = set()
    client = MongoClient('mongodb://localhost:27017/')
    back_up_zk = client['back_up_zk']
    back_collection = back_up_zk[str(back_poid)]

    actproduct = client['actproduct']
    act_collection = actproduct[str(poi_id)]

    query_params = {
        'source': 'pc',
        'conflictCoverType': 1,
        'yodaReady': 'h5',
        'csecplatform': 4,
        'csecversion': '2.4.0',
    }
    headers2 = {
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

    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/create'

    session = requests.session()
    session.headers = headers2
    session.cookie = cookie
    session.params = query_params

    actlist = []
    k = 0

    for document_back in back_collection.find():
        if "actPrice" not in document_back:
            continue
        k += 1
        name = document_back['name']
        spec = document_back['spec']
        originPrice = document_back['originPrice']
        price = document_back['actPrice']
        # print(document_new)
        # print(name, spec, originPrice, price)
        document_new = act_collection.find_one({"name": name, "spec": spec})
        # print(document_new)
        if document_new:
            if originPrice - price <= 0:
                result.add(f'折扣价格大于原价 {name}, {spec}')
                continue
            if originPrice < 0 or price < 0:
                result.add(f'价格不能为负数 {name}, {spec}')
                continue
            actlist.append(
                set_foods(document_new['skuId'], document_new['spuId'], originPrice, price)
            )
        else:
            print("店铺没有商品", name, spec)
            result.add(f'新店没有商品 {name}')

        if k >= 30:
            if not len(actlist):
                k = 0
                continue
            if add_act(session, poi_id, actlist, url):
                actlist = []
                k = 0
    # print(actlist)
    if len(actlist):
        add_act(session, poi_id, actlist, url)

    return result


if __name__ == '__main__':
    cookie = "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; wm_order_channel=appshare1; utm_source=5913; _ga_NMY341SNCF=GS1.3.1716602003.3.1.1716603712.0.0.0; acctId=97786666; token=0h5rLEuzGbvrUwVItsXSXMCSwA8bztdSyp7cDR9g4SwQ*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=2VtwEpD5fdEW_dtACPxV1b05QiNPZQGGo02BBp8RDvaI3NB0yb3dE0mi1cpOaTnF6jXq_8aEl07b2Ks2XORrVg; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; isOfflineSelfOpen=0; logistics_support=; JSESSIONID=1k4nqasgja6qy1vy72qj6tm93t; setPrivacyTime=1_20240608; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=kttuoali91kunefimnv8; _lxsdk_s=18ff56c14da-fe5-026-323%7C%7C1542"
    Recover_jg("19021228_0", "19021228", cookie)
