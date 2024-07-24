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
            {"unit": "1个", "box_price": val['boxPrice'], "spec": val['spec'],
             "weight": "1",
             "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['ladder_num'],
                                         "ladder_price": val['boxPrice']},

             "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
                                "auto_refresh": 1},

             "attrList": val['attrList']
             },
        )
    return productsk


def add_product(new_poi_id, document, description, session, result):
    err = 0
    url = 'https://e.waimai.meituan.com/reuse/product/food/w/save'
    if document:
        description = document.get('description', '') if description == '' else description
        min_order_count = document.get('min_order_count', 1)
        try:
            attrList = set_attribute(document['attrList01'], document['attrList02'])
            # print(attrList, document['name'])
            bb = {"description": description, "name": document['name'], "wm_poi_id": new_poi_id,
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
                  "newSpuAttrs": attrList,
                  "stockAndBoxPriceSkus": set_wmProductSkuVos(document['wmProductSkuVos']),
                  "unifiedPackagingFee": 2,
                  "wmProductLadderBoxPrice": {"status": 1, "ladder_num": "", "ladder_price": ""},  # 包装费
                  "wmProductStock": {"id": 0, "stock": "10000", "max_stock": "10000", "auto_refresh": 1},
                  "productCardDisplayContent": "", "wmProductVideo": None, "singleOrderNoDelivery": 0,
                  "onlySellInCombo": False,
                  "id": document['proid'],
                  "properties_values":
                      {
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

                  "labelValues": [{"sequence": 1, "value": ""}, {"sequence": 2, "value": ""}], "suggestTraceInfoList": [
                    {"setTraceId": True, "setTraceType": True, "traceId": "897162237673668406", "traceType": 100002}]}

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


if __name__ == '__main__':

    cookie = "_lxsdk_cuid=1907674a096c8-06ae10f67ea48e-26001d51-1fa400-1907674a096c8; _lxsdk=1907674a096c8-06ae10f67ea48e-26001d51-1fa400-1907674a096c8; device_uuid=!67ffb930-2b2f-4166-b4b0-dd4816931fd5; uuid_update=true; pushToken=0QnFMD5KqStXzYgWvlYyxvIgybuHhCZ6V9HPWUW4S5Hc*; WEBDFPID=60v4x02764315xy2y3u3217568yzy19y80923y9w26v97958yu872u7v-2035338216679-1719978216679OEAGYAOfd79fef3d01d5e9aadc18ccd4d0c95072970; acctId=97786666; token=0e7QhkVo1nQ9xoaSJFZIOqkZteJK_P7iIjuz-2mtehhk*; isOfflineSelfOpen=0; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=r0JrEXOwoyRI-PuEnuiS83jIx57_weqsbL2nsUGgBfZrYPT2eiiC44I1uXy7rJ7f8GuHol-UHjSlSomq-cixlg; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; wmPoiId=22554404; wmPoiName=MONTO%E5%8A%A8%E7%89%A9%E5%A5%B6%E6%B2%B9%C2%B7%E6%89%8B%E5%B7%A5%E8%89%BA%E7%94%9F%E6%97%A5%E8%9B%8B%E7%B3%95%EF%BC%88%E5%8D%97%E6%98%8C%E6%97%97%E8%88%B0%E5%BA%97%EF%BC%89; logistics_support=; set_info_single=%7B%22regionIdForSingle%22%3A%221000360100%22%2C%22regionVersionForSingle%22%3A1718860061%7D; setPrivacyTime=3_20240715; shopCategory=food; wpush_server_url=wss://wpush.meituan.com; set_info=%7B%22wmPoiId%22%3A22554404%2C%22ignoreSetRouterProxy%22%3Atrue%7D; JSESSIONID=1uoml8f0cdx4m1c4nez8luspg0; logan_session_token=vcye0d3udv2msa948093; _lxsdk_s=190b5051b57-fd3-3ca-f93%7C%7C8121"

    pri_id = '22554404'
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
    session = requests.session()
    session.headers = headers
    # 创建 MongoDB 客户端
    client = MongoClient('mongodb://localhost:27017/')
    # 选择数据库和集合（相当于 SQL 中的表）
    db = client['test']
    collection = db[str(pri_id)]


    result = set()

    df = pd.read_excel(r'G:\updata\test\MONTO南昌旗舰店.xlsx', engine='openpyxl')
    for key, val in df.iterrows():
        name = val['商品name']
        description = val['描述']
        document = collection.find_one({"name": name})
        # print(document)
        add_product(pri_id, document, description, session, result)