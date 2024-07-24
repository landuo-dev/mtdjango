import asyncio
import aiohttp
import time
import pandas as pd
import requests
from pymongo import MongoClient
import json
import traceback
import re

from Custom_features.setting import set_bb


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


async def main02(df, cookie, poi_id, result):
    url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
    # result = set()
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
    db = client['test']

    if not str(poi_id) in db.list_collection_names():
        return '该店没入库'

    session = aiohttp.ClientSession()
    err = 0
    names = set()
    for i, data in df.iterrows():
        flog = ''

        try:
            try:
                # poi_id = int(data.iloc[0])
                # single positional indexer is out-of-bounds
                collection = db[str(poi_id)]
                name = data.iloc[2]
                product_info = str(data.iloc[3])
                if product_info == 'nan':
                    product_info = ''
            except Exception as e:
                print(data.iloc[2])
                print(i)
                print(e)
                result.add(data.iloc[2])
                continue
            document = collection.find_one({"name": name})
            description = data.iloc[4] if not pd.isna(data.iloc[4]) else document.get('description', '')
            if not document:
                print(i)
                print("该店铺没有商品", name)
                result.add(f"该店铺没有商品 {data.iloc[2]}")
                continue

            bb, updatadatabase = set_bb(poi_id, document, description, name, product_info)
            names.add(name)
            wmFoodVoJson02 = [bb]
            post_data = {
                'wmPoiId': poi_id,
                'entranceType': 2,
                'userType': 0,
                'wmFoodVoJson': json.dumps(wmFoodVoJson02)
            }

            num = 0

            while 3 > num:
                json_data = await fetch_data(session, url, headers, post_data, name)
                if json_data is None:
                    collection.update_one({"name": name}, {"$set": {"attrList02": updatadatabase}})
                    err = 0
                    break  # 如果请求成功或不需要重试，则跳出循环
                if json_data['msg'] == "参加活动商品无法修改，请先将商品下掉活动":
                    print(name, json_data['msg'])
                    result.add(f"{json_data['msg']} -->{name}")
                    err = 0
                    break
                print(json_data['msg'], name)
                print(i)  # 确保i在此上下文中已定义
                num += 1
                err += 1
                flog = f"{json_data['msg']} -->{name}"

                if err >= 30:
                    await session.close()
                    return "0"
                await asyncio.sleep(1)

        except Exception as e:
            # traceback.print_exc()
            print(data.iloc[2])
            result.add(data.iloc[2])
            print(i)
            print(e)

        result.add(flog)
    # print(names)
    await session.close()

    return result

# if __name__ == '__main__':
#     # Python 3.7及以上版本，可以直接运行
#     poiId = 19021228菜
#     df = pd.read_excel(r'G:\updata\夹心\19021228.xlsx')
#     asyncio.run(main02(df,
#                        "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; _lxsdk=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; acctId=97786666; token=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=rbAzQ0FErd8OINAT34hV7Qd4dhEeLPTSYalMD3CsvtDc4jcw_4QgBIJyu8LGpNlRLJCSpNy7sGhVki1h8xZ_kA; city_location_id=0; location_id=0; cityId=440300; provinceId=440000; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; wmPoiId=19021228; isOfflineSelfOpen=0; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; logistics_support=; shopCategory=food; wpush_server_url=wss://wpush.meituan.com; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=wbm6p52l3dke8mwrwk43; _lxsdk_s=18f4127f7ef-90-e2e-8c3%7C%7C104",
#                        poiId))
