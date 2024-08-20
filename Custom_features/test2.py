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

    db_act = client[str(poi_id)]
    collection_act = db_act["proact"]
    collection_act.drop()
    db_pro = client[str(poi_id)]
    collection = db_pro["prodata"]

    documents = []
    err_list = []
    for key, value in df.iterrows():
        try:
            poi_id = str(value['门店ID'])
            skuid = value['SKUID']
            try:
                name, spec = value['商品名称-规格'].rsplit('-', 1)
            except Exception as e:
                print(e, value['商品名称-规格'])
                name = value['商品名称-规格']
                spec = '一个'
            doc = collection.find_one({"name": name})
            if name == "【七夕限定】入目无他人 四下皆是你节日蛋糕":
                print(doc)
            if not doc:
                print(f"商品不存在{name}: {name}")
                continue
            spuid = doc['proid']
            originPrice = round(float(value['商品原价']), 2)
            daylimit = value['每日库存'] if value['每日库存'] != '不限量' else -1
            orderLimit = value['每单限购'] if value['每单限购'] != '不限购' else -1
            sr1 = re.sub(' ', '', value['活动优惠'])
            # print(name, poi_id, skuid)
            discount = re.search("(.*?)折", sr1).group(1)
            actprice = round(float(re.search('-(.*?)元', sr1).group(1)), 2)

            documents.append(
                {"poiId": poi_id, "spuId": spuid, "skuId": skuid, "name": name, "spec": spec,
                 "originPrice": originPrice,
                 "actPrice": actprice, "daylimit": daylimit, "orderLimit": orderLimit, "discount": discount})
        except Exception as e:
            print(e)
            # print(value)
            err_list.append(value['商品名称-规格'].rsplit('-', 1))
    print(err_list)
    if len(documents) > 0:
        collection_act.insert_many(documents)
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
    collection = db['prodata']

    db_act = client[str(poi_id)]
    collection_act = db_act["proact"]
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
            num += 1
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
    result = collection.update_one({"spuId": spuId, "skuId": skuId},
                                   {"$set": {
                                       "actId": actid,
                                       "errMsg": errMsg,
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
                        if not actid:
                            document.append({
                                "spuId": j['spuId'],
                                "skuId": k['id'],
                                'poiId': poid,
                                'name': k['skuName'],
                                'spec': spec,
                                'originPrice': round(float(k['price']), 2),
                                'tagName': i['name'],
                                'errMsg': '',
                                "daylimit": -1,
                                "orderLimit": -1,
                            })
                        else:
                            collection.update_one({"spuId": j['spuId'], "skuId": k['id']},
                                                  {"$set": {
                                                      "actId": actid,
                                                      "errMsg": k['errMsg'],
                                                      "tagName": i['name'],
                                                      "spec": spec
                                                  }})

            else:
                raise ValueError('入库失败')
    else:
        print('店铺标签获取失败')
        raise ValueError('入库失败')

    if len(document):
        collection.insert_many(document)
        # collection.create_index([("name", 1), ("spce", -1)])
    return result


if __name__ == '__main__':
    poi_id = 24049457
    cookie = "_lxsdk_cuid=190ec99e78cc8-04af514e2bcd18-26001f51-1fa400-190ec99e78dc8; device_uuid=!2b23ba99-8d9a-4cd7-b755-ab52d7ee3a8d; uuid_update=true; acctId=203266787; token=0cZzMC398fBvQeQGT6NWna0zSMska41zcVHBcF01ZyjI*; wmPoiId=24049457; isOfflineSelfOpen=0; city_id=320200; isChain=0; ignore_set_router_proxy=false; region_id=1000320200; region_version=1721895015; bsid=oWVNDyXTGyO_rpqzTs5kky_jvDhHSOdKpa-mHHCo3LphBp_s0GTS0_d334FBsC-nbFoPheAO9hwzhazheEb2Aw; city_location_id=320200; location_id=10000016; has_not_waimai_poi=0; cityId=440300; provinceId=440000; set_info_single=%7B%22regionIdForSingle%22%3A%221000320200%22%2C%22regionVersionForSingle%22%3A1721895015%7D; set_info=%7B%22wmPoiId%22%3A%2224049457%22%2C%22region_id%22%3A%221000320200%22%2C%22region_version%22%3A1721895015%7D; pushToken=0cZzMC398fBvQeQGT6NWna0zSMska41zcVHBcF01ZyjI*; com.sankuai.fspfecap.fe.gongyibiz_strategy=; com.sankuai.fspfecap.fe.gongyibiz_random=; WEBDFPID=vv7w74y4wv505v78zy0162v6xw895563809ux4641w697958536yxy58-2037580224839-1722220224839SAEMYWSfd79fef3d01d5e9aadc18ccd4d0c95071385; _source=APP; acctName=wmlsCa945965; uuid=!2b23ba99-8d9a-4cd7-b755-ab52d7ee3a8d; igateApp=igate; _lxsdk=!2b23ba99-8d9a-4cd7-b755-ab52d7ee3a8d; JSESSIONID=1e5164dem288u1i2w8j6sp5crf; shopCategory=food; wpush_server_url=wss://wpush.meituan.com; setPrivacyTime=3_20240817; logan_session_token=2k5u9u1eb1khfrb25l1v; _lxsdk_s=191493b8ff4-d0d-5f2-7d3%7C%7C10376"
    main1(poi_id, cookie)
    print('任务1完成')
    main02(poi_id, cookie)
    print('完成')
