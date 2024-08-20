import time
import traceback
import pandas as pd
import requests
from pymongo import MongoClient
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# from config import headers2, headers1


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
                "originPrice": originPrice,
                "actPrice": actPrice,
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
    num = 0
    while 3 > num:
        try:
            response = requests.get(url, params=quer_data, headers=headers, timeout=5)
            if response.status_code == 200:
                json_data = response.json()
                # print(f'获取{tagname}数据成功')
                return json_data
            break
        except RuntimeError:
            print('超时重试')
            num += 1
            time.sleep(1)
        except Exception:
            num += 1
            time.sleep(1)

    return None

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
    response = requests.post(url, headers=headers, data=set_post_data2(name, poi_id),
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


def main(new_poi_id, old_poi_id, cookie, result):
    # result = set()
    client = MongoClient('mongodb://localhost:27017/')
    db_old = client[str(old_poi_id)]
    db_new = client[str(new_poi_id)]
    collection_old = db_old["proact"]
    collection_new = db_new["proact"]
    collection_test = db_old["prodata"]

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
    for i in collection_old.find():
        k += 1

        if "errMsg" in i and i['errMsg'] == "":
            continue
        try:
            document_old = collection_test.find_one({'proid': i['spuId']})
            name = document_old['name']
            spec = i['spec']
            price = i['actPrice']
        except Exception as e:
            print(e)
            result.add(f"基础信息没有找到 {i['name']}， {i['spec']}")
            continue
        document_new = collection_new.find_one({"name": name, "spec": spec})
        # print(document_new)
        if document_new and 'errMsg' in document_new and document_new['errMsg'] == '':
            actlist.append(set_foods(document_new['skuId'], document_new['spuId'], document_new['originPrice'], price))
        else:
            print("店铺没有商品", name, spec)
            result.add(f'新店没有商品 {name}')
            continue
        if k >= 30:
            if not len(actlist):
                k = 0
                continue
            starttime, endtime = get_time()
            num = 0
            flog = ''
            while 3 > num:
                try:
                    post_data = set_post_data(starttime, endtime, new_poi_id, actlist)
                    response = session.post(url, json=post_data)
                    if response.status_code == 200:
                        json_data = response.json()
                        print(json_data)
                        if json_data['msg']:
                            print(json_data['msg'])
                            flog = json_data['msg']
                            num += 1
                            time.sleep(1)
                            continue
                        del actlist
                        actlist = []
                        k = 0
                        break
                except TimeoutError:
                    print('超时了')
                    num += 1
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    num += 1
                    time.sleep(1)
            if num == 3:
                result.add(f'{flog}-->{name}')
    return result


if __name__ == '__main__':
    cookie = "_lxsdk_cuid=18dfcce628cc8-0882cdb9e0b95e-26001b51-1fa400-18dfcce628cc8; _lxsdk=18dfcce628cc8-0882cdb9e0b95e-26001b51-1fa400-18dfcce628cc8; device_uuid=!56a54be6-5f9f-444a-a6ff-cced5f2a194b; uuid_update=true; pushToken=0EAybFBHus01vbIzx8kete7YiEfD_tK5okUJpL_lc-E0*; WEBDFPID=18792605781x5z4z120y232v5u881v9x81v88367948979581x8v1867-2025048690330-1709688690330IASUUSWfd79fef3d01d5e9aadc18ccd4d0c95078727; acctId=160721552; token=0fDTf42mzhMEs35UUSk8xzHnhSbKUrgsPIg7A1BCNy6E*; wmPoiId=21390439; isOfflineSelfOpen=1; city_id=440300; isChain=0; ignore_set_router_proxy=false; region_id=1000440300; region_version=1715169772; bsid=qTC-G24i-Wx6n39buSmUULfAj3p0M32OsN_xXFU2S7pSE-HiaqHgwSXu_BCCSgeE4-ZqtmWp0WFxPi2rW_Sdhw; city_location_id=440300; location_id=10000018; has_not_waimai_poi=0; cityId=440300; provinceId=440000; set_info=%7B%22wmPoiId%22%3A%2221390439%22%2C%22region_id%22%3A%221000440300%22%2C%22region_version%22%3A1715169772%7D; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; JSESSIONID=wd4y5jr7prskk6gwi7a6ij5z; logan_session_token=4wptajjw14omf9h0kdcz; _lxsdk_s=18f5bebc630-3b2-572-8bc%7C160721552%7C184"

    new_poid = '21390439'
    old_poid = '21061151'
    main(new_poid, old_poid, cookie)

    # '''
    # 15678783
    # 戴安娜玫瑰🌟卡布奇诺浪漫氛围感生日蛋糕
    # '''
