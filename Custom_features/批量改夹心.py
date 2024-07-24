# import asyncio
# import aiohttp
import time
import pandas as pd
import requests
from pymongo import MongoClient
import json
import traceback
import re

# from config import headers1 as headers
from Custom_features.setting import while_fun
from Custom_features.setting import set_attribute, set_wmProductSkuVos


def main02(df, cookie, poi_id):
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
    db = client['test']

    if not str(poi_id) in db.list_collection_names():
        return '该店没入库'

    session = requests.session()
    session.headers = headers
    session.cookie = cookie

    err = 0
    for i, data in df.iterrows():
        try:
            try:
                # poi_id = int(data.iloc[0])
                collection = db[str(poi_id)]
                name = data.iloc[2]
                product_info = str(data.iloc[3])
                if product_info == 'nan':
                    product_info = ''
                description = str(data.iloc[4])
                if description == 'nan':
                    description = ''
            except Exception as e:
                print(data.iloc[2])
                print(i)
                print(e)
                result.add(data.iloc[2])
                continue
            document = collection.find_one({"name": name})
            if not document:
                print(i)
                print("该店铺没有商品", name)
                result.add(f"该店铺没有商品 {data.iloc[2]}")
                continue
            attributes, updatadatabase = set_attribute(product_info, attrs=document['attrList01'])
            # if name == "金榜题名 前程   似锦 毕业季蛋糕":
            #     print(attributes)
            #     break
            # break
            # print(attributes)
            # return 0


            wmFoodVoJson02 = [bb]
            post_data = {
                'wmPoiId': poi_id,
                'entranceType': 2,
                'userType': 0,
                'wmFoodVoJson': json.dumps(wmFoodVoJson02)
            }

            res = while_fun(session.post, url=url, headers=headers, data=post_data, timeout=(5, 5))
            # print(res)
            if res:
                json_data = res.json()
                if json_data.get('msg') == 'success':
                    print(json_data, '夹心')
                    collection.update_one({"name": name}, {"$set": {"attrList02": updatadatabase}})
                    errr = 0
                if json_data['msg'] == "参加活动商品无法修改，请先将商品下掉活动" or json_data['msg'] == "请勿重复提交":
                    print(name, json_data['msg'])
                    result.add(f"{json_data['msg']} -->{name}")
                    err = 0

                err += 1
            else:
                result.add(f"添加失败 -->{name}")
                if err >= 10:
                    raise "错误"

        except Exception as e:
            # traceback.print_exc()
            print(data.iloc[2])
            result.add(data.iloc[2])
            print(i)
            print(e)

    return result


if __name__ == '__main__':
    # Python 3.7及以上版本，可以直接运行
    poiId = 19021228
    df = pd.read_excel(r'G:\updata\夹心\19021228.xlsx')
