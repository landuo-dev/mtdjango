import requests
from pymongo import MongoClient
import json
from pymongo import MongoClient
import pandas as pd
import time
import re

from Custom_features.get_tag import get_tag
from Custom_features.del_tag import del_tagname


def set_attribute(attrList01, attrList02, chenCheng=''):
    attributes = []
    if not len(attrList01):
        return '错误'

    for index, i in enumerate(attrList01):
        if i['value']:
            value = i['value'] + chenCheng
        else:
            value = ''
        attributes.append(
            {"name": i['name'], "name_id": i['name_id'], "price": i['price'], "value": value,
             "value_id": i['value_id'], "no": 0,
             "mode": i['mode'],
             "weight": i['weight'], "weightUnit": i['weightUnit'], "sell_status": i['sell_status'],
             "value_sequence": i['value_sequence'], "unitType": 1
             }
        )

    if not len(attrList02):
        return attributes
    attrList02.sort(key=lambda x: x['name'])
    name = attrList02[0]['name']
    indx = 1
    num = 1
    for index, i in enumerate(attrList02):
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
            {"name": i['name'], "name_id": 0, "value": i['value'], "value_id": 0, "price": int(i['price']), "no": num,
             "mode": i['mode'], "value_sequence": indx, "weight": number, "weightUnit": '个', "sell_status": 0
             })
        indx += 1
    return attributes


def set_wmProductSkuVos(sk):
    productsk = []
    for i, val in enumerate(sk):
        productsk.append(
            {"price": val['price'], "unit": "1个", "box_price": str(min(int(val['boxPrice']), 5)), "spec": val['spec'],
             "weight": "1",
             "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['boxNum'],
                                         "ladder_price": str(min(int(val['boxPrice']), 5))},
             "wmProductStock": {"id": "0", "stock": val['stock'], "max_stock": val['stock'],
                                "auto_refresh": 1},
             "attrList": [{"name": "份量", "name_id": 0, "value": val['spec'].split('(')[0], "value_id": 0, "no": 0}]},
        )
    return productsk



def add_product(old_poi_id, new_poi_id, description, cookie, dict1, result):
    # 创建 MongoDB 客户端
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client[str(old_poi_id)]
    collection = db['prodata']
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
    arr = list(collection.find())[::-1]

    session = requests.session()
    session.headers = headers
    session.cookie = cookie
    err = 0
    for document in arr:
        description = document.get('description', '') if description == '' else description
        min_order_count = document.get('min_order_count', 1)
        try:
            attrList = set_attribute(document['attrList01'], document['attrList02'])
            # print(attrList, document['name'])
            bb = {"description": description, "name": document['name'], "wm_poi_id": new_poi_id,
                  "tag_id": dict1[document['tagName']], "tag_name": document['tagName'],
                  "isShippingTimeSyncPoi": 2, "shipping_time_x": "-", "min_order_count": min_order_count,
                  "wmProductPics": [
                      {"pic_large_url": document['defaultPicUrl'],
                       "pic_small_url": document['defaultPicUrl'],
                       "quality_score": -9, "specialEffectEnable": 0, "picPropagandaList": [],
                       "picExtend": "{\"source\":5}",
                       "imagePickType": 0, "sequence": 0}], "specialEffectPic": None,
                  "category_id": document['spTagId'],
                  "labelList": document['wmProductLabelVos'],
                  "newSpuAttrs": attrList,
                  "stockAndBoxPriceSkus": set_wmProductSkuVos(document['wmProductSkuVos']),
                  "unifiedPackagingFee": 2,
                  "wmProductLadderBoxPrice": {"status": 1, "ladder_num": 1, "ladder_price": ""},
                  "wmProductStock": {"id": 0, "stock": 10000, "max_stock": 10000, "auto_refresh": 1},
                  "productCardDisplayContent": "", "wmProductVideo": {}, "singleOrderNoDelivery": 0,
                  "onlySellInCombo": False,
                  "properties_values": {
                      "1000000003": [
                          {"customized": 0, "enumLimit": -1, "id": 161724, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 2,
                           "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 6, "wm_product_lib_tag_id": 1000000003, "wm_product_lib_tag_name": "口味",
                           "wm_product_property_template_id": 5510, "value_id": 99, "value": "甜"},
                          {"customized": 0, "enumLimit": -1, "id": 161730, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 1,
                           "is_required": 2, "level": 3, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 1000000003,
                           "prompt_document": "", "sequence": 2, "wm_product_lib_tag_id": 99,
                           "wm_product_lib_tag_name": "甜",
                           "wm_product_property_template_id": 5510, "value_id": 101, "value": "甜味"},
                          {"customized": 0, "enumLimit": -1, "id": 161724, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 2,
                           "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 6, "wm_product_lib_tag_id": 1000000003, "wm_product_lib_tag_name": "口味",
                           "wm_product_property_template_id": 5510, "value_id": 99, "value": "甜"}], "1000000006": [
                          {"customized": 0, "enumLimit": -1, "id": 161723, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 1,
                           "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 5, "wm_product_lib_tag_id": 1000000006, "wm_product_lib_tag_name": "制作方法",
                           "wm_product_property_template_id": 5510, "value_id": 256, "value": "烘焙"}], "1000000015": [
                          {"customized": 0, "enumLimit": 1, "id": 161719, "inputTypeLimit": "", "input_type": 7,
                           "is_leaf": 1,
                           "is_required": 1, "level": 2, "maxLength": -1, "multiSelect": 1, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 1, "wm_product_lib_tag_id": 1000000015, "wm_product_lib_tag_name": "主料",
                           "wm_product_property_template_id": 5510, "value": "蛋糕胚", "value_id": 112331}],
                      "1000000027": [
                          {"customized": 0, "enumLimit": -1, "id": 161727, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 1,
                           "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 9, "wm_product_lib_tag_id": 1000000027,
                           "wm_product_lib_tag_name": "包装特色",
                           "wm_product_property_template_id": 5510, "value_id": 110309, "value": "定制设计"}],
                      "1000000048": [
                          {"customized": 0, "enumLimit": -1, "id": 161728, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 1,
                           "is_required": 1, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 10, "wm_product_lib_tag_id": 1000000048,
                           "wm_product_lib_tag_name": "是否自制",
                           "wm_product_property_template_id": 5510, "value_id": 113857, "value": "自制"}],
                      "1200004473": [
                          {"customized": 0, "enumLimit": -1, "id": 161726, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 1,
                           "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 8, "wm_product_lib_tag_id": 1200004473,
                           "wm_product_lib_tag_name": "制作时长~蛋糕",
                           "wm_product_property_template_id": 5510, "value_id": 1300019364, "value": "0~半小时"}],
                      "1200189639": [
                          {"customized": 0, "enumLimit": -1, "id": 161729, "inputTypeLimit": "", "input_type": 1,
                           "is_leaf": 1,
                           "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                           "prompt_document": "",
                           "sequence": 11, "wm_product_lib_tag_id": 1200189639,
                           "wm_product_lib_tag_name": "蛋糕场景用途",
                           "wm_product_property_template_id": 5510, "value_id": 1300019431,
                           "value": "以上场景通用"}]},
                  "suggestTraceInfoList": [
                      {"setTraceId": True, "setTraceType": True, "traceId": "4008459803303154213", "traceType": 100003},
                      {"setTraceId": True, "setTraceType": True, "traceId": "-53536320223525572", "traceType": 100002},
                      {"setTraceId": True, "setTraceType": True, "traceId": "4473829507692099121", "traceType": 100001},
                      {"setTraceId": True, "setTraceType": True, "traceId": "5928610738252008318", "traceType": 100001},
                      {"setTraceId": True, "setTraceType": True, "traceId": "-7555290018422721229",
                       "traceType": 100001}]}

            # print(bb)
            wmFoodVoJson02 = [bb]
            post_data = {
                'wmPoiId': new_poi_id,
                'entranceType': 0,
                'userType': 0,
                'wmFoodVoJson': json.dumps(wmFoodVoJson02)
            }
            num = 0
            while 3 > num:
                try:
                    response = session.post(url, data=post_data)
                    json_data = response.json()
                    if json_data['msg'] != 'success':
                        print(json_data['msg'], document['name'])
                        result.add(json_data['msg'] + ' ' + document['name'])

                        # 判断json_data中的msg是否包含“已有同名商品”
                        if '已有同名商品' in json_data['msg']:
                            break
                        num += 1
                        time.sleep(1)
                        err += 1
                        continue
                    print(json_data)
                    err = 0
                    break
                except requests.exceptions.ReadTimeout:
                    print("请求超时，请手动修改", document['name'])
                    num += 1
                    err += 1
                    time.sleep(1)
                except Exception as e:
                    print(e, document['name'])
                    err += 1
                    result.add(document['name'])

        except Exception as e:
            print(e)

        if err >= 30:
            return "0"


def move_pro(old_poi_id, new_poi_id, description, cookie_new, cookie_old, result):
    # result = set()
    dict1 = {}

    tags_new = get_tag(new_poi_id, cookie_new)
    for i in tags_new:
        del_tagname(new_poi_id, i['id'], cookie_new)

    tags = get_tag(old_poi_id, cookie_old)

    for i in tags:
        dict1[i['name']] = i['id']

    url = "https://e.waimai.meituan.com/reuse/product/food/w/saveTagInfo"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': cookie_new,
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
    session = requests.session()
    session.headers = headers
    session.cookie = cookie_new
    chang = len(tags) + 100
    for i, val in enumerate(tags):
        if dict1.get(val['name'], 0):
            print(val['name'])
            post_data = {
                'tagInfo': json.dumps(
                    {"id": "", "name": val['name'], "description": "", "top_flag": 0, "tag_type": 0,
                     "time_zone": {"1": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "2": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "3": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "4": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "5": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "6": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}],
                                   "7": [{"start": "00:00", "end": "23:59", "time": "00:00-23:59"}]},
                     "sequence": chang + i}),
                'wmPoiId': str(new_poi_id)
            }
            # print(post_data, new_poi_id)
            res = session.post(url, data=post_data, headers=headers)
            print(res.text)

    tegs = get_tag(new_poi_id, cookie_new)
    for i in tegs:
        dict1[i['name']] = i['id']

    flog = 1
    flog = add_product(old_poi_id, new_poi_id, description, cookie_new, dict1, result)
    return flog


if __name__ == '__main__':
    new_poid, old_poid = 24368919, 24343873

    cookie_new = "_lxsdk_cuid=18ecfe70f19c8-053bc20de9f5f7-26001b51-1fa400-18ecfe70f19c8; _lxsdk=18ecfe70f19c8-053bc20de9f5f7-26001b51-1fa400-18ecfe70f19c8; device_uuid=!a872b6f5-f83c-4286-b560-e138826d7cec; uuid_update=true; pushToken=0nIZj3B_LinFqiwrhDfunX124caw0KHxKieouFQ2LELs*; WEBDFPID=vxwwy223wyvw5wvxyz68426y169u7x6381vw46yuz43979589zx3w31z-2028334451068-1712974451068ISEUCQGfd79fef3d01d5e9aadc18ccd4d0c95072090; shopCategory=food; acctId=205819758; token=0tlXPy7jiwnFS2rZugztm-DNb8PjCQKodre_BJB5B_Ek*; wmPoiId=24368919; isOfflineSelfOpen=1; city_id=150100; isChain=0; ignore_set_router_proxy=false; region_id=1000150100; region_version=1723804352; bsid=Rd6WrtkAijA4hKWmlkY7WLlKKv5qRKJoaxZOMhrlTgZ_qVuYLCgWDcH2ZaRzCGPEG9xn5BbOKUKC62uGlSTtvg; city_location_id=150100; location_id=150105; has_not_waimai_poi=0; onlyForDaoDianAcct=0; cityId=440300; provinceId=440000; set_info_single=%7B%22regionIdForSingle%22%3A%221000150100%22%2C%22regionVersionForSingle%22%3A1723804352%7D; set_info=%7B%22wmPoiId%22%3A%2224368919%22%2C%22region_id%22%3A%221000150100%22%2C%22region_version%22%3A1723804352%7D; wpush_server_url=wss://wpush.meituan.com; JSESSIONID=1ahnu9pufjokv1ek56vccbgk46; logan_session_token=v64pww741b7uj3ify83c; _lxsdk_s=191686c30a3-fbf-2ba-b7f%7C%7C77"

    cookie_old = "_lxsdk_cuid=18ecfe70f19c8-053bc20de9f5f7-26001b51-1fa400-18ecfe70f19c8; _lxsdk=18ecfe70f19c8-053bc20de9f5f7-26001b51-1fa400-18ecfe70f19c8; device_uuid=!a872b6f5-f83c-4286-b560-e138826d7cec; uuid_update=true; pushToken=0nIZj3B_LinFqiwrhDfunX124caw0KHxKieouFQ2LELs*; WEBDFPID=vxwwy223wyvw5wvxyz68426y169u7x6381vw46yuz43979589zx3w31z-2028334451068-1712974451068ISEUCQGfd79fef3d01d5e9aadc18ccd4d0c95072090; acctId=194003691; token=0CkVFOCaTGw8KabDL5W4H6FhcyLJyMaoQN37PvPjCZ1E*; wmPoiId=24343873; isOfflineSelfOpen=1; city_id=150105; isChain=0; ignore_set_router_proxy=false; region_id=1000150100; region_version=1723697752; bsid=HQjBBmnynetHzDLu1Y6bDpGlJ1Kp3QaoG_lDLF2bsTglAbeVsA_3ZEql1V_fxrlUNu1_AMRnorOLm1xpVeujHQ; city_location_id=150100; location_id=150105; has_not_waimai_poi=0; onlyForDaoDianAcct=0; cityId=440300; provinceId=440000; set_info_single=%7B%22regionIdForSingle%22%3A%221000150100%22%2C%22regionVersionForSingle%22%3A1723697752%7D; set_info=%7B%22wmPoiId%22%3A%2224343873%22%2C%22region_id%22%3A%221000150100%22%2C%22region_version%22%3A1723697752%7D; shopCategory=food; wpush_server_url=wss://wpush.meituan.com; JSESSIONID=j5p049q5vrxzpgafcwsj1d44; logan_session_token=wstsp95sdyjh50du37le; _lxsdk_s=19159f1aa9a-ef1-088-93%7C%7C884"
    dis = '''
    '''
    result = set()
    move_pro(old_poid, new_poid, dis, cookie_new, cookie_old, result)
    print(result)

    #     更新新店的数据库
    # main01(new_poid, headers1)
    # print('任务1完成')
    # main02(new_poid)
    # print('完成')

    # client = MongoClient('mongodb://localhost:27017/')
    # db = client['actproduct']
    # collect = db['21335860']
    #
    # collect.update_many({"tagName": "情侣纪念︵💘︵"}, {"$set": {"tagName": "情侣婚庆︵💘︵"}})

"""

白富美【人间富婆】生日蛋糕

"""
