# utf - 8
import asyncio
import time
import traceback

import aiohttp
import requests
import re
import json
import pandas as pd
from pymongo import MongoClient
from requests.exceptions import InvalidHeader


class JX():
    def __init__(self, poi_id, cookie):
        self.poi_id = str(poi_id)
        self.cookie = cookie
        self.headers = {
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
        client = MongoClient('mongodb://localhost:27017/')
        # 选择数据库和集合（相当于 SQL 中的表）
        self.db = client['test']
        # collection = db[str(poi_id)]
        self.collection = self.db[self.poi_id]
        self.session = requests.session()

    def while_fun(self, func, *args, **kwargs):
        num = 0
        while num < 3:
            try:
                res = func(*args, **kwargs)
                # print(res.json())
                if res.status_code == 200:
                    return res
                num += 1
            except InvalidHeader:
                print("多余字符")
                return 0
            except Exception as e:
                print(e)
                num += 1
                time.sleep(1)
        return 0

    def get_tag(self):
        data = {
            'tabStatus': '-1',
            'inRecycleBin': '0',
            'wmPoiId': self.poi_id,
            'appType': '3'
        }
        # 发送 POST 请求
        url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/tag/r/tagList?ignoreSetRouterProxy=true'
        # response = requests.post(url, headers=headers, data=data)
        response = self.while_fun(requests.post, url=url, headers=self.headers, data=data)
        if response.status_code == 200:
            json_data = response.json()
            if json_data['msg'] != 'success':
                print('报错了', json_data['msg'])
            else:
                return json_data['data']

    def zz(self, num1, num2):
        return num1 // num2 if num1 % num2 == 0 else num1 // num2 + 1

    def getdata(self, i):
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

    def get_product_v2(self):
        num = 0
        while 3 > num:
            try:
                response = self.session.get(
                    'https://e.waimai.meituan.com/reuse/product/food/r/editView/v2',
                )
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                num += 1
        if num == 3:
            return None

        # 解析返回的JSON数据，提取所需的信息
        json_data = response.json()['data']['wmProductSpu']
        dis = {
            'description': json_data['description'],
            "min_order_count": json_data['min_order_count'],
            'attrList01': [],
            'attrList02': [],
            "wmProductSkuVos": [],
        }

        for attr in json_data['newSpuAttrs']:
            if attr['name'] == '份量':
                dis['attrList01'].append(attr)
            else:
                dis['attrList02'].append(attr)

        for skattr in json_data['wmProductSkus']:
            arr = []
            for attr in skattr['attrList']:
                arr.append({
                    "name": attr['name'],
                    "value": attr['value'],
                    "no": attr['no'],
                })
            # print(arr)
            dic1 = {
                "attrList": arr,
                "boxPrice": skattr['box_price'],
                "boxNum": skattr['box_num'],
                "price": skattr['price'],
                "spec": skattr['spec'],
                "stock": skattr['stock'],
                "weightUnit": skattr['weight_unit'],
                "unit": skattr['unit'],
                "weight": skattr['weight'],
                "ladder_num": skattr["wmProductLadderBoxPrice"]['ladder_num'],
                "ladder_price": skattr["wmProductLadderBoxPrice"]['ladder_price'],
            }
            # print(skattr)
            dis['wmProductSkuVos'].append(dic1)
        # print(dis)
        return dis

    def aa(self, data):
        spuListVos = data['data']['spuListVos']
        documents = []
        params = {
            'spuId': '',
            'wmPoiId': self.poi_id,
            'clientId': '2',
            'v2': '1',
        }

        for i in spuListVos:
            # print(i)

            dis1 = self.getdata(i)
            params['spuId'] = i['id']
            self.session.params = params

            dis2 = self.get_product_v2()
            dis1.update(dis2)

            if self.collection.find_one({"name": i['name']}):
                self.collection.update_one({"name": i['name']}, {"$set": dis1})
            else:
                documents.append(dis1)
        if len(documents):
            self.collection.insert_many(documents)
            print(data['data']['spuListVos'][0]['tagName'])
            print('添加成功')
        else:
            print('没有商品')

    def get_product(self):
        url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/food/r/getSpuListCommon?ignoreSetRouterProxy=true'
        tag_data = self.get_tag()
        # 创建 MongoDB 客户端

        self.collection.drop()
        if not len(tag_data):
            print(tag_data)
            raise '标签获取失败'

        self.session.headers = self.headers

        for i in range(len(tag_data)):
            # print(tag_data[i]['name'])
            pageNum = self.zz(tag_data[i]['spuCount'], 90)
            for j in range(pageNum):
                data = {
                    'tagId': tag_data[i]['id'],
                    'pageNum': j + 1,
                    'pageSize': 90,
                    'needAllCount': '1',
                    'tabStatus': '-1',
                    'inRecycleBin': '0',
                    'wmPoiId': self.poi_id,  # 店铺id
                    'appType': '3'
                }
                num = 0
                # response = session.post(url, data=data)
                while 3 > num:
                    try:
                        response = self.while_fun(self.session.post, url=url, data=data)
                        if response.status_code == 200:
                            json_data = response.json()
                            self.aa(json_data)
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

    def set_attribute_yj(self, sr1, attrList02, chenCheng=''):
        print(chenCheng)
        """
        :param sr1: 6英寸=123#10英寸=220#8英寸=300
        :param attrList02: 不用改
        :return:
        """
        arr = sr1.split('#')
        arr = [i.split('=') for i in arr]
        print(arr)
        attributes = []
        if not len(arr):
            return '错误'
        for index, val in enumerate(arr):
            if not val[0]:
                continue
            if '人' in val[0]:
                weight = val[0][0]
                weightUnit = val[0]
            else:
                weightUnit = '个'
                weight = 1

            attributes.append(
                {"name": '份量', "name_id": 0, "price": int(val[1]), "value": val[0] + chenCheng, "value_id": 0,
                 "no": 0,
                 "mode": 2,
                 "weight": weight, "weightUnit": weightUnit, "sell_status": 0, "value_sequence": index, "unitType": 1
                 }
            )

        if not len(attrList02):
            return attributes
        attrList02.sort(key=lambda x: x['name'])
        name = attrList02[0]['name']
        indx = 1
        num = 1
        for index, i in enumerate(attrList02):
            if name != i['name']:
                name = i['name']
                indx = 1
                num += 1
            attributes.append(
                {"name": i['name'], "name_id": 0, "value": i['value'], "value_id": 0, "price": int(i['price']),
                 "no": num,
                 "mode": 1, "value_sequence": indx, "weight": 0, "weightUnit": '个', "sell_status": 0
                 })
            indx += 1
        return attributes

    def set_wmProductSkuVos_yj01(self, sk, boxPrice):
        productsk = []

        for i, val in enumerate(sk):
            productsk.append(
                {"unit": "1个", "box_price": boxPrice, "spec": val['spec'],
                 "weight": "1",
                 "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['ladder_num'],
                                             "ladder_price": boxPrice},

                 "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
                                    "auto_refresh": 1},

                 "attrList": val['attrList']
                 },
            )
        return productsk