from pymongo import MongoClient
import requests
import pandas as pd
import re
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from Custom_features.save_pro import save
from Custom_features.单商品折扣入库 import save_act_data
from Custom_features.save_act import saveAct


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


def get_actdata(poiId, tagId, startTime, endTime, tagname, cookie):
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

    url = "https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/query/queryProductByWmPoiIdAndTagId?weeksTime=1,2,3,4,5,6,7&period=00:00-23:59"
    num = 0
    while 3 > num:
        try:
            response = requests.get(url, params=quer_data, headers=headers, timeout=5)
            if response.status_code == 200:
                json_data = response.json()
                # print(f'获取{tagname}数据成功')
                return json_data
        except Exception as e:
            print(e)
            num += 1

    return None

    # fileName = os.path.join(f'./product_data/', '折扣活动.json')
    # with open(fileName, 'w', encoding='utf-8') as file:
    #     json.dump(json_data, file, ensure_ascii=False, indent=4)
    # print("JSON 数据已成功保存到 output.json 文件中。")


def updata_data(collection, act_name, name, spec, actid, errMsg, spuId, skuId, price, tagName):
    spec = spec.rsplit('(')[0]
    # act_name = re.sub('@', '', act_name)
    count1 = collection.count_documents({"name": act_name})
    if count1 == 1:
        collection.update_one({"name": act_name},
                              {"$set": {
                                  "name": name,
                                  "actId": actid,
                                  "errMsg": errMsg,
                                  'spuId': spuId,
                                  "skuId": skuId,
                                  "tagName": tagName,
                                  "originPrice": price
                              }})
    else:
        result = collection.update_one({"name": act_name, "spec": spec},
                                       {"$set": {
                                           "name": name,
                                           "actId": actid,
                                           "errMsg": errMsg,
                                           'spuId': spuId,
                                           "skuId": skuId,
                                           "tagName": tagName,
                                           "originPrice": price
                                       }})


def add_acct(document, cookie):
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/create'

    query_params = {
        'source': 'pc',
        'conflictCoverType': 0,
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

    starttime, endtime = get_time()

    # print(document)
    post_data = set_post_data(starttime, endtime, document['poiId'], document['skuId'],
                              document['spuId'],
                              document['originPrice'], document['actPrice'])

    num = 0
    while 3 > num:
        try:
            response = requests.post(url, params=query_params, json=post_data, headers=headers2)
            json_data = response.json()
            failList = json_data['data']['failList']
            if len(failList):
                errmsg = failList[0]['errMsg']
                if errmsg == "7天内上调过价格不可设置活动":
                    return 1
            print(json_data)
            return 0
        except Exception as e:
            print(e)
            num += 1
    return 0


def add_updata(doc, collection, poid, name, act_name, cookie):
    # 获取当前日期和时间的datetime对象
    now = datetime.now()

    # 设置时间为0时0分0秒
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today + relativedelta(months=1)
    # 转换为时间戳
    startTime = int(today.timestamp())
    endTime = int(next_month.timestamp())

    act_data = get_actdata(poid, doc['tagId'], startTime, endTime, doc['tagName'], cookie)
    if act_data:
        for j in act_data['data']:
            for k in j['skuList']:
                if k['skuName'] == name:
                    actid = k['mutexActId']
                    updata_data(collection, act_name, name, k['spec'], actid, k['errMsg'], j['spuId'], k['id'],
                                k['price'], doc['tagName'])
                else:
                    break


def set_post_data1(name, poi_id):
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
    spec = re.sub(' ', '', i['food']['spec'].rsplit('(')[0])
    dicts = {
        'weeksTime': i['weeksTime'],
        'period': i['period'],
        'poiId': str(poi_id),
        'poiName': i['poiName'],
        'actId': i['actId'],
        'autoDelayDays': i['autoDelayDays'],
        # 'name': i['food']['wmSkuName'],
        'spec': spec,
        'poiCharge': i['actInfo'][0]['poiCharge'],
        'originPrice': i['actInfo'][0]['originPrice'],
        'actPrice': i['actInfo'][0]['actPrice'],
        'startTime': i['startTime'],
        'endTime': i['endTime'],
    }
    return dicts


def save_database(poi_id, data, collection):
    lists = data['list']
    documents = []
    for i in lists:
        dicts = getdata(i, poi_id)
        spec = re.sub(' ', '', i['food']['spec'].rsplit('(')[0])
        name = re.sub('@', '', i['food']['wmSkuName'])
        # doc = collection.find_one({"name": name, 'spec': spec})
        # print(i['food']['wmSkuName'][:-1], spec)
        if collection.find_one({"name": name, 'spec': spec}):
            collection.update_one({"name": name, 'spec': spec},
                                  {'$set': dicts})
            continue
    #     documents.append(dicts)
    # if len(documents):
    #     collection.insert_many(documents)


def updata_add(collection_act, name, poi_id, cookie):
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
    num = 0
    while 3 > num:
        try:
            response = requests.post(url, headers=headers, data=set_post_data1(name, poi_id),
                                     params=query_params, timeout=4)
            if response.status_code == 200:
                # print(response.text)
                json_data = response.json()['data']
                if len(json_data['list']):
                    # pass
                    save_database(poi_id, json_data, collection_act)
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


def delete_product(collection, actid, cookie):
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

    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/disable'

    num = 0
    while 3 > num:
        try:
            response = requests.post(url, headers=headers, data=data, params=query_params)
            print(response.text)
            if response.status_code == 200:
                json_data = response.json()
                # if json_data['msg'] == ''
                actids = actid.split(',')
                for i in actids:
                    if i:
                        collection.update_one({'actId': int(i)}, {"$set": {"actId": '', "errMsg": ''}})
            break
        except Exception as e:
            print(e)
            num += 1


def del_actproduct(collect_act, name):
    acts = collect_act.find({"name": name})
    actid = ''
    if acts:
        for i in acts:
            if 'actId' in i and i['actId'] != '' or i['errMsg'] != '':
                if i['actId']:
                    actid += str(i['actId']) + ','

    return actid


def yichangtianjia(collect_act, name, cookie, tem=1):
    flog = 0
    if tem:
        for p in collect_act.find({'name': name}):
            if p['errMsg'] == '7天内上调过价格不可设置活动':
                return 1
    for p in collect_act.find({'name': name}):
        if 'actPrice' in p:
            # print(p)
            flog = add_acct(p, cookie)
    return flog


def rep_pro(poi_id, df, cookie, result):
    # result = set()
    client = MongoClient('mongodb://localhost:27017/')
    db = client[poi_id]
    collect_pro = db["prodata"]
    collect_act = db["proact"]

    for i, data in df.iterrows():
        name_x = data.iloc[0]
        act_name_x = data.iloc[1]

        name_y = data.iloc[2]
        act_name_y = data.iloc[3]
        print(poi_id, "开始替换", name_x, name_y)
        if pd.isnull(act_name_y) or act_name_y == '':
            act_name_y = name_y
        if pd.isnull(act_name_x) or act_name_x == '':
            act_name_x = name_x
        doc_x = collect_pro.find_one({'name': name_x})
        doc_y = collect_pro.find_one({'name': name_y})
        if not doc_y or not doc_x:
            print('店铺没有商品')
            result.add('店铺没有商品')
            raise ValueError('店铺没有商品')

        save_act_data(doc_x['proid'], poi_id, cookie)
        save_act_data(doc_y['proid'], poi_id, cookie)

        actid_x = del_actproduct(collect_act, act_name_x)
        actid_y = del_actproduct(collect_act, act_name_y)

        print(actid_x)
        print(actid_y)
        if actid_x:
            delete_product(collect_act, actid_x, cookie)
        if actid_y:
            delete_product(collect_act, actid_y, cookie)

        time.sleep(1)
        flog1 = 0
        flog2 = 0

        flog1 += save(collect_pro, doc_x, doc_x, poi_id, name_x[:-2] + '@', cookie, result)
        print(name_x[:-2] + "@ 完成")
        flog1 += save(collect_pro, doc_x, doc_y, poi_id, name_x, cookie, result)
        print(f"{name_y}--->{name_x} 完成")
        flog2 += save(collect_pro, doc_y, doc_x, poi_id, name_y, cookie, result)
        print(f"{name_x}--->{name_y} 完成")
        if flog1:
            print("报错还原")
            result.add(f'请检查“{name_x}”的折扣名有没有错')
            save(collect_pro, doc_x, doc_x, poi_id, name_x, cookie, result)
        elif flog2:
            print("报错还原")
            result.add(f'请检查“{name_y}”的折扣名有没有错')
            save(collect_pro, doc_y, doc_y, poi_id, name_y, cookie, result)
            save(collect_pro, doc_x, doc_x, poi_id, name_x, cookie, result)
        else:
            collect_pro.update_one({"name": name_x}, {"$set": {
                "proid": doc_y['proid']
            }})
            collect_pro.update_one({"name": name_y}, {"$set": {
                "proid": doc_x['proid']
            }})
        time.sleep(4)
        doc_x = collect_pro.find_one({'name': name_x})

        doc_y = collect_pro.find_one({'name': name_y})

        add_updata(doc_x, collect_act, poi_id, name_x, act_name_x, cookie)

        add_updata(doc_y, collect_act, poi_id, name_y, act_name_y, cookie)

        print(name_x)
        flog_x = yichangtianjia(collect_act, name_x, cookie)
        if flog_x:
            result = set()
            saveAct(collect_act, doc_x, doc_x, poi_id, name_x, cookie, result)
            if len(result):
                print(result)
            flog_x = yichangtianjia(collect_act, name_x, cookie, 0)
            save(collect_pro, doc_x, doc_x, poi_id, name_x, cookie, result)

        print(name_y)
        flog_y = yichangtianjia(collect_act, name_y, cookie)
        if flog_y:
            result = set()
            saveAct(collect_act, doc_y, doc_y, poi_id, name_y, cookie, result)
            if len(result):
                print(result)
            flog_y = yichangtianjia(collect_act, name_y, cookie, 0)
            save(collect_pro, doc_y, doc_y, poi_id, name_y, cookie, result)

        time.sleep(1)
        updata_add(collect_act, name_x, poi_id, cookie)
        updata_add(collect_act, name_y, poi_id, cookie)

        add_updata(doc_x, collect_act, poi_id, name_x, name_x, cookie)
        add_updata(doc_x, collect_act, poi_id, name_y, name_y, cookie)
    return result
    # document = collect_act.find_one({'name': name_x})


if __name__ == '__main__':
    '''
    💥飞舞青春~创意蝶舞奶油生日蛋糕
    动物奶油零卡糖木糖醇选择

    failList

    '''

    poi_id = '11199362'
    cookie = "wm_order_channel=default; swim_line=default; utm_source=; WEBDFPID=zz364z653321562y0226u035wy124w4780892u35zy997958z546xy50-2037775463940-1722415462888CKWCUAMfd79fef3d01d5e9aadc18ccd4d0c95079811; iuuid=4B73777D2D5F22EC75E9DC73ECA620FEC9647DB7C4ECAB2B84ECF45F4F93EBBF; _lxsdk_cuid=1910b815d0dc8-07b8a26ad21e4f-4c657b58-1fa400-1910b815d0dc8; _lxsdk=4B73777D2D5F22EC75E9DC73ECA620FEC9647DB7C4ECAB2B84ECF45F4F93EBBF; device_uuid=!23251eaf-a663-4c28-8869-62b74ec5ea7f; uuid_update=true; acctId=97786666; token=0ok4g26IuIQK8gK8v0p-RC460MfVBD_KZxkogAHBL5t8*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=wICMFP3BXUb1fLKXE9A5cSmcdd1LCjX_3JN17GR3BMcMxtAjBzV4frYe91f7FP0Wn06CnQsYSYiiFD59gFqgYw; city_location_id=0; location_id=0; has_not_waimai_poi=0; onlyForDaoDianAcct=0; cityId=440300; provinceId=440000; pushToken=0ok4g26IuIQK8gK8v0p-RC460MfVBD_KZxkogAHBL5t8*; isOfflineSelfOpen=0; wmPoiId=11199362; wmPoiName=SweetCake%E7%BD%91%E7%BA%A2%E5%88%9B%E6%84%8F%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E4%B8%89%E6%9E%97%E5%BA%97%EF%BC%89; logistics_support=; set_info_single=%7B%22regionIdForSingle%22%3A%221000310100%22%2C%22regionVersionForSingle%22%3A1615358295%7D; shopCategory=food; wpush_server_url=wss://wpush.meituan.com; set_info=%7B%22wmPoiId%22%3A11199362%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=sann9n1s4mfrjl4kzdej; _lxsdk_s=1914f757e87-da2-53a-289%7C97786666%7C254"

    df = pd.read_excel(r'C:\Users\Admin\Downloads\replaceTemp (5).xlsx')
    result = set()
    rep_pro(poi_id, df, cookie, set())
    print(result)

"""
不止是今天，每一天，💗
我都很爱您！
唯有您在，我才是孩子！🍇

"""
