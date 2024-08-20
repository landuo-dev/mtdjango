# utf - 8
import asyncio
import random
import time
import traceback

import aiohttp
import requests
import re
import json
import pandas as pd
from pymongo import MongoClient
from requests.exceptions import InvalidHeader
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient


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
        self.client = MongoClient('mongodb://localhost:27017/')
        # 选择数据库和集合（相当于 SQL 中的表）
        self.db = self.client[self.poi_id]
        # collection = db[str(poi_id)]
        self.collection = self.db["prodata"]
        self.session = requests.session()
        self.session.headers = self.headers
        # res = requests.get(
        #     "http://www.zdopen.com/PrivateProxy/GetIP/?api=202408101456362844&akey=eeed4049479ed4f3&count=8&adr=%E5%B9%BF%E4%B8%9C&fitter=1&timespan=15&tunnel=1&type=3").json()
        # self.proxy_pool = [f"http://{i['ip']}:{i['port']}" for i in res['data']['proxy_list']]
        # print(self.proxy_pool)
        self.proxy_pool = [
            'http://159.226.227.118:80',
            'http://42.63.65.49:80',
            'http://182.34.18.44:8089',
            'http://94.74.80.88:20201',
            'http://36.6.145.58:8089',
            'https://113.223.213.93:8089',
            'http://60.214.128.150:9091',
            'https://114.232.109.124:8089',
            'https://183.164.243.12:8089',
            'https://36.6.144.216:8089',
            'http://223.111.245.251:80',
            'https://117.69.236.15:8089',
            'https://117.69.190.143:41122',
            'http://117.57.93.37:8089',
            'https://36.6.145.202:8089',
            'https://113.223.215.45:8089',
            'https://123.182.58.55:8089',
            'http://110.80.140.213:443',
            'http://47.93.121.200:80',
            'http://123.13.218.68:9002',
            'http://111.224.212.154:8089',
            'http://123.57.172.180:18080',
            'http://61.129.2.212:8080',
            'http://111.177.63.86:8888',
            'http://47.102.111.107:8080',
            'http://118.31.1.154:80',
            'http://111.225.152.22:8089',
            'http://111.172.239.145:3128',
            'http://120.25.1.15:7890',
            'http://115.223.11.212:50000',
            'http://39.104.87.157:82',
            'http://47.93.249.121:8118',
            'http://113.219.247.226:30000',
            'https://111.172.239.145:3128',
            'httpss://114.236.93.203:22486',

            # # 更多代理...
        ]
        self.max_num = 10

    def while_fun(self, func, *args, **kwargs):
        num = 0
        while self.max_num > num:
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

    # 设置夹心入库

    def get_random_proxy(self):
        return random.choice(self.proxy_pool)

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
        proxy = self.get_random_proxy()
        num = 0
        while self.max_num > num:
            try:
                response = self.session.get(
                    'https://e.waimai.meituan.com/reuse/product/food/r/editView/v2',
                    # proxies={'http': proxy, 'https': proxy},
                )
                if response.status_code == 200:
                    break
            except Exception as e:
                print(e)
                time.sleep(5)
                num += 1
        if num == 3:
            return None

        # 解析返回的JSON数据，提取所需的信息
        json_data = response.json()['data']['wmProductSpu']
        dis = {
            'description': json_data['description'],
            "min_order_count": json_data['min_order_count'],
            "mapSpuExtendList": json_data["mapSpuExtendList"],
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
                "ladder_num": skattr['wmProductLadderBoxPrice']['ladder_num'],
                "ladder_price": skattr['wmProductLadderBoxPrice']['ladder_price'],
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

        for i in range(len(tag_data)):
            # print(tag_data[i]['name'])
            pageNum = self.zz(tag_data[i]['spuCount'], 30)
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
                while self.max_num > num:
                    try:
                        response = self.while_fun(self.session.post, url=url, data=data)
                        if response.status_code == 200:
                            json_data = response.json()
                            self.aa(json_data)
                            break
                        else:
                            print('请求失败', response.json())
                            num += 1
                            time.sleep(5)
                            continue

                    except Exception as e:
                        print(e)
                        num += 1
                        time.sleep(5)
                        continue

    # 结束夹心入库

    # 更改夹心
    def set_attribute(self, str1, attrs, mode):
        attributes = []
        updatabase = []
        dic1 = {}
        flog = 0
        if len(attrs):
            for index, i in enumerate(attrs):
                if i['price'] != 0:
                    dic1[i['name']] = dic1.get(i['name'], [])
                    dic1[i['name']].append(i['value'])
                if i['value']:
                    value = i['value'].strip()
                else:
                    value = i['value']
                attributes.append(
                    {"name": i['name'].strip(), "name_id": i['name_id'], "price": i['price'],
                     "value": value, "value_id": i['value_id'], "no": 0,
                     "mode": i['mode'],
                     "weight": i['weight'], "weightUnit": i['weightUnit'], "sell_status": i['sell_status'],
                     "value_sequence": i['value_sequence'], "unitType": 1
                     }
                )
        else:
            attributes.append(
                {"name": "份量", "name_id": 0, "price": 500, "value": "1个", "value_id": 0, "no": 0,
                 "mode": 2,
                 "weight": 1, "weightUnit": "个", "sell_status": 0, "value_sequence": 0, "unitType": 1
                 }
            )
        # print(attributes) 夹心选择一#甜甜黄桃果肉🍑#进口新鲜火龙果💕##夹心选择二#甜甜黄桃果肉🍑#进口新鲜火龙果##
        strs = str1.split('##')
        for num, i in enumerate(strs):
            arr = i.split('#')
            for j in range(len(arr) - 1):
                if not arr[j + 1]:
                    continue
                nameval = re.sub(' ', '', arr[j + 1]).split('=')
                if len(nameval) == 2:
                    name = nameval[0]
                    price = nameval[1]
                    flog = 1
                    # print(name, price)
                else:
                    name = nameval[0]
                    price = 0
                # print(name, price)
                dic1[arr[0]] = dic1.get(arr[0], [])
                dic1[arr[0]].append(name)
                attributes.append(
                    {"name": arr[0], "name_id": 0, "value": name, "value_id": 0, "price": price, "no": num + 1,
                     "mode": mode, "value_sequence": j, "weight": 0, "weightUnit": None, "sell_status": 0
                     })
                updatabase.append(
                    {
                        "name": arr[0],
                        "price": 0,
                        'value': arr[j + 1]
                    }
                )
        return attributes, updatabase, flog, dic1

    def set_wmProductSkuVos(self, sk):
        flog = 0
        productsk = []
        for i, val in enumerate(sk):
            price = str(min(int(val['boxPrice']), 5))
            productsk.append(
                {"price": val['price'], "unit": '1个', "box_price": price, "spec": val['spec'],
                 "weight": "1",
                 "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['ladder_num'],
                                             "ladder_price": price},
                 "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
                                    "auto_refresh": 1},
                 "attrList": val['attrList']
                 },
            )
        return productsk

    def set_properties(self, value):
        data = {}
        for key, val in value.items():
            temp = []
            for v in val:
                temp.append(
                    {"customized": 0, "enumLimit": -1, "id": 0, "inputTypeLimit": "", "input_type": 1,
                     "is_leaf": v['is_leaf'],
                     "is_required": 2, "keyProperty": 0, "level": v['level'], "maxLength": -1, "multiSelect": 0,
                     "parent_tag_id": v['code'],
                     "prompt_document": "", "sequence": v['sequence'], "wm_product_lib_tag_id": v['code'],
                     "wm_product_lib_tag_name": v['name'],
                     "wm_product_property_template_id": v['template_id'], "value_id": v['value_id'], "value": v['value']
                     })
            data[key] = temp
        return data

    def set_aa(self, names, l, bb, sr1, arr):
        # arr = []
        # arr.append({"name": "份量", "name_id": 0, "value": val, "value_id": 0, "no": 0}):

        if len(names) <= l:
            arr01 = []
            key = ''

            for i in sr1:
                # key += str(i[1]) + "·"
                if i[0] == '份量':
                    key += str(i[1]) + "(1个)·"
                    arr01.append({"name": i[0], "name_id": 0, "value": i[1], "value_id": 0, "no": 0})
                else:
                    key += str(i[1]) + "·"
                    arr01.append({"name": i[0], "name_id": 0, "value": i[1], "value_id": 0})
            else:
                key = key[:-1]
            arr[key] = arr01
            return 0

        for i in bb[names[l]]:
            sr1.append((names[l], i))
            self.set_aa(names, l + 1, bb, sr1, arr)
            sr1.pop()

    # 设置包装费，自定义包装费/复制包装费
    def set_wmProductSkuVos1(self, dic1):
        # print(dic1, 'dic1')
        sr1 = []
        arr = {}
        self.set_aa(list(dic1.keys()), 0, dic1, sr1, arr)
        productsk = []
        pattern = r'\([^()]*\)'
        for key, val in arr.items():
            dic2 = {"unit": '1个', "box_price": "0", "spec": key,
                    "weight": "1",
                    "wmProductLadderBoxPrice": {"status": 1, "ladder_num": "1",
                                                "ladder_price": "0"},
                    "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
                                       "auto_refresh": 0},
                    "attrList": val,
                    }
            productsk.append(dic2)
        # for i, val in enumerate(sk):
        #     dic2 = {"unit": '1个', "box_price": str(int(val['boxPrice'])), "spec": val['spec'],
        #             "weight": "1",
        #             "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['boxNum'],
        #                                         "ladder_price": str(int(val['boxPrice']))},
        #             "wmProductStock": {"id": "0", "stock": val['stock'], "max_stock": val['maxStock'],
        #                                "auto_refresh": 1},
        #             }
        #     if "·" in val['spec']:
        #         key = re.sub(pattern, '', val['spec'])
        #         dic2['attrList'] = arr[key]
        #     else:
        #         dic2['attrList'] = [
        #             {"name": "份量", "name_id": 0, "value": val['spec'].split('(')[0], "value_id": 0, "no": 0}]
        #
        #     productsk.append(dic2)

        return productsk

    def set_bb(self, document, description, product_info, mode, properties_num=1):
        proid = document['proid']
        if mode:
            attributes, updatadatabase, flog, dic1 = self.set_attribute(product_info, document['attrList01'], 1)
            productskuvos = self.set_wmProductSkuVos(document['wmProductSkuVos'])
        else:
            attributes, updatadatabase, flog, dic1 = self.set_attribute(product_info, document['attrList01'], 2)
            productskuvos = self.set_wmProductSkuVos1(dic1)
        result = ''
        # print('attributes', attributes)
        min_order_count = document.get('min_order_count', 1)
        properties_values = self.set_properties(document['mapSpuExtendList'])
        bb = {"description": description, "name": document['name'], "wm_poi_id": self.poi_id,
              "tag_id": document['tagId'],
              "tag_name": document['tagName'], "isShippingTimeSyncPoi": 2,
              "shipping_time_x": document['shippingTimeX'],
              "min_order_count": min_order_count,
              "wmProductPics":
                  [
                      {"aestheticsScore": "", "blur_result": 1, "blur_score": 0.999, "border_result": 1,
                       "border_score": 1,
                       "ctime": 1713842990, "detailList": [{"extra": "", "picPropaganda": {
                          "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                          "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                          "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                          "setTypeName": True,
                          "suggestion": "商品图片翻拍,建议重新上传图片", "type": "recapture", "typeName": "翻拍"},
                                                            "result": 1,
                                                            "score": 1, "setExtra": True, "setPicPropaganda": True,
                                                            "setResult": True,
                                                            "setScore": True, "setType": True, "setTypeName": True,
                                                            "type": "recapture", "typeName": "图片翻拍"},
                                                           {"extra": "",
                                                            "picPropaganda": {
                                                                "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                                                                "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                                                                "setBadPicUrl": True,
                                                                "setGoodPicUrl": True,
                                                                "setSuggestion": True,
                                                                "setType": True,
                                                                "setTypeName": True,
                                                                "suggestion": "商品图片模糊，建议重新上传图",
                                                                "type": "blur",
                                                                "typeName": "模糊"},
                                                            "result": 1,
                                                            "score": 0.999,
                                                            "setExtra": True,
                                                            "setPicPropaganda": True,
                                                            "setResult": True,
                                                            "setScore": True,
                                                            "setType": True,
                                                            "setTypeName": True,
                                                            "type": "blur",
                                                            "typeName": "图片模糊"},
                                                           {"extra": "", "picPropaganda": {
                                                               "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                                                               "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                                                               "setBadPicUrl": True, "setGoodPicUrl": True,
                                                               "setSuggestion": True,
                                                               "setType": True, "setTypeName": True,
                                                               "suggestion": "商品图片周围存在边框，建议重新上传图片",
                                                               "type": "border", "typeName": "图片周围有边框"},
                                                            "result": 1,
                                                            "score": 1, "setExtra": True, "setPicPropaganda": True,
                                                            "setResult": True,
                                                            "setScore": True, "setType": True, "setTypeName": True,
                                                            "type": "border",
                                                            "typeName": "图片有边框"}],
                       "detailListIterator": [{"extra": "",
                                               "picPropaganda": {
                                                   "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                                                   "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                                                   "setBadPicUrl": True,
                                                   "setGoodPicUrl": True,
                                                   "setSuggestion": True,
                                                   "setType": True,
                                                   "setTypeName": True,
                                                   "suggestion": "商品图片翻拍,建议重新上传图片",
                                                   "type": "recapture",
                                                   "typeName": "翻拍"},
                                               "result": 1,
                                               "score": 1,
                                               "setExtra": True,
                                               "setPicPropaganda": True,
                                               "setResult": True,
                                               "setScore": True,
                                               "setType": True,
                                               "setTypeName": True,
                                               "type": "recapture",
                                               "typeName": "图片翻拍"},
                                              {"extra": "",
                                               "picPropaganda": {
                                                   "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                                                   "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                                                   "setBadPicUrl": True,
                                                   "setGoodPicUrl": True,
                                                   "setSuggestion": True,
                                                   "setType": True,
                                                   "setTypeName": True,
                                                   "suggestion": "商品图片模糊，建议重新上传图",
                                                   "type": "blur",
                                                   "typeName": "模糊"},
                                               "result": 1,
                                               "score": 0.999,
                                               "setExtra": True,
                                               "setPicPropaganda": True,
                                               "setResult": True,
                                               "setScore": True,
                                               "setType": True,
                                               "setTypeName": True,
                                               "type": "blur",
                                               "typeName": "图片模糊"},
                                              {"extra": "",
                                               "picPropaganda": {
                                                   "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                                                   "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                                                   "setBadPicUrl": True,
                                                   "setGoodPicUrl": True,
                                                   "setSuggestion": True,
                                                   "setType": True,
                                                   "setTypeName": True,
                                                   "suggestion": "商品图片周围存在边框，建议重新上传图片",
                                                   "type": "border",
                                                   "typeName": "图片周围有边框"},
                                               "result": 1,
                                               "score": 1,
                                               "setExtra": True,
                                               "setPicPropaganda": True,
                                               "setResult": True,
                                               "setScore": True,
                                               "setType": True,
                                               "setTypeName": True,
                                               "type": "border",
                                               "typeName": "图片有边框"}],
                       "detailListSize": 3, "id": 228980523725, "isMaster": 0, "is_quality_low": False,
                       "is_scored": 1,
                       "picExtend": "",
                       "pic_large_url": document['defaultPicUrl'],
                       "pic_small_url": document['picUrl'], "quality_score": 1, "recapture_result": 1,
                       "recapture_score": 1,
                       "sequence": 0,
                       "setAestheticsScore": True, "setBlur_result": True, "setBlur_score": True,
                       "setBorder_result": True,
                       "setBorder_score": True, "setCtime": True, "setDetailList": True, "setId": True,
                       "setIsMaster": True,
                       "setIs_quality_low": True, "setIs_scored": True, "setPicExtend": True,
                       "setPic_large_url": True,
                       "setPic_small_url": True, "setQuality_score": True, "setRecapture_result": True,
                       "setRecapture_score": True,
                       "setSequence": True, "setSpOverrided": True, "setSpecialEffectBigUrl": True,
                       "setSpecialEffectEnable": True,
                       "setSpecialEffectUrl": True, "setUtime": True, "setValid": True, "setWhite_rate_score": True,
                       "setWmProductPicMaterialList": False, "setWm_food_spu_id": True, "setWm_poi_id": True,
                       "setWm_product_sku_id": True, "spOverrided": False, "specialEffectBigUrl": "",
                       "specialEffectEnable": 0,
                       "specialEffectUrl": "", "utime": 1713842990, "valid": 1, "white_rate_score": 1,
                       "wmProductPicMaterialList": None, "wmProductPicMaterialListIterator": None,
                       "wmProductPicMaterialListSize": 0,
                       "picPropagandaList": [
                           {
                               "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                               "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                               "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                               "setTypeName": True,
                               "suggestion": "商品图片翻拍,建议重新上传图片", "type": "recapture",
                               "typeName": "翻拍"},
                           {
                               "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                               "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                               "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                               "setTypeName": True,
                               "suggestion": "商品图片模糊，建议重新上传图", "type": "blur", "typeName": "模糊"},
                           {
                               "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                               "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                               "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                               "setTypeName": True,
                               "suggestion": "商品图片周围存在边框，建议重新上传图片", "type": "border",
                               "typeName": "图片周围有边框"}]}],
              "specialEffectPic": None, "category_id": document['spTagId'],
              "labelList": document['wmProductLabelVos'],
              "newSpuAttrs": attributes,
              "stockAndBoxPriceSkus": productskuvos,
              "unifiedPackagingFee": 2,
              "wmProductLadderBoxPrice": {"status": 1, "ladder_num": "", "ladder_price": ""},  # 包装费
              "wmProductStock": {"id": 0, "stock": "10000", "max_stock": "10000", "auto_refresh": 1},
              "productCardDisplayContent": "", "wmProductVideo": None, "singleOrderNoDelivery": 0,
              "onlySellInCombo": False,
              "id": proid,
              "properties_values":
                  properties_values,

              "labelValues": [{"sequence": 1, "value": ""}, {"sequence": 2, "value": ""}], "suggestTraceInfoList": [
                {"setTraceId": True, "setTraceType": True, "traceId": "897162237673668406", "traceType": 100002}]}
        return bb, updatadatabase

    async def fetch_data(self, session, url, post_data, as_requests=1):
        try:
            if as_requests:
                request_options = {"headers": self.headers, "data": post_data,
                                   "timeout": aiohttp.ClientTimeout(total=5),
                                   "proxy": self.get_random_proxy()}
            else:
                request_options = {"headers": self.headers, "data": post_data}
            async with session.post(url=url, **request_options) as response:

                if response.status != 200:
                    raise Exception(f"HTTP Error {response.status}")
                json_data = await response.json()
                print(json_data, '夹心')
                if json_data.get('msg') != 'success':
                    return json_data
                # print(json_data)
                return None
        except Exception as e:
            print(e)
            return None

    async def Recover(self, back_poi_id, as_requests):
        url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
        result = set()
        # 创建 MongoDB 客户端
        client = MongoClient('mongodb://localhost:27017/')
        # 选择数据库和集合（相当于 SQL 中的表）
        test = client[self.poi_id]
        back = client['back_up_jx']
        back_collection = back[str(back_poi_id)]
        collection = test["prodata"]

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

                post_data = self.set_post_data_yj(back_document, back_document['description'], document['attrList01'],
                                                  chenCheng='', name=document['name'], attribute=document['attrList02'])

                num = 0
                while 3 > num:
                    json_data = await self.fetch_data(session, url, post_data, as_requests)
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

    async def updata01(self, df, result, mode):
        url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
        # result = set()
        if not "prodata" in self.db.list_collection_names():
            return ValueError('该店没入库')
        session = aiohttp.ClientSession()
        err = 0
        names = set()
        for i, data in df.iterrows():
            flog = ''
            try:
                try:
                    # poi_id = int(data.iloc[0])
                    # single positional indexer is out-of-bounds
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
                document = self.collection.find_one({"name": name})
                description = str(data.iloc[4]) if not pd.isna(data.iloc[4]) else document.get('description', '')
                if description == "-1":
                    description = ""
                if not document:
                    print(i)
                    print("该店铺没有商品", name)
                    result.add(f"该店铺没有商品 {data.iloc[2]}")
                    continue

                bb, updatadatabase = self.set_bb(document, description, product_info, mode)
                names.add(name)
                wmFoodVoJson02 = [bb]
                post_data = {
                    'wmPoiId': self.poi_id,
                    'entranceType': 2,
                    'userType': 0,
                    'wmFoodVoJson': json.dumps(wmFoodVoJson02)
                }

                num = 0
                while self.max_num > num:
                    json_data = await self.fetch_data(session, url, post_data, 0)
                    if json_data is None:
                        # self.collection.update_one({"name": name}, {"$set": {"attrList02": updatadatabase}})
                        err = 0
                        break  # 如果请求成功或不需要重试，则跳出循环
                    if json_data['msg'] == "参加活动商品无法修改，请先将商品下掉活动" or "图片来源异常" in json_data['msg']:
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
                        raise Exception("请求错误次数过多")

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
        # return result

    def updata_jx(self, df, result, mode=1):
        res = asyncio.run(self.updata01(df, result, mode))

    def run_Recover(self, back_poi_id, as_requests=1):
        asyncio.run(self.Recover(back_poi_id, as_requests))

        # 结束更新夹心

    # 原价菜单，更改菜单原价
    def yx_attrbute01(self, attrList02, attributes):
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
                {"name": i['name'], "name_id": 0, "value": i['value'], "value_id": 0, "price": (i['price']),
                 "no": num,
                 "mode": i['mode'], "value_sequence": indx, "weight": i['weight'], "weightUnit": i['weightUnit'],
                 "sell_status": 0
                 })
            indx += 1

    def yx_attrbute02(self, attrList02, attributes, dic1, mode=1):
        '''
        备注#每单仅限一份哦#多点也仅限一份哦
        :param attrList02:
        :param attributes:
        :return:
        '''
        strs = attrList02.split('##')
        for num, i in enumerate(strs):
            arr = i.split('#')

            for j in range(len(arr) - 1):
                if not arr[j + 1]:
                    continue
                nameval = re.sub(' ', '', arr[j + 1]).split('=')
                if len(nameval) == 2:
                    name = nameval[0].strip()
                    price = nameval[1]
                    flog = 1
                    # print(name, price)
                else:
                    name = nameval[0].strip()
                    price = 0
                # print(name, price)
                dic1[arr[0]] = dic1.get(arr[0], [])
                dic1[arr[0]].append(name)
                attributes.append(
                    {"name": arr[0], "name_id": 0, "value": name, "value_id": 0, "price": price, "no": num + 1,
                     "mode": mode, "value_sequence": j, "weight": 0, "weightUnit": None, "sell_status": 0
                     })

    def set_attribute03(self, attrList01, attrList02, chenCheng=''):
        attributes = []
        if not len(attrList01):
            raise ValueError('错误')
        dic1 = {}
        for index, i in enumerate(attrList01):
            if i['price'] != 0:
                dic1[i['name']] = dic1.get(i['name'], [])
                dic1[i['name']].append(i['value'])
            if i['value']:
                value = i['value'] + chenCheng
            else:
                value = ''
            attributes.append(
                {"name": i['name'], "name_id": 0, "price": int(i['price']), "value": value,
                 "value_id": 0, "no": 0,
                 "mode": i['mode'],
                 "weight": i['weight'], "weightUnit": i['weightUnit'], "sell_status": i['sell_status'],
                 "value_sequence": i['value_sequence'], "unitType": 1
                 }
            )

        if not len(attrList02):
            return attributes, dic1
        attrList02.sort(key=lambda x: x['name'])
        name = attrList02[0]['name']
        indx = 1
        num = 1

        for index, i in enumerate(attrList02):

            dic1[i['name']] = dic1.get(i['name'], [])
            dic1[i['name']].append(i['value'])

            number = 1
            if "个" in i['value']:
                try:
                    number = re.findall(r'\d+', i['value'])[0]
                except Exception as e:
                    print(e)
                    number = 1
            if name != i['name']:
                name = i['name']
                indx = 1
                num += 1
            attributes.append(
                {"name": i['name'], "name_id": 0, "value": i['value'], "value_id": 0, "price": int(i['price']),
                 "no": num, "mode": i['mode'], "value_sequence": indx, "weight": number, "weightUnit": None,
                 "sell_status": 0
                 })
            indx += 1
        return attributes, dic1

    def set_attribute_yj(self, sr1, attrList02, chenCheng='', mode=1):
        print(chenCheng)
        """
        :param sr1: 6英寸=123#10英寸=220#8英寸=300
        :param attrList02: 不用改
        :return:
        """
        dic1 = {}
        arr = sr1.split('#')
        arr = [i.split('=') for i in arr]
        print(arr)
        attributes = []
        if not len(arr):
            return '错误'
        for index, val in enumerate(arr):
            if not val[0]:
                continue
            if '人份' in val[0]:
                weight = val[0][0]
                weightUnit = val[0]
            else:
                weightUnit = '个'
                weight = 1

            if val[1] != 0 and val[1] != '0':
                dic1['份量'] = dic1.get("份量", [])
                dic1['份量'].append(val[0])

            attributes.append(
                {"name": '份量', "name_id": 0, "price": eval(val[1]), "value": val[0].strip() + chenCheng, "value_id": 0,
                 "no": 0,
                 "mode": 2,
                 "weight": weight, "weightUnit": weightUnit, "sell_status": 0, "value_sequence": index, "unitType": 1
                 }
            )

        if not len(attrList02):
            return attributes, dic1

        if '##' in attrList02:
            self.yx_attrbute02(attrList02, attributes, dic1=dic1, mode=mode)
        else:
            self.yx_attrbute01(attrList02, attributes)

        return attributes, dic1

    def set_wmProductSkuVos_yj01(self, sk, boxPrice):
        productsk = []
        flog = 0
        if not boxPrice:
            flog = 1
        for i, val in enumerate(sk):
            if flog:
                boxPrice = val['boxPrice']
            # print(boxPrice)
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

    def set_post_data_yj(self, document, description, sr1, chenCheng, doc=None, boxPrice=None, min_order_count=None,
                         attribute=None, name=None):

        if not doc:
            porid = document['proid']
        else:
            porid = doc['proid']

        picurl = document['picUrl']
        defaultPicUrl = document['defaultPicUrl']
        if not name:
            name = document['name']
            if not attribute:
                attrList, dic1 = self.set_attribute_yj(sr1, document['attrList02'], chenCheng)
            else:
                print('sr1---------->', sr1, attribute)
                attrList, dic1 = self.set_attribute_yj(sr1, attribute, chenCheng)
        else:
            attrList, dic1 = self.set_attribute03(sr1, attribute, chenCheng)

        # print(attrList)
        wmProductSkuVos = self.set_wmProductSkuVos_yj01(document['wmProductSkuVos'], boxPrice)
        if not min_order_count:
            min_order_count = 1
        properties_values = self.set_properties(document['mapSpuExtendList'])
        category_id = document['spTagId']
        bb = {"description": description, "name": name, "wm_poi_id": self.poi_id,
              "tag_id": document['tagId'],
              "tag_name": document['tagName'], "isShippingTimeSyncPoi": 2, "shipping_time_x": "-",
              "min_order_count": min_order_count,
              "wmProductPics":
                  [
                      {"aestheticsScore": "", "blur_result": 1, "blur_score": 0.999, "border_result": 1,
                       "border_score": 1,
                       "ctime": 1713842990, "detailList": [{"extra": "", "picPropaganda": {
                          "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                          "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                          "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                          "setTypeName": True,
                          "suggestion": "商品图片翻拍,建议重新上传图片", "type": "recapture", "typeName": "翻拍"},
                                                            "result": 1,
                                                            "score": 1, "setExtra": True, "setPicPropaganda": True,
                                                            "setResult": True,
                                                            "setScore": True, "setType": True, "setTypeName": True,
                                                            "type": "recapture", "typeName": "图片翻拍"},
                                                           {"extra": "",
                                                            "picPropaganda": {
                                                                "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                                                                "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                                                                "setBadPicUrl": True,
                                                                "setGoodPicUrl": True,
                                                                "setSuggestion": True,
                                                                "setType": True,
                                                                "setTypeName": True,
                                                                "suggestion": "商品图片模糊，建议重新上传图",
                                                                "type": "blur",
                                                                "typeName": "模糊"},
                                                            "result": 1,
                                                            "score": 0.999,
                                                            "setExtra": True,
                                                            "setPicPropaganda": True,
                                                            "setResult": True,
                                                            "setScore": True,
                                                            "setType": True,
                                                            "setTypeName": True,
                                                            "type": "blur",
                                                            "typeName": "图片模糊"},
                                                           {"extra": "", "picPropaganda": {
                                                               "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                                                               "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                                                               "setBadPicUrl": True, "setGoodPicUrl": True,
                                                               "setSuggestion": True,
                                                               "setType": True, "setTypeName": True,
                                                               "suggestion": "商品图片周围存在边框，建议重新上传图片",
                                                               "type": "border", "typeName": "图片周围有边框"},
                                                            "result": 1,
                                                            "score": 1, "setExtra": True, "setPicPropaganda": True,
                                                            "setResult": True,
                                                            "setScore": True, "setType": True, "setTypeName": True,
                                                            "type": "border",
                                                            "typeName": "图片有边框"}],
                       "detailListIterator": [{"extra": "",
                                               "picPropaganda": {
                                                   "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                                                   "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                                                   "setBadPicUrl": True,
                                                   "setGoodPicUrl": True,
                                                   "setSuggestion": True,
                                                   "setType": True,
                                                   "setTypeName": True,
                                                   "suggestion": "商品图片翻拍,建议重新上传图片",
                                                   "type": "recapture",
                                                   "typeName": "翻拍"},
                                               "result": 1,
                                               "score": 1,
                                               "setExtra": True,
                                               "setPicPropaganda": True,
                                               "setResult": True,
                                               "setScore": True,
                                               "setType": True,
                                               "setTypeName": True,
                                               "type": "recapture",
                                               "typeName": "图片翻拍"},
                                              {"extra": "",
                                               "picPropaganda": {
                                                   "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                                                   "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                                                   "setBadPicUrl": True,
                                                   "setGoodPicUrl": True,
                                                   "setSuggestion": True,
                                                   "setType": True,
                                                   "setTypeName": True,
                                                   "suggestion": "商品图片模糊，建议重新上传图",
                                                   "type": "blur",
                                                   "typeName": "模糊"},
                                               "result": 1,
                                               "score": 0.999,
                                               "setExtra": True,
                                               "setPicPropaganda": True,
                                               "setResult": True,
                                               "setScore": True,
                                               "setType": True,
                                               "setTypeName": True,
                                               "type": "blur",
                                               "typeName": "图片模糊"},
                                              {"extra": "",
                                               "picPropaganda": {
                                                   "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                                                   "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                                                   "setBadPicUrl": True,
                                                   "setGoodPicUrl": True,
                                                   "setSuggestion": True,
                                                   "setType": True,
                                                   "setTypeName": True,
                                                   "suggestion": "商品图片周围存在边框，建议重新上传图片",
                                                   "type": "border",
                                                   "typeName": "图片周围有边框"},
                                               "result": 1,
                                               "score": 1,
                                               "setExtra": True,
                                               "setPicPropaganda": True,
                                               "setResult": True,
                                               "setScore": True,
                                               "setType": True,
                                               "setTypeName": True,
                                               "type": "border",
                                               "typeName": "图片有边框"}],
                       "detailListSize": 3, "id": 228980523725, "isMaster": 0, "is_quality_low": False,
                       "is_scored": 1,
                       "picExtend": "",
                       "pic_large_url": defaultPicUrl,
                       "pic_small_url": picurl, "quality_score": 1, "recapture_result": 1,
                       "recapture_score": 1,
                       "sequence": 0,
                       "setAestheticsScore": True, "setBlur_result": True, "setBlur_score": True,
                       "setBorder_result": True,
                       "setBorder_score": True, "setCtime": True, "setDetailList": True, "setId": True,
                       "setIsMaster": True,
                       "setIs_quality_low": True, "setIs_scored": True, "setPicExtend": True,
                       "setPic_large_url": True,
                       "setPic_small_url": True, "setQuality_score": True, "setRecapture_result": True,
                       "setRecapture_score": True,
                       "setSequence": True, "setSpOverrided": True, "setSpecialEffectBigUrl": True,
                       "setSpecialEffectEnable": True,
                       "setSpecialEffectUrl": True, "setUtime": True, "setValid": True, "setWhite_rate_score": True,
                       "setWmProductPicMaterialList": False, "setWm_food_spu_id": True, "setWm_poi_id": True,
                       "setWm_product_sku_id": True, "spOverrided": False, "specialEffectBigUrl": "",
                       "specialEffectEnable": 0,
                       "specialEffectUrl": "", "utime": 1713842990, "valid": 1, "white_rate_score": 1,
                       "wmProductPicMaterialList": None, "wmProductPicMaterialListIterator": None,
                       "wmProductPicMaterialListSize": 0,
                       "picPropagandaList": [
                           {
                               "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                               "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                               "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                               "setTypeName": True,
                               "suggestion": "商品图片翻拍,建议重新上传图片", "type": "recapture",
                               "typeName": "翻拍"},
                           {
                               "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                               "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                               "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                               "setTypeName": True,
                               "suggestion": "商品图片模糊，建议重新上传图", "type": "blur", "typeName": "模糊"},
                           {
                               "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                               "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                               "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                               "setTypeName": True,
                               "suggestion": "商品图片周围存在边框，建议重新上传图片", "type": "border",
                               "typeName": "图片周围有边框"}]}],
              "specialEffectPic": None, "category_id": category_id,
              "labelList": document['wmProductLabelVos'],
              "newSpuAttrs": attrList,
              "stockAndBoxPriceSkus": wmProductSkuVos,
              "unifiedPackagingFee": 2,
              "wmProductLadderBoxPrice": {"status": 1, "ladder_num": "", "ladder_price": ""},  # 包装费
              "wmProductStock": {"id": 0, "stock": "10000", "max_stock": "10000", "auto_refresh": 1},
              "productCardDisplayContent": "", "wmProductVideo": None, "singleOrderNoDelivery": 0,
              "onlySellInCombo": False,
              "id": porid,
              "properties_values": properties_values,
              "labelValues": [{"sequence": 1, "value": ""}, {"sequence": 2, "value": ""}], "suggestTraceInfoList": [
                {"setTraceId": True, "setTraceType": True, "traceId": "897162237673668406", "traceType": 100002}]}
        # print(bb)
        wmFoodVoJson02 = [bb]
        post_data = {
            'wmPoiId': self.poi_id,
            'entranceType': 2,
            'userType': 0,
            'wmFoodVoJson': json.dumps(wmFoodVoJson02)
        }
        return post_data

    def save(self, document, sr1, description, boxPrice=None, min_order_count=None, attribute=None):
        reult = set()
        url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
        flog = 0
        try:
            post_data = self.set_post_data_yj(document, description, sr1, '', boxPrice, min_order_count, attribute)
            num = 0
            while self.max_num > num:
                try:
                    response = requests.post(url, headers=self.headers, data=post_data, timeout=5)
                    json_data = response.json()
                    if json_data['msg'] != 'success':
                        print(json_data['msg'], document['name'])
                        post_data = self.set_post_data_yj(document, description, sr1, '.', boxPrice, min_order_count,
                                                          attribute)
                        flog = 1
                        reult.add(f"{json_data['msg']} {document['name']})")
                        num += 1
                        continue
                    if flog:
                        flog = 2
                    print(json_data)

                    break
                except requests.exceptions.ReadTimeout:
                    print("请求超时，请手动修改", document['name'])
                    num += 1
                    time.sleep(5)
                except Exception as e:
                    print(e)
                    num += 1
        except Exception as e:
            print(e)
            print(document['name'])
            traceback.print_exc()
            # print(response.status_code, i)
            # print(response.json())

        if flog == 2:
            post_data = self.set_post_data_yj(document, description, sr1, '', boxPrice, min_order_count, attribute)
            response = requests.post(url, headers=self.headers, data=post_data, timeout=5)
            json_data = response.json()
            print(json_data, "还原")
        return reult

    def yanjia(self, df):
        dic1 = {}
        for key, val in df.iterrows():
            dic1[val.iloc[2]] = dic1.get(val.iloc[2], '') + str(val.iloc[3]) + "=" + str(val.iloc[4]) + "#"

        df_unique = df.drop_duplicates(subset='商品名称', keep='first')
        # print(dic1['提拉米苏蛋糕'])
        for key, val in df_unique.iterrows():
            try:
                name = val['商品名称']
                spce = dic1[name]
                # spce = val.iloc[3]
                ladder_num = str(val.iloc[5])
                document = self.collection.find_one({"name": name})
                print(spce)
                print("ladder_num", len(ladder_num))
                if document:
                    description = val['描述'] if not pd.isna(val['描述']) else document['description']
                else:
                    print(f'该店铺没有商品{name}, {spce}')
                    continue
                    # raise ValueError('该店铺没有商品')
                # print(val['描述'])

                if len(ladder_num) == 1:
                    boxPrice = val.iloc[5]
                    min_order_count = val.iloc[6]
                    attribute = val.iloc[9]
                    # print(boxPrice)
                    self.save(document, spce, description, boxPrice, min_order_count, attribute)
                else:
                    # pass
                    self.save(document, spce, description)
            except Exception as e:
                print(e)
                print(val.iloc[2])
                traceback.print_exc()
                # break

    #  结束更改原价菜单

    #  设置替换销量
    def get_time(self):
        # 获取当前日期和时间的datetime对象
        now = datetime.now()
        # 设置时间为0时0分0秒
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        next_month = today + relativedelta(years=1)
        # 转换为时间戳
        starttime = today.timestamp()
        endtime = next_month.timestamp()

        return (int(starttime), int(endtime))

    def set_post_data(self, name):
        post_data = {
            "skuName": name,
            'creatorRoleType': '-1',
            'pageNum': '1',
            'poiId': self.poi_id,
            'pageSize': 10,
            'status': '1',
        }
        return post_data

    def getdata_thxl(self, i):
        spec = i['food']['spec'].split('(')[0]
        dicts = {
            'weeksTime': i['weeksTime'],
            'period': i['period'],
            'poiId': self.poi_id,
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

    def save_act_data(self, proid, collect_act):
        doc = collect_act.find_one({"spuId": proid})
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

        response = self.while_fun(requests.post, url=url, headers=self.headers,
                                  data=self.set_post_data(doc['name']), params=query_params)
        json_data = response.json()['data']['list']

        # print(json_data)
        for i in json_data:
            # print(i)
            name = i['food']['wmSkuName']
            spec = i['food']['spec'].split('(')[0]
            dicts = self.getdata_thxl(i)
            # if not spec:
            #     continue

            count1 = collect_act.count_documents({"spuId": proid})
            # print(count1)
            if count1 == 1:
                if collect_act.find_one({"spuId": proid}):
                    collect_act.update_one({"name": name, 'spec': spec},
                                           {'$set': dicts})
            elif count1 > 1:
                if collect_act.find_one({"spuId": proid, "spec": spec}):
                    collect_act.update_one({"name": name, 'spec': spec},
                                           {'$set': dicts})
            else:
                collect_act.insert_one(dicts)

    def del_actproduct(self, collect_act, porid):
        acts = collect_act.find({"spuId": porid})
        actid = ''
        if acts:
            for i in acts:
                if 'actId' in i and i['actId'] != '' or i['errMsg'] != '':
                    if i['actId']:
                        actid += str(i['actId']) + ','

        return actid

    def delete_product(self, collection, actid):
        query_params = {
            'source': 'pc',
            'conflictCoverType': 0,
            'yodaReady': 'h5',
            'csecplatform': 4,
            'csecversion': '2.4.0',
        }

        data = {
            'actType': '17',
            'actIds': actid,
        }

        url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/common/disable'

        num = 0
        while self.max_num > num:
            try:
                response = requests.post(url, headers=self.headers, data=data, params=query_params)
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

    def save_thxl(self, document, doc, name, reult, pd=1):
        url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
        flog = 0
        num = 0
        try:
            # break
            # print(attrList)
            # print(len(attributes))
            # break
            # 三个全黑
            if pd:
                post_data = self.set_post_data_yj(document, document['description'], document['attrList01'],
                                                  '', doc=doc, name=name, attribute=document['attrList02'])
            else:
                post_data = self.set_post_data_yj(document, document['description'], document['attrList01'],
                                                  '.', doc=doc, name=name, attribute=document['attrList02'])

            # print(post_data)
            while self.max_num > num:
                try:
                    response = requests.post(url, headers=self.headers, data=post_data, timeout=5)
                    json_data = response.json()
                    print(json_data)
                    if json_data['msg'] != 'success':
                        if '商品价格涨幅不可超过40%' in json_data['msg']:
                            print(json_data['msg'], document['name'])
                            post_data = self.set_post_data_yj(document, document['description'], document['attrList01'],
                                                              '.', doc=doc, name=name,
                                                              attribute=document['attrList02'])
                            num += 1
                            flog = 1
                            continue
                        post_data = self.set_post_data_yj(document, document['description'], document['attrList01'],
                                                          '.', doc=doc, name=name,
                                                          attribute=document['attrList02'])
                        reult.add(str(json_data['msg']) + " " + document['name'] + '\n')
                        num += 1
                        flog = 1
                        continue

                    break
                except requests.exceptions.ReadTimeout:
                    print("请求超时，请手动修改", name)
                    num += 1
                    time.sleep(5)
                except Exception as e:
                    print(e)
                    num += 1
        except Exception as e:
            print(e)
            print(name)
            traceback.print_exc()
            reult.add(str(e) + " " + name + '\n')
            # print(response.status_code, i)
            # print(response.json())

        if flog or not pd:
            post_data = self.set_post_data_yj(document, document['description'], document['attrList01'],
                                              '', doc=doc, name=name, attribute=document['attrList02'])
            response = requests.post(url, headers=self.headers, data=post_data, timeout=5)
            json_data = response.json()
            print(json_data, "还原")

        if num >= 3:
            return 1

        return 0

    def updata_data(self, collection, porid, name, spec, actid, errMsg, spuId, skuId, price, tagName):
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

    def get_actdata(self, tagId, startTime, endTime):
        quer_data = {
            'source': 'pc',
            'actType': '17',
            'poiId': self.poi_id,
            'startTime': str(startTime),
            'endTime': str(endTime),
            'tagId': tagId,
            'yodaReady': 'h5',
            'csecplatform': '4',
            'csecversion': ' 2.4.0',

        }

        url = "https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/query/queryProductByWmPoiIdAndTagId?weeksTime=1,2,3,4,5,6,7&period=00:00-23:59"
        num = 0
        while self.max_num > num:
            try:
                response = requests.get(url, params=quer_data, headers=self.headers, timeout=5)
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

    def set_post_data_xlth(self, startTime, endTime, wmSkuId, wmSpuId, originPrice, actPrice, daylimit, orderLimit):
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
            "poiId": self.poi_id,
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

    def add_updata(self, doc, collection, name, proid):
        # 获取当前日期和时间的datetime对象
        now = datetime.now()

        # 设置时间为0时0分0秒
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        next_month = today + relativedelta(months=1)
        # 转换为时间戳
        startTime = int(today.timestamp())
        endTime = int(next_month.timestamp())

        act_data = self.get_actdata(doc['tagId'], startTime, endTime)
        if act_data:
            for j in act_data['data']:

                if not int(j['spuId']) == proid:
                    continue
                for k in j['skuList']:
                    actid = k['mutexActId']
                    self.updata_data(collection, proid, name, k['spec'], actid, k['errMsg'], j['spuId'], k['id'],
                                     k['price'], doc['tagName'])

    def add_acct(self, document):
        url = 'https://waimaieapp.meituan.com/proxy-gw/promotion/wmapi/activity/product/create'

        query_params = {
            'source': 'pc',
            'conflictCoverType': 0,
            'yodaReady': 'h5',
            'csecplatform': 4,
            'csecversion': '2.4.0',
        }

        starttime, endtime = self.get_time()

        headers2 = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': self.cookie,
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

        # print(document)
        post_data = self.set_post_data_xlth(starttime, endtime, document['skuId'],
                                            document['spuId'],
                                            document['originPrice'], document['actPrice'], document['daylimit'],
                                            document['orderLimit'])

        num = 0
        while self.max_num > num:
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

    def save_database(self, data, collection):
        lists = data['list']
        documents = []
        for i in lists:
            dicts = self.getdata_thxl(i)
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

    def updata_add(self, collection_act, name):
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

        num = 0
        while self.max_num > num:
            try:
                response = requests.post(url, headers=self.headers, data=self.set_post_data(name),
                                         params=query_params, timeout=4)
                if response.status_code == 200:
                    # print(response.text)
                    json_data = response.json()['data']
                    if len(json_data['list']):
                        # pass
                        self.save_database(json_data, collection_act)
                    break
                else:
                    print(f'连接失败， 正在重新尝试第{num}次', name)
                    num += 1
                    time.sleep(5)
            except Exception as e:
                print(e, name)
                print(f'连接失败， 正在重新尝试第{num}次')
                num += 1
                time.sleep(5)

    def yichangtianjia(self, collect_act, porid, tem=1):
        flog = 0
        if tem:
            for p in collect_act.find({'spuId': porid}):
                if p['errMsg'] == '7天内上调过价格不可设置活动':
                    return 1
        for p in collect_act.find({'spuId': porid}):
            if 'actPrice' in p:
                # print(p, name)
                flog = self.add_acct(p)
        return flog

    def replace_product(self, name_x, name_y, result):
        collect_act = self.db["proact"]

        doc_x = self.collection.find_one({'name': name_x})
        doc_y = self.collection.find_one({'name': name_y})
        if not doc_y or not doc_x:
            print('店铺没有商品')
            result.add('店铺没有商品')
            raise ValueError('店铺没有商品')

        porid_x = doc_x['proid']
        porid_y = doc_y['proid']

        print(porid_x, porid_y)

        self.save_act_data(porid_x, collect_act)
        self.save_act_data(porid_y, collect_act)

        actid_x = self.del_actproduct(collect_act, porid_x)
        actid_y = self.del_actproduct(collect_act, porid_y)

        print(actid_x)
        print(actid_y)
        if actid_x:
            self.delete_product(collect_act, actid_x)
        if actid_y:
            self.delete_product(collect_act, actid_y)

        time.sleep(5)
        flog1 = 0
        flog2 = 0

        # flog1 += save(collect_pro, doc_x, doc_x, poi_id, name_x[:-2] + '@', cookie, result)

        flog1 += self.save_thxl(doc_x, doc_x, name_x[:-2] + '@', result)
        print(name_x[:-2] + "@ 完成")
        flog1 += self.save_thxl(doc_x, doc_y, name_x, result)
        print(f"{name_y}----->{name_x} 完成")
        flog2 += self.save_thxl(doc_y, doc_x, name_y, result)
        print(f"{name_x}----->{name_y} 完成")
        if flog1:
            print("报错还原")
            result.add(f'请检查“{name_x}”的折扣名有没有错')
            self.save_thxl(doc_x, doc_x, name_x, result)
        elif flog2:
            print("报错还原")
            result.add(f'请检查“{name_y}”的折扣名有没有错')
            self.save_thxl(doc_y, doc_y, name_y, result)
            self.save_thxl(doc_x, doc_x, name_x, result)
        else:
            self.collection.update_one({"name": name_x}, {"$set": {
                "proid": doc_y['proid']
            }})
            self.collection.update_one({"name": name_y}, {"$set": {
                "proid": doc_x['proid']
            }})

            actdocx = [i for i in collect_act.find({"spuId": porid_x})]
            actdocy = [i for i in collect_act.find({"spuId": porid_y})]

            for doc in actdocx:
                collect_act.update_one({"name": doc['name'], "spec": doc['spec']}, {
                    "$set": {"spuId": porid_y, "orderLimit": doc['orderLimit'], "daylimit": doc['daylimit']}})
            for doc in actdocy:
                collect_act.update_one({"name": doc['name'], "spec": doc['spec']}, {
                    "$set": {"spuId": porid_x, "orderLimit": doc['orderLimit'], "daylimit": doc['daylimit']}})

        # time.sleep(4)
        doc_x = self.collection.find_one({'name': name_x})
        doc_y = self.collection.find_one({'name': name_y})

        porid_x = doc_x['proid']
        porid_y = doc_y['proid']

        self.add_updata(doc_x, collect_act, name_x, porid_x)
        self.add_updata(doc_y, collect_act, name_y, porid_y)

        print(name_y)
        flog_x = self.yichangtianjia(collect_act, porid_x)
        if flog_x:
            result1 = set()
            self.save_thxl(doc_x, doc_x, name_x, result)
            if len(result1):
                print(result1)
            flog_x = self.yichangtianjia(collect_act, porid_x, 0)
            self.save_thxl(doc_x, doc_x, name_x, result)

        print(name_x)
        flog_y = self.yichangtianjia(collect_act, porid_y)
        if flog_y:
            result1 = set()
            self.save_thxl(collect_act, doc_y, doc_y, name_y, result)
            if len(result1):
                print(result1)
            flog_y = self.yichangtianjia(collect_act, porid_y, 0)
            self.save_thxl(doc_y, doc_y, name_y, result)

        time.sleep(5)
        self.updata_add(collect_act, porid_x)
        self.updata_add(collect_act, porid_y)

        self.add_updata(doc_x, collect_act, name_x, porid_x)
        self.add_updata(doc_x, collect_act, name_y, porid_y)
        return result

    # 结束设置销量替换

    #  替换失败还原

    def replaceFailedRevert(self, name_x, result):
        collect_act = self.db["proact"]

        doc_x = self.collection.find_one({'name': name_x})
        if  not doc_x:
            print('店铺没有商品')
            result.add('店铺没有商品')
            raise ValueError('店铺没有商品')

        porid_x = doc_x['proid']


        self.save_act_data(collect_act)

        actid_x = self.del_actproduct(collect_act, porid_x)
        actid_y = self.del_actproduct(collect_act, porid_y)

        print(actid_x)
        print(actid_y)
        if actid_x:
            self.delete_product(collect_act, actid_x)
        if actid_y:
            self.delete_product(collect_act, actid_y)

        time.sleep(5)
        flog1 = 0
        flog2 = 0

        # flog1 += save(collect_pro, doc_x, doc_x, poi_id, name_x[:-2] + '@', cookie, result)

        flog1 += self.save_thxl(doc_x, doc_x, name_x[:-2] + '@', result)
        print(name_x[:-2] + "@ 完成")
        flog1 += self.save_thxl(doc_x, doc_y, name_x, result)
        print(f"{name_y}----->{name_x} 完成")
        flog2 += self.save_thxl(doc_y, doc_x, name_y, result)
        print(f"{name_x}----->{name_y} 完成")
        if flog1:
            print("报错还原")
            result.add(f'请检查“{name_x}”的折扣名有没有错')
            self.save_thxl(doc_x, doc_x, name_x, result)
        elif flog2:
            print("报错还原")
            result.add(f'请检查“{name_y}”的折扣名有没有错')
            self.save_thxl(doc_y, doc_y, name_y, result)
            self.save_thxl(doc_x, doc_x, name_x, result)
        else:
            self.collection.update_one({"name": name_x}, {"$set": {
                "proid": doc_y['proid']
            }})
            self.collection.update_one({"name": name_y}, {"$set": {
                "proid": doc_x['proid']
            }})

            actdocx = [i for i in collect_act.find({"spuId": porid_x})]
            actdocy = [i for i in collect_act.find({"spuId": porid_y})]

            for doc in actdocx:
                collect_act.update_one({"name": doc['name'], "spec": doc['spec']}, {
                    "$set": {"spuId": porid_y, "orderLimit": doc['orderLimit'], "daylimit": doc['daylimit']}})
            for doc in actdocy:
                collect_act.update_one({"name": doc['name'], "spec": doc['spec']}, {
                    "$set": {"spuId": porid_x, "orderLimit": doc['orderLimit'], "daylimit": doc['daylimit']}})

        # time.sleep(4)
        doc_x = self.collection.find_one({'name': name_x})
        doc_y = self.collection.find_one({'name': name_y})

        porid_x = doc_x['proid']
        porid_y = doc_y['proid']

        self.add_updata(doc_x, collect_act, name_x, porid_x)
        self.add_updata(doc_y, collect_act, name_y, porid_y)

        print(name_y)
        flog_x = self.yichangtianjia(collect_act, porid_x)
        if flog_x:
            result1 = set()
            self.save_thxl(doc_x, doc_x, name_x, result)
            if len(result1):
                print(result1)
            flog_x = self.yichangtianjia(collect_act, porid_x, 0)
            self.save_thxl(doc_x, doc_x, name_x, result)

        print(name_x)
        flog_y = self.yichangtianjia(collect_act, porid_y)
        if flog_y:
            result1 = set()
            self.save_thxl(collect_act, doc_y, doc_y, name_y, result)
            if len(result1):
                print(result1)
            flog_y = self.yichangtianjia(collect_act, porid_y, 0)
            self.save_thxl(doc_y, doc_y, name_y, result)

        time.sleep(5)
        self.updata_add(collect_act, porid_x)
        self.updata_add(collect_act, porid_y)

        self.add_updata(doc_x, collect_act, name_x, porid_x)
        self.add_updata(doc_x, collect_act, name_y, porid_y)
        return result

    # 结束替换失败还原




    # 添加商品设置

    def set_wmProductSkuVos_create(self, dic1, boxPrice):
        # print(dic1, 'dic1')
        sr1 = []
        arr = {}
        # self.set_aa(list(dic1.keys()), 0, dic1, sr1, arr)
        productsk = []
        # print(arr)
        pattern = r'\([^()]*\)'
        for val in dic1:
            dic2 = {"unit": '1个', "box_price": boxPrice, "spec": val,
                    "weight": "1",
                    "wmProductLadderBoxPrice": {"status": 1, "ladder_num": "1",
                                                "ladder_price": boxPrice},
                    "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
                                       "auto_refresh": 0},
                    "attrList": {"name": "份量", "name_id": 0, "value": val, "value_id": 0, "no": 0},
                    }
            productsk.append(dic2)

        return productsk

    def add_product(self, df, result):
        url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
        tag_url = "https://e.waimai.meituan.com/reuse/product/food/w/saveTagInfo"
        dic1 = {}
        dict1 = {}
        for key, val in df.iterrows():
            dic1[val.iloc[2]] = dic1.get(val.iloc[2], '') + str(val.iloc[3]) + "=" + str(val.iloc[4]) + "#"

        print(dic1)
        df_unique = df.drop_duplicates(subset='商品名称', keep='first')
        tag_list = set(df_unique['分类名称'].to_list())
        for i, tag_name in enumerate(tag_list):
            post_data = {
                'tagInfo': json.dumps(
                    {"id": "", "name": tag_name, "description": "", "top_flag": 0, "tag_type": 0,
                     "time_zone": {"1": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "2": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "3": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "4": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "5": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "6": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "7": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}]},
                     "sequence": 10 + i}, ensure_ascii=False),
                'wmPoiId': self.poi_id
            }

            # print(post_data, new_poi_id)
            # print(post_data)
            res = self.session.post(tag_url, data=post_data)
            print(res.text)
        tegs = self.get_tag()
        for i in tegs:
            dict1[i['name']] = i['id']

        # print(dic1['提拉米苏蛋糕'])
        err = 0
        for key, val in df_unique.iterrows():
            try:
                name = val['商品名称']
                spec = dic1[name]
                description = val['描述']
                attribute = "" if pd.isna(val['属性']) else val['属性']
                min_order_count = val['最小购买量']
                boxPrice = val["餐盒价格"]
                tag_name = val['分类名称']

                properties_values = {
                    "1000000003": [
                        {"customized": 0, "enumLimit": -1, "id": 161284, "inputTypeLimit": "1", "input_type": 1,
                         "is_leaf": 1,
                         "is_required": 1, "keyProperty": 0, "level": 2, "maxLength": 0, "multiSelect": 0,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 3, "wm_product_lib_tag_id": 1000000003,
                         "wm_product_lib_tag_name": "口味",
                         "wm_product_property_template_id": 8, "value_id": 133, "value": "原味"}],

                    "1000000004": [
                        {"customized": 0, "enumLimit": -1, "id": 161285, "inputTypeLimit": "1", "input_type": 1,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": 0, "multiSelect": 0,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 4, "wm_product_lib_tag_id": 1000000004,
                         "wm_product_lib_tag_name": "凉热",
                         "wm_product_property_template_id": 8, "value_id": 139, "value": "热"}],

                    "1000000008": [
                        {"customized": 0, "enumLimit": -1, "id": 161288, "inputTypeLimit": "", "input_type": 2,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": -1, "multiSelect": 1,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 7, "wm_product_lib_tag_id": 1000000008,
                         "wm_product_lib_tag_name": "时段",
                         "wm_product_property_template_id": 8, "value_id": 108861, "value": "晚餐"},
                        {"customized": 0, "enumLimit": -1, "id": 161288, "inputTypeLimit": "", "input_type": 2,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": -1, "multiSelect": 1,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 7, "wm_product_lib_tag_id": 1000000008,
                         "wm_product_lib_tag_name": "时段",
                         "wm_product_property_template_id": 8, "value_id": 147, "value": "早餐"},
                        {"customized": 0, "enumLimit": -1, "id": 161288, "inputTypeLimit": "", "input_type": 2,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": -1, "multiSelect": 1,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 7, "wm_product_lib_tag_id": 1000000008,
                         "wm_product_lib_tag_name": "时段",
                         "wm_product_property_template_id": 8, "value_id": 150, "value": "夜宵"},
                        {"customized": 0, "enumLimit": -1, "id": 161288, "inputTypeLimit": "", "input_type": 2,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": -1, "multiSelect": 1,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 7, "wm_product_lib_tag_id": 1000000008,
                         "wm_product_lib_tag_name": "时段",
                         "wm_product_property_template_id": 8, "value_id": 110237, "value": "午餐"},
                        {"customized": 0, "enumLimit": -1, "id": 161288, "inputTypeLimit": "", "input_type": 2,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": -1, "multiSelect": 1,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 7, "wm_product_lib_tag_id": 1000000008,
                         "wm_product_lib_tag_name": "时段",
                         "wm_product_property_template_id": 8, "value_id": 149, "value": "下午茶"}],

                    "1000000015": [
                        {"customized": 0, "enumLimit": 1, "id": 161282, "inputTypeLimit": "1", "input_type": 7,
                         "is_leaf": 1,
                         "is_required": 1, "keyProperty": 0, "level": 2, "maxLength": 0, "multiSelect": 1,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 1, "wm_product_lib_tag_id": 1000000015,
                         "wm_product_lib_tag_name": "主料",
                         "wm_product_property_template_id": 8, "value": "猪肉", "value_id": 816}],

                    "1000000027": [
                        {"customized": 0, "enumLimit": -1, "id": 161289, "inputTypeLimit": "", "input_type": 1,
                         "is_leaf": 1,
                         "is_required": 2, "keyProperty": 0, "level": 2, "maxLength": -1, "multiSelect": 0,
                         "parent_tag_id": 0,
                         "prompt_document": "", "sequence": 8, "wm_product_lib_tag_id": 1000000027,
                         "wm_product_lib_tag_name": "包装特色",
                         "wm_product_property_template_id": 8, "value_id": 109468, "value": "环保"}]
                }
                category_id = 90000106
            except Exception as e:
                print(e)
                continue
            try:
                attrList, attrdic = self.set_attribute_yj(spec, attribute)
                wmProducList = self.set_wmProductSkuVos_create(attrdic['份量'], boxPrice)
                # print(attrList, document['name'])
                bb = {"description": description, "name": name, "wm_poi_id": self.poi_id,
                      "tag_id": dict1[tag_name], "tag_name": tag_name,
                      "isShippingTimeSyncPoi": 2, "shipping_time_x": "-", "min_order_count": min_order_count,
                      "wmProductPics": [
                          {"pic_large_url": "",  # 选择图片
                           "pic_small_url": "",
                           "quality_score": -9, "specialEffectEnable": 0, "picPropagandaList": [],
                           "picExtend": "{\"source\":5}",
                           "imagePickType": 0, "sequence": 0}], "specialEffectPic": None,
                      "category_id": category_id,  # 分类选项
                      "labelList": [],
                      "newSpuAttrs": attrList,
                      "stockAndBoxPriceSkus": wmProducList,
                      "unifiedPackagingFee": 2,
                      "wmProductLadderBoxPrice": {"status": 1, "ladder_num": 1, "ladder_price": ""},
                      "wmProductStock": {"id": 0, "stock": 10000, "max_stock": 10000, "auto_refresh": 1},
                      "productCardDisplayContent": "", "wmProductVideo": {}, "singleOrderNoDelivery": 0,
                      "onlySellInCombo": False,
                      "properties_values":
                          properties_values,
                      "suggestTraceInfoList": [
                          {"setTraceId": True, "setTraceType": True, "traceId": "4008459803303154213",
                           "traceType": 100003},
                          {"setTraceId": True, "setTraceType": True, "traceId": "-53536320223525572",
                           "traceType": 100002},
                          {"setTraceId": True, "setTraceType": True, "traceId": "4473829507692099121",
                           "traceType": 100001},
                          {"setTraceId": True, "setTraceType": True, "traceId": "5928610738252008318",
                           "traceType": 100001},
                          {"setTraceId": True, "setTraceType": True, "traceId": "-7555290018422721229",
                           "traceType": 100001}]}

                # print(bb)
                wmFoodVoJson02 = [bb]
                post_data = {
                    'wmPoiId': self.poi_id,
                    'entranceType': 0,
                    'userType': 0,
                    'wmFoodVoJson': json.dumps(wmFoodVoJson02)
                }
                num = 0

                while self.max_num > num:
                    try:
                        response = self.session.post(url, data=post_data)
                        json_data = response.json()
                        if json_data['msg'] != 'success':
                            print(json_data['msg'], name)
                            result.add(json_data['msg'] + ' ' + name)

                            # 判断json_data中的msg是否包含“已有同名商品”
                            if '已有同名商品' in json_data['msg']:
                                break
                            num += 1
                            time.sleep(5)
                            err += 1
                            continue
                        print(json_data)
                        err = 0
                        break
                    except requests.exceptions.ReadTimeout:
                        print("请求超时，请手动修改", name)
                        num += 1
                        err += 1
                        time.sleep(5)
                    except Exception as e:
                        print(e, name)
                        err += 1
                        result.add(name)

            except Exception as e:
                print(e)

            if err >= 30:
                return "0"

    #  结束添加商品

    # 删除商品设置
    def del_tagname(self, tagid):
        data = {
            'tagId': tagid,
            'wmPoiId': self.poi_id,
        }
        response = self.session.post(
            'https://e.waimai.meituan.com/reuse/product/food/w/deleteTagById',
            data=data,
        )
        print(response.json())

    def del_pro(self, pro_ids):
        url = 'https://e.waimai.meituan.com/reuse/product/food/w/batchDelete'
        data = {
            'opTab': 0,
            'tagCat': 1,
            'wmPoiId': self.poi_id,
            "skuIds": pro_ids,
            "viewStyle": 0,
            'v2': 1
        }
        res = self.session.post(url, data=data).json()
        print(res)

    def get_tage_product(self, target):
        # 获取商品
        url = 'https://e.waimai.meituan.com/gw/bizproduct/v3/food/r/getSpuListCommon?ignoreSetRouterProxy=true'
        tage_names = self.get_tag()
        # print(tage_names)
        tag_data = None
        for i in tage_names:
            if i['name'] == target:
                tag_data = i

        assert tag_data is not None, '没有找到该标签'
        pro_ids = ''
        pro_num = 0
        pageNum = self.zz(tag_data['spuCount'], 30)
        for j in range(pageNum):
            print(j)
            pro_ids = ''
            data = {
                'tagId': tag_data['id'],
                'pageNum': 1,
                'pageSize': '30',
                'needAllCount': '1',
                'tabStatus': '-1',
                'inRecycleBin': '0',
                'wmPoiId': self.poi_id,  # 店铺id
                'appType': '3'
            }
            print(data)
            num = 0
            # response = session.post(url, data=data)
            while self.max_num > num:
                try:
                    response = self.while_fun(requests.post, headers=self.headers, url=url, data=data)
                    if response.status_code == 200:
                        json_data = response.json()
                        for k in json_data['data']['spuListVos']:
                            for n in k['wmProductSkuVos']:
                                pro_ids += str(n['id']) + ','
                        # print(pro_ids)
                        self.del_pro(pro_ids)
                        break

                    else:
                        print('请求失败', response.json())
                        num += 1
                        time.sleep(5)
                        continue

                except Exception as e:
                    print(e)
                    num += 1
                    time.sleep(5)
                    continue

        return tag_data

    def del_product(self, tagname):
        # 删除商品
        tag_data = self.get_tage_product(tagname)
        self.del_tagname(tag_data['id'])

        return 0


#     结束删除商品设置


if __name__ == '__main__':
    # asyncio
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    cookie = "_lxsdk_cuid=190a0db1af4c8-0cd06bc2f88d9d-26001c51-1fa400-190a0db1af4c8; device_uuid=!94d7445a-a2ed-47d7-8010-8432028f6322; uuid_update=true; pushToken=09pEkZvq6nDmuDqh6CFubPArvfISAWHgGDcJYvydSSU0*; _lxsdk=!94d7445a-a2ed-47d7-8010-8432028f6322; WEBDFPID=yz76y3w74x6u545011zy346vz1340642809ww35v0wx97958y4wv89z8-2037061296710-1721701296710OCEKKIQfd79fef3d01d5e9aadc18ccd4d0c95072811; acctId=97786666; token=0SMpnRePP2E0A1ZnrE-cgmrVH6yGdwFahVU6Q7toqTDQ*; isOfflineSelfOpen=0; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=gX96DeBVSLMlUKtxsf0_d0TITUbwiPo2fd1a9y5dP0SBIBZ3fqXqg1iWXhgUhMFG8y9mqqgt15BY5bPRg6nqrA; city_location_id=0; location_id=0; has_not_waimai_poi=0; onlyForDaoDianAcct=0; cityId=440300; provinceId=440000; logistics_support=; setPrivacyTime=3_20240819; wmPoiId=23866026; wmPoiName=%E5%B5%8A%E5%B7%9E%E5%B0%8F%E5%90%83(%E5%B0%8F%E7%AC%BC%E5%8C%85%C2%B7%E7%B2%A5%C2%B7%E6%B1%A4%E7%B2%89%E9%9D%A2); set_info_single=%7B%22regionIdForSingle%22%3A%221000330200%22%2C%22regionVersionForSingle%22%3A1720677971%7D; _source=APP; acctName=13922879731; uuid=!94d7445a-a2ed-47d7-8010-8432028f6322; igateApp=igate; shopCategory=food; JSESSIONID=1isjmsoamxsrm16ne2s8rnnveu; wpush_server_url=wss://wpush.meituan.com; set_info=%7B%22wmPoiId%22%3A23866026%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=oz1egk12otfyahez018k; _lxsdk_s=191684f53ff-dd1-da2-f97%7C201322941%7C4540"

    poi_id = '23866026'

    jx = JX(poi_id, cookie)

    # jx.run_Recover("11199362_0")

    # jx.get_product()

    # df = pd.read_excel(r"G:\updata\夹心\test.xls")
    #
    # jx.updata_jx(df, set(), 1)

    # document = jx.collection.find_one({"name": "提拉米苏蛋糕"}) getProductThreshold

    # df = pd.read_excel(r'G:\updata\test\test2.xlsx', engine='openpyxl')
    # df = pd.read_excel(r'G:\updata\test\test2.xls')
    # info = '夹心选择一#甜甜黄桃果肉🍑#进口新鲜火龙果💕#新鲜美味芒果肉🥭#醇厚奥利奥碎🍪  #酸甜草莓果馅#新鲜美味芒果果馅🥭##夹心选择二#甜甜黄桃果肉🍑#进口新鲜火龙果💕#新鲜美味芒果肉🥭#醇厚奥利奥碎🍪  #酸甜草莓果馅#新鲜美味芒果果馅🥭##'
    # resultj = set()
    # jx.updata_jx(df, resultj, 1)
    # jx.set_bb(document, '', info, 0)

    # df = pd.read_excel(r'G:\updata\原价\test.xlsx')
    # jx.yanjia(df)
    # jx.updata_jx(df, set(), 1)

    # result = set()
    # df = pd.read_excel(r'G:\updata\test\刷打包费1-.xlsx', engine='openpyxl')
    # jx.add_product(df, result)
    # print(result)

    tagers = [
        '店铺公告1',
        '店铺公告2',
        '店铺公告3',
        '店铺公告4',
        '店铺公告5',
        '店铺公告6',
    ]
    for i in tagers:
        res = jx.del_product(i)
        print(res)

    # doc = jx.collection.find_one({"name": '指谁谁发财生日蛋糕'})
    # jx.set_properties(doc['mapSpuExtendList'])

    # result = set()
    # docx = jx.collection.find_one({"name": '只许一人终老节日蛋糕'})
    # jx.save_thxl(docx, docx, '只许一人终老节日蛋糕', result)

    # jx.replace_product("生日蜡烛", "【“石”分喜歡   “榴”你身邊】秋天的石榴生日蛋糕", result)
    # jx.get_product_v2()
    # print(result)
    '''
    {'份量': ['10人份'], '口味': ['不辣', '微辣', '中辣', '特辣'], '自选粉面': ['米粉', '河粉', '面条'], '薄皮小笼包（5个）': ['鲜肉蒸饺（5个）', '玉米蒸饺（5个）'], '汤/饮料/小吃': ['现磨豆浆（热的）', '现磨豆浆（冰的）', '百事可乐', '冰红茶', '茶叶蛋（1个）', '荷包蛋（1个）', '咸鸭蛋（1个）']}

    '''
