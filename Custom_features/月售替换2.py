from pymongo import MongoClient
import requests
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


def set_post_data(startTime, endTime, poiId, wmSkuId, wmSpuId, originPrice, actPrice, daylimit, orderLimit):
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
                "orderLimit": orderLimit,
                "dayLimit": daylimit,
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
                              document['spuId'], document['originPrice'], document['actPrice'],
                              document['daylimit'], document['orderLimit'])

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


def updata_data(collection, porid, name, spec, actid, errMsg, spuId, skuId, price, tagName):
    spec = spec.split('(')[0]
    # act_name = re.sub('@', '', act_name)
    count1 = collection.count_documents({"spuId": porid})

    if count1 == 1:
        collection.update_one({"spuId": porid},
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
        collection.update_one({"spuId": porid, "spec": spec},
                              {"$set": {
                                  "name": name,
                                  "actId": actid,
                                  "errMsg": errMsg,
                                  'spuId': spuId,
                                  "skuId": skuId,
                                  "tagName": tagName,
                                  "originPrice": price
                              }})


def add_updata(doc, collection, poid, name, proid, cookie):
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

            if not int(j['spuId']) == proid:
                continue
            for k in j['skuList']:
                actid = k['mutexActId']
                updata_data(collection, proid, name, k['spec'], actid, k['errMsg'], j['spuId'], k['id'],
                            k['price'], doc['tagName'])


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


# 定义一个函数，用于获取数据
def getdata(i, poi_id):
    # 从字典中提取数据，并去除空格
    spec = re.sub(' ', '', i['food']['spec'].split('(')[0])
    # 创建一个字典，存储提取的数据
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
    # 返回字典
    return dicts


def save_database(poi_id, data, collection):
    lists = data['list']
    documents = []
    for i in lists:
        dicts = getdata(i, poi_id)
        spec = re.sub(' ', '', i['food']['spec'].split('(')[0])
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
    # 定义URL
    url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/list'
    # 定义GET查询参数
    query_params = {
        'actType': '17',
        'source': 'pc',
        'yodaReady': 'h5',
        'csecplatform': '4',
        'csecversion': ' 2.4.0',
    }

    # 定义请求头
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


def del_actproduct(collect_act, porid):
    acts = collect_act.find({"spuId": porid})
    actid = ''
    if acts:
        for i in acts:
            if 'actId' in i and i['actId'] != '' or i['errMsg'] != '':
                if i['actId']:
                    actid += str(i['actId']) + ','

    return actid


def yichangtianjia(collect_act, porid, cookie, tem=1):
    flog = 0
    if tem:
        for p in collect_act.find({'spuId': porid}):
            if p['errMsg'] == '7天内上调过价格不可设置活动':
                return 1
    for p in collect_act.find({'spuId': porid}):
        if 'actPrice' in p:
            # print(p, name)
            flog = add_acct(p, cookie)
    return flog


def rep_pro(poi_id, name_x, name_y, cookie, result):
    # result = set()
    client = MongoClient('mongodb://localhost:27017/')
    db_pro = client['test']
    db_act = client['actproduct']
    collect_pro = db_pro[poi_id]
    collect_act = db_act[poi_id]

    doc_x = collect_pro.find_one({'name': name_x})
    doc_y = collect_pro.find_one({'name': name_y})
    if not doc_y or not doc_x:
        print('店铺没有商品')
        result.add('店铺没有商品')
        raise ValueError('店铺没有商品')

    porid_x = doc_x['proid']
    porid_y = doc_y['proid']

    save_act_data(porid_x, poi_id, cookie)
    save_act_data(porid_y, poi_id, cookie)

    actid_x = del_actproduct(collect_act, porid_x)
    actid_y = del_actproduct(collect_act, porid_y)

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
    print(f"{name_y}改{name_x} 完成")
    flog2 += save(collect_pro, doc_y, doc_x, poi_id, name_y, cookie, result)
    print(f"{name_x}改{name_y} 完成")
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

        actdocx = [i for i in collect_act.find({"spuId": porid_x})]
        actdocy = [i for i in collect_act.find({"spuId": porid_y})]

        for doc in actdocx:
            collect_act.update_one({"name": doc['name'], "spec": doc['spec']}, {"$set": {"spuId": porid_y}})
        for doc in actdocy:
            collect_act.update_one({"name": doc['name'], "spec": doc['spec']}, {"$set": {"spuId": porid_x}})

    # time.sleep(4)
    doc_x = collect_pro.find_one({'name': name_x})
    doc_y = collect_pro.find_one({'name': name_y})

    porid_x = doc_x['proid']
    porid_y = doc_y['proid']

    add_updata(doc_x, collect_act, poi_id, name_x, porid_x, cookie)
    add_updata(doc_y, collect_act, poi_id, name_y, porid_y, cookie)

    print(name_x)
    flog_x = yichangtianjia(collect_act, porid_x, cookie)
    if flog_x:
        result1 = set()
        saveAct(collect_act, doc_x, doc_x, poi_id, name_x, cookie, result)
        if len(result1):
            print(result1)
        flog_x = yichangtianjia(collect_act, porid_x, cookie, 0)
        save(collect_pro, doc_x, doc_x, poi_id, name_x, cookie, result)

    print(name_y)
    flog_y = yichangtianjia(collect_act, porid_y, cookie)
    if flog_y:
        result1 = set()
        saveAct(collect_act, doc_y, doc_y, poi_id, name_y, cookie, result)
        if len(result1):
            print(result1)
        flog_y = yichangtianjia(collect_act, porid_y, cookie, 0)
        save(collect_pro, doc_y, doc_y, poi_id, name_y, cookie, result)

    time.sleep(1)
    updata_add(collect_act, porid_x, poi_id, cookie)
    updata_add(collect_act, porid_y, poi_id, cookie)

    add_updata(doc_x, collect_act, poi_id, name_x, porid_x, cookie)
    add_updata(doc_x, collect_act, poi_id, name_y, porid_y, cookie)
    return result
    # document = collect_act.find_one({'name': name_x})


if __name__ == '__main__':
    '''
    💥飞舞青春~创意蝶舞奶油生日蛋糕
    动物奶油零卡糖木糖醇选择

    failList

    '''
    result = set()
    cookie = "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; wm_order_channel=appshare1; utm_source=5913; _ga_NMY341SNCF=GS1.3.1716602003.3.1.1716603712.0.0.0; acctId=97786666; token=0h5rLEuzGbvrUwVItsXSXMCSwA8bztdSyp7cDR9g4SwQ*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=2VtwEpD5fdEW_dtACPxV1b05QiNPZQGGo02BBp8RDvaI3NB0yb3dE0mi1cpOaTnF6jXq_8aEl07b2Ks2XORrVg; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; swim_line=default; oops=AgEDJP87Lagf480BSkg0e-TouAZnaFTzZS3UcSCP07bhTsfPRLJFit-KvzKtRzno0QCnIYbbpi1aYgAAAADIIAAAxADcf9SQ9fl3e22SjlA7BzOL3OmYyinw8Tx2l24yMPMwDCvhDFDc_JGOt8bdb2gK; userId=1616653911; _lx_utm=utm_source%3D5913; isOfflineSelfOpen=0; logistics_support=; JSESSIONID=1fcdxba5ci968sqm1n22zkben; setPrivacyTime=2_20240619; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=f6a1cbxbyavrqwrausmy; _lxsdk_s=1902d47cbef-b18-479-6d1%7C97786666%7C2338"

    rep_pro('19021228', '测试商品2', '测试商品', '', '', cookie, result)

"""
不止是今天，每一天，💗
我都很爱您！
唯有您在，我才是孩子！🍇

"""
