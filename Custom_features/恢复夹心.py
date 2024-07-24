import asyncio
import aiohttp
import time
import pandas as pd
import requests
from pymongo import MongoClient
import json
import traceback
import re

from Custom_features.set_yuan_bb import set_post_data


async def fetch_data(session, url, headers, post_data, name):
    try:
        async with session.post(url, headers=headers, data=post_data) as response:
            if response.status != 200:
                raise Exception(f"HTTP Error {response.status}")
            json_data = await response.json()
            print(json_data, '夹心')
            if json_data.get('msg') != 'success':
                return json_data
            # print(json_data)
            return None
    except Exception as e:
        return None


async def Recover(back_poi_id, poi_id, cookie):
    url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
    result = set()
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

    # 创建 MongoDB 客户端
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    test = client['test']
    back = client['back_up_jx']
    back_collection = back[str(back_poi_id)]
    collection = test[str(poi_id)]
    if not str(poi_id) in test.list_collection_names():
        return '该店没入库'

    session = aiohttp.ClientSession()
    err = 0
    for doc in collection.find():
        try:
            name = doc['name']
            document = collection.find_one({"name": name})
            back_document = back_collection.find_one({"name": name})
            if not document:
                print("该店铺没有商品", name)
                result.add(f"该店铺没有商品 {name}")
                continue

            post_data = set_post_data(poi_id, back_document, back_document, back_document['name'])

            num = 0
            while 3 > num:
                json_data = await fetch_data(session, url, headers, post_data, name)
                if json_data is None:

                    err = 0
                    break  # 如果请求成功或不需要重试，则跳出循环
                if json_data['msg'] == "参加活动商品无法修改，请先将商品下掉活动":
                    print(name, json_data['msg'])
                    result.add(f"{json_data['msg']} -->{name}")
                    err = 0
                    break
                print(json_data['msg'], name)

                num += 1
                err += 1
                result.add(f"{json_data['msg']} -->{name}")
                if err >= 30:
                    await session.close()
                    return "0"
                await asyncio.sleep(1)


        except Exception as e:
            # traceback.print_exc()
            print(doc['name'])
            result.add(doc['name'])
            print(e)
    await session.close()

    return result

if __name__ == '__main__':
    # Python 3.7及以上版本，可以直接运行
    poiId = '19021228'
    back_poiId = "19021228_0"
    asyncio.run(Recover(back_poiId, poiId,
                       "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; wm_order_channel=appshare1; utm_source=5913; _ga_NMY341SNCF=GS1.3.1716602003.3.1.1716603712.0.0.0; acctId=97786666; token=0h5rLEuzGbvrUwVItsXSXMCSwA8bztdSyp7cDR9g4SwQ*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=2VtwEpD5fdEW_dtACPxV1b05QiNPZQGGo02BBp8RDvaI3NB0yb3dE0mi1cpOaTnF6jXq_8aEl07b2Ks2XORrVg; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; isOfflineSelfOpen=0; logistics_support=; JSESSIONID=1k4nqasgja6qy1vy72qj6tm93t; setPrivacyTime=1_20240608; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=kttuoali91kunefimnv8; _lxsdk_s=18ff56c14da-fe5-026-323%7C%7C1294"
                        ))
