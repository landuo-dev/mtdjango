# from pymongo import MongoClient
# import json
# import pandas as pd
#
# poi_id = 19021228
#
# client = MongoClient('mongodb://localhost:27017/')
# # 选择数据库和集合（相当于 SQL 中的表）
# db = client['actproduct']
# collection = db[str(poi_id)]
# documents = []
# for i in collection.find():
#     if i['errMsg'] == "已参与折扣活动":
#         documents.append({
#                 '商品id': i['actId'],
#                 '店铺id': poi_id,
#                 '商品名字': i['name'],
#                 '商品规格': i['spec'],
#                 '原价': i['originPrice'],
#                 '折扣价': i['actPrice'],
#         })
#
# df = pd.DataFrame(documents)
# filename = f'G:\\updata\折扣\\{str(poi_id)}.xlsx'
# df.to_excel(filename, index=False, engine='openpyxl')
import time

import requests


def get_exl(poi_id, cookie):
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

    url = "https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/act/item/export"

    query_data = {
        'source': 'pc',
        'yodaReady': 'h5',
        'csecplatform': '4',
        'csecversion': ' 2.4.0',
    }

    post_data = {
        'actType': 17,
        'poiIds': poi_id,
        'status': 1,
        'skuName': None,
        'chargeType': '-1',
    }

    num = 0
    while 3 > num:
        try:
            resp = requests.post(url, params=query_data, data=post_data, headers=headers, timeout=5)
            if resp.status_code == 200:
                json_data = resp.json()
                if json_data['msg'] == '文件已生成':
                    url = json_data['data']
                    return url
            num += 1
        except Exception as e:
            time.sleep(1)
            num += 1
            print(e)
    return None
