import io
import re
import time

import pandas as pd
import requests
import json
from pymongo import MongoClient
import os
import urllib.parse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from Custom_features.折扣价格输出excel import get_exl


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
    spec = re.sub(' ', '', i['food']['spec'].rsplit('(')[0])
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
        spec = re.sub(' ', '', i['food']['spec'].rsplit('(')[0])
        if collection.find_one({"name": i['food']['wmSkuName'], 'spec': spec}):
            collection.update_one({"name": i['food']['wmSkuName'], 'spec': spec},
                                  {'$set': dicts})
            result += f"已有商品{i['food']['wmSkuName']}, 更新数据{i['food']['wmSkuName']}--->"
            continue
        documents.append(dicts)
    if len(documents):
        collection.insert_many(documents)


def main1(poi_id, cookie):
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/list'
    result = ''
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

    ecl_url = get_exl(poi_id, cookie)
    print(ecl_url, 'sss')
    if not ecl_url:
        # main1_new(poi_id, cookie)
        return "0"
    num = 0
    while 4 > num:
        try:
            time.sleep(2)
            if ecl_url:
                response = requests.get(ecl_url, headers=headers)
                with io.BytesIO(response.content) as file:
                    # 使用pandas读取Excel文件
                    df = pd.read_excel(file)
                    break
        except Exception as e:
            print(e)
            num += 1

    if num == 4:
        raise '文件获取失败'

    arr = df.iloc[:, 3].to_list()
    arr = set([i.rsplit('-')[0] for i in arr])
    db_act = client[str(poi_id)]
    collection_act = db_act["proact"]
    collection_act.drop()
    for name in arr:
        # print(i['name'])
        # print(name)
        num = 0
        while 3 > num:
            try:
                response = sess.post(url, data=set_post_data(str(name), poi_id))
                # print(response.text)
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


def main1_new(poi_id, cookie):
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/list'
    result = ''
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
    db = client[str(poi_id)]
    collection = db["prodata"]
    collection_act = db["proact"]
    for i in collection.find():
        # print(i['name'])
        num = 0
        while 5 > num:
            try:
                response = sess.post(url, data=set_post_data(i['name'], poi_id))
                if response.status_code == 200:
                    json_data = response.json()['data']
                    if len(json_data['list']):
                        save_database(poi_id, json_data, collection_act, result)
                    break
                else:
                    print(f'连接失败， 正在重新尝试第{num}次', i['name'])
                    num += 1
                    time.sleep(1)
            except Exception as e:
                print(e, i['name'])
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
                                       "spec": spec,
                                       "daylimit": -1,
                                       "orderLimit": -1,
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
    db = client[str(poid)]
    collection = db["proact"]
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
                        spec = re.sub(' ', '', k['spec'].rsplit('(')[0])
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
                                "daylimit": -1,
                                "orderLimit": -1,


                            })
                        else:
                            # pass
                            updata_data(collection, k['skuName'], spec, actid, k['errMsg'], j['spuId'], k['id'],
                                        i['name'])
            else:
                raise '入库失败'
    else:
        print('店铺标签获取失败')
        raise '入库失败'

    if len(document):
        collection.insert_many(document)
        collection.create_index([("name", 1), ("spce", -1)])

    return result


if __name__ == '__main__':
    poi_id = 23879028
    cookie = "cityId=440300; provinceId=440000; set_info_single=%7B%22regionIdForSingle%22%3A%221000371000%22%2C%22regionVersionForSingle%22%3A1720752251%7D; WEBDFPID=u296zw08x74u58u8z23v858370v74093809ww6316ww9795801zw6116-2037058254592-1721698254592WCQCGCKfd79fef3d01d5e9aadc18ccd4d0c95073741; _lxsdk_cuid=19134c8e7a3c8-021b7552ff292b-133b483a-1fa400-19134c8e7a3c8; _lxsdk=0501F1C16F9EC2AB4B749FF5766F8B9D93C412755BB75547AEE0191CE5F844CB; brandId=-1; existBrandPoi=true; newCategory=false; uuid_update=true; acctId=97786666; isOfflineSelfOpen=0; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; city_location_id=0; location_id=0; has_not_waimai_poi=0; onlyForDaoDianAcct=0; logistics_support=; _lxsdk=0501F1C16F9EC2AB4B749FF5766F8B9D93C412755BB75547AEE0191CE5F844CB; device_uuid=!97987721-9691-478a-844b-ae172b287226; pushToken=0QTN2mbmo6ODKnRvW5cQOQIwGJtkc2aVP_C1bUYEA-HI*; iuuid=0501F1C16F9EC2AB4B749FF5766F8B9D93C412755BB75547AEE0191CE5F844CB; ci=30; cityname=%E6%B7%B1%E5%9C%B3; token=0ialZk6VupyxYtjXobEvLLZvKp01k2GXK3Pfkl6adm38*; bsid=tMvsyTRsRTaF2vGqsXlfSzzaj3W6aTRKQLt_FXBqkwLFBMyY19Aqt6I_lSDYLsMKYh1Z7V_VPNXIJmNySKv_tA; wmPoiId=23879028; wmPoiName=%E5%96%9C%E6%A3%A0Cake%E7%94%9F%E6%97%A5%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6(%E5%A8%81%E6%B5%B7%E5%BA%97); shopCategory=food; JSESSIONID=11rkgfu0korqs1opliehvn0idm; setPrivacyTime=3_20240813; wpush_server_url=wss://wpush.meituan.com; set_info=%7B%22wmPoiId%22%3A23879028%2C%22ignoreSetRouterProxy%22%3Atrue%7D; WEBDFPID=x4yu36uvy7225u6y1u228329z8z8523v8098vv684y8979581z8y4142-2033865114822-1718505114822EIOUGQKfd79fef3d01d5e9aadc18ccd4d0c95073918; _lxsdk_cuid=18f7085f26ac8-055ac2e62b074d-26001a51-1fa400-18f7085f26bc8; _lxsdk_s=191300411b2-75f-77a-7a1%7C%7C24359; logan_session_token=t1h1j4gvpovq1sco7qt4; _lxsdk_s=191300411b2-75f-77a-7a1%7C%7C24360; _lxsdk_s=191300411b2-75f-77a-7a1%7C%7C24360; _lxsdk_s=191300411b2-75f-77a-7a1%7C%7C24360"

    main1(poi_id, cookie)
    print('任务1完成')
    main02(poi_id, cookie)
    print('完成')
