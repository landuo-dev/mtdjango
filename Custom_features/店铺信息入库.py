# config: utf - 8
import time

from pymongo import MongoClient
import json
import pandas as pd
import re
import requests

from Custom_features.setting import while_fun
from Custom_features.详情 import get_product as get_product_jx

def get_tag(poi_id, headers):
    data = {
        'tabStatus': '-1',
        'inRecycleBin': '0',
        'wmPoiId': poi_id,
        'appType': '3'
    }
    # 发送 POST 请求
    url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/tag/r/tagList?ignoreSetRouterProxy=true'
    # response = requests.post(url, headers=headers, data=data)
    response = while_fun(requests.post, url=url, headers=headers, data=data)
    if response.status_code == 200:
        json_data = response.json()
        if json_data['msg'] != 'success':
            print('报错了', json_data['msg'])
        else:
            return json_data['data']


def getdata(i):
    if i['name'] == "💥飞舞青春~创意蝶舞奶油生日蛋糕":
        print(i['shippingTimeX'])
    try:
        dicts = {
            'defaultPicUrl': i['wmProductPicVos'][0]['picLargeUrl'],
            'picUrl': i['wmProductPicVos'][0]['picUrl'],
            'discountPrice': i['discountPrice'],
            'discountTips': i['discountTips'],
            'proid': i['id'],
            'name': i['name'],
            'price': i['price'],
            'stock': i['stock'],
            'tagId': i['tagId'],
            'spTagId': i['spTagId'],
            'tagName': i['tagName'],
            "shippingTimeX": i['shippingTimeX'] if i['shippingTimeX'] != '' else '-',
            # 'wmProductSkuVos': i['wmProductSkuVos'],
            'wmProductLabelVos': i['wmProductLabelVos'],

        }
    except Exception as e:
        dicts = {
            'defaultPicUrl': '',
            'picUrl': '',
            'discountPrice': i['discountPrice'],
            'discountTips': i['discountTips'],
            'proid': i['id'],
            'name': i['name'],
            'price': i['price'],
            'stock': i['stock'],
            'tagId': i['tagId'],
            'spTagId': i['spTagId'],
            'tagName': i['tagName'],
            "shippingTimeX": i['shippingTimeX'] if i['shippingTimeX'] != '' else '-',
            'wmProductLabelVos': i['wmProductLabelVos'],
        }
    return dicts


def aa(poi_id, data, collection, cookie):
    spuListVos = data['data']['spuListVos']
    documents = []

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Pragma': 'no-cache',
        'Referer': 'https://e.waimai.meituan.com/gw/static_resource/product',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'spuId': '',
        'wmPoiId': poi_id,
        'clientId': '2',
        'v2': '1',
    }

    session = requests.session()
    session.headers = headers


    for i in spuListVos:
        # print(i)

        dis1 = getdata(i)
        params['spuId'] = i['id']
        session.params = params

        dis2 = get_product_jx(session)
        dis1.update(dis2)

        if collection.find_one({"name": i['name']}):
            collection.update_one({"name": i['name']}, {"$set": dis1})
        else:
            documents.append(dis1)
    if len(documents):
        collection.insert_many(documents)
        print(data['data']['spuListVos'][0]['tagName'])
        print('添加成功')
    else:
        print('没有商品')


def zz(num1, num2):
    return num1 // num2 if num1 % num2 == 0 else num1 // num2 + 1


def get_product(poi_id, cookie):
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
    url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/food/r/getSpuListCommon?ignoreSetRouterProxy=true'
    tag_data = get_tag(poi_id, headers)
    # 创建 MongoDB 客户端
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['test']
    # collection = db[str(poi_id)]
    collection = db[str(poi_id)]
    collection.drop()
    if not len(tag_data):
        print(tag_data)
        raise '标签获取失败'

    session = requests.session()
    session.headers = headers
    session.cookie = cookie

    for i in range(len(tag_data)):
        # print(tag_data[i]['name'])
        pageNum = zz(tag_data[i]['spuCount'], 90)
        for j in range(pageNum):
            data = {
                'tagId': tag_data[i]['id'],
                'pageNum': j + 1,
                'pageSize': 90,
                'needAllCount': '1',
                'tabStatus': '-1',
                'inRecycleBin': '0',
                'wmPoiId': poi_id,  # 店铺id
                'appType': '3'
            }
            num = 0
            # response = session.post(url, data=data)
            while 3 > num:
                try:
                    response = while_fun(session.post, url=url, data=data)
                    if response.status_code == 200:
                        json_data = response.json()
                        aa(poi_id, json_data, collection, cookie)
                        break
                    else:
                        print('请求失败', response.json())
                        num += 1
                        time.sleep(3)
                        continue

                except Exception as e:
                    print(e)
                    num += 1
                    time.sleep(3)
                    continue

    client.close()

# if __name__ == '__main__':
#     cookie = "_lxsdk_cuid=18f13e73a1bc8-0863beffacba6b-26001d51-1fa400-18f13e73a1bc8; _lxsdk=18f13e73a1bc8-0863beffacba6b-26001d51-1fa400-18f13e73a1bc8; device_uuid=!9368750a-9fec-47ea-ab77-3c2d60f167cb; uuid_update=true; pushToken=0Q1onnLxaMzr17UJZ8oT3p3VBm6zVC3A2BCAP_ZALirY*; WEBDFPID=z06u834w1032585uz809275vx5u9x32y81u86uv627z979584xy100y1-2029387406345-1714027406345WSWWIEAfd79fef3d01d5e9aadc18ccd4d0c95071602; acctId=193486281; shopCategory=food; token=0jhfyBdi-duTBIUeMInmR3WPIwF2bUKDYqhFtKsDV4Dg*; wmPoiId=21383154; isOfflineSelfOpen=1; city_id=370200; isChain=0; ignore_set_router_proxy=false; region_id=1000370200; region_version=1715150986; bsid=_bbJzjJNolJ3IU-A2n2SJPlY1NPwVxNuAOrdc-CemfalylduwGK3ggopebARLi4LqbIn896fowqmJNnrzUC-5g; city_location_id=370200; location_id=370211; has_not_waimai_poi=0; cityId=440300; provinceId=440000; set_info=%7B%22wmPoiId%22%3A%2221383154%22%2C%22region_id%22%3A%221000370200%22%2C%22region_version%22%3A1715150986%7D; JSESSIONID=2qywghze4y8d31sgw6ihw45a; wpush_server_url=wss://wpush.meituan.com; logan_session_token=s6hxug93bqcajyxilw6s; _lxsdk_s=18f5790ac7b-e09-8c3-611%7C%7C184"
#
#     headers = {
#         'Accept': 'application/json, text/plain, */*',
#         'Accept-Language': 'zh-CN,zh;q=0.9',
#         'Connection': 'keep-alive',
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Cookie': cookie,
#         'Origin': 'https://e.waimai.meituan.com',
#         'Referer': 'https://e.waimai.meituan.com/gw/static_resource/product',
#         'Sec-Fetch-Dest': 'empty',
#         'Sec-Fetch-Mode': 'cors',
#         'Sec-Fetch-Site': 'same-origin',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
#         'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
#         'sec-ch-ua-mobile': '?0',
#         'sec-ch-ua-platform': '"Windows"'
#         # ... 其他 headers 字段
#     }
#
#     get_product("21383154", cookie)
