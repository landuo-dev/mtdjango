from pymongo import MongoClient
import json
import pandas as pd
import math
import time
import requests

from Custom_features.setting import set_bb






def main1(df, cookie, poi_id):
    # get_product(poiId)
    # 创建 MongoDB 客户端
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['test']
    reult = ''
    url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
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
    for i, data in df.iterrows():
        try:
            try:
                # poi_id = int(data.iloc[0])
                collection = db[str(int(poi_id))]
                name = data.iloc[2]
                product_info = str(data.iloc[3])
                if product_info == 'nan':
                    product_info = ''
                description = data.iloc[4]
            except Exception as e:
                print(i)
                print(e)
                continue
            document = collection.find_one({"name": name})
            if not document:
                print(i)
                print("该店铺没有商品", name)
                continue
            # print(attributes)
            # break
            # print(len(attributes))
            # break
            # 三个全黑
            bb, updataattributes = set_bb(poi_id, document, description, name, product_info)

            wmFoodVoJson02 = [bb]
            post_data = {
                'wmPoiId': poi_id,
                'entranceType': 2,
                'userType': 0,
                'wmFoodVoJson': json.dumps(wmFoodVoJson02)
            }

            num = 0
            while 3 > num:
                try:
                    response = requests.post(url, headers=headers, data=post_data, timeout=5)
                    json_data = response.json()
                    if json_data['msg'] != 'success':
                        # print(json_data['msg'], name)
                        reult += (str(json_data['msg']) + " " + name + '\n')
                        print(i)
                    # print(json_data)
                    break
                except requests.exceptions.ReadTimeout:
                    print("请求超时，请手动修改", name)
                    print(i)
                    num += 1
                    time.sleep(1)
                except Exception as e:
                    print(i)
        except Exception as e:
            print(i)
            print(e)
            # print(response.status_code, i)
            # print(response.json())
    return reult

if __name__ == '__main__':
    main1()
