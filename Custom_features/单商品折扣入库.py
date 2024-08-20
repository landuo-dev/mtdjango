import requests
from pymongo import MongoClient
import re

from Custom_features.setting import while_fun


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
    spec = i['food']['spec'].split('(')[0]
    dicts = {
        'weeksTime': i['weeksTime'],
        'period': i['period'],
        'poiId': poi_id,
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


def save_act_data(proid, poi_id, cookie):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[str(poi_id)]
    collec = db['proact']
    doc = collec.find_one({"spuId": proid})
    # print(doc)
    name = doc.get('name', 0)
    if not name:
        raise ValueError('输入的数据有误，请重新输入')

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

    response = while_fun(requests.post, url=url, headers=headers, data=set_post_data(doc['name'], str(poi_id)),
                         params=query_params)
    json_data = response.json()['data']['list']

    # print(json_data)
    for i in json_data:
        # print(i)
        name = i['food']['wmSkuName']
        spec = i['food']['spec'].split('(')[0]
        dicts = getdata(i, str(poi_id))
        # if not spec:
        #     continue

        count1 = collec.count_documents({"spuId": proid})
        # print(count1)
        if count1 == 1:
            if collec.find_one({"spuId": proid}):
                collec.update_one({"name": name, 'spec': spec},
                                  {'$set': dicts})
        elif count1 > 1:
            if collec.find_one({"spuId": proid, "spec": spec}):
                collec.update_one({"name": name, 'spec': spec},
                                  {'$set': dicts})
        else:
            collec.insert_one(dicts)


if __name__ == '__main__':
    name = '测试商品'
    poi_id = '19021228'
    cookie = "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; wm_order_channel=appshare1; utm_source=5913; _ga_NMY341SNCF=GS1.3.1716602003.3.1.1716603712.0.0.0; acctId=97786666; token=0h5rLEuzGbvrUwVItsXSXMCSwA8bztdSyp7cDR9g4SwQ*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=2VtwEpD5fdEW_dtACPxV1b05QiNPZQGGo02BBp8RDvaI3NB0yb3dE0mi1cpOaTnF6jXq_8aEl07b2Ks2XORrVg; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; swim_line=default; oops=AgEDJP87Lagf480BSkg0e-TouAZnaFTzZS3UcSCP07bhTsfPRLJFit-KvzKtRzno0QCnIYbbpi1aYgAAAADIIAAAxADcf9SQ9fl3e22SjlA7BzOL3OmYyinw8Tx2l24yMPMwDCvhDFDc_JGOt8bdb2gK; userId=1616653911; isOfflineSelfOpen=0; logistics_support=; au_trace_key_net=default; openh5_uuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; isIframe=false; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; JSESSIONID=4n7cp52j0m5q1t5cr2chnnik4; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=t97466sicyu4l5xnjl93; _lxsdk_s=19049579c90-e0c-c9d-43a%7C%7C1030"

    save_act_data(15513051818, poi_id, cookie)
    # save_act_data(name, poi_id, cookie)
    '''
    exceptions must derive from BaseException

    '''
