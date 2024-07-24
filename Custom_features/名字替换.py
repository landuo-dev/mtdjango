from pymongo import MongoClient
import json
import re
import time
import requests
import traceback
import pandas as pd

from Custom_features.setting import while_fun


def set_attribute(attrList01, attrList02):
    attributes = []
    if not len(attrList01):
        return '错误'
    for index, i in enumerate(attrList01):
        number = 1
        if "个" in i['value']:
            try:
                number = re.findall(r'\d+', i['value'])[0]
            except Exception as e:
                print(e)
                number = 1
        attributes.append(
            {"name": i['name'], "name_id": 0, "price": int(i['price']), "value": i['value'], "value_id": 0, "no": 0,
             "mode": 2,
             "weight": number, "weightUnit": "个", "sell_status": 0, "value_sequence": index, "unitType": 1
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
             "mode": 1, "value_sequence": indx, "weight": 0, "weightUnit": '个', "sell_status": 0
             })
        indx += 1
    return attributes


def set_wmProductSkuVos(sk):
    productsk = []
    for i, val in enumerate(sk):
        productsk.append(
            {"unit": "1个", "box_price": str(int(val['boxPrice'])), "spec": val['spec'],
             "weight": "1",
             "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['boxNum'],
                                         "ladder_price": str(int(val['boxPrice']))},
             "wmProductStock": {"id": "0", "stock": val['stock'], "max_stock": val['maxStock'],
                                "auto_refresh": 1},
             "attrList": [{"name": "份量", "name_id": 0, "value": val['spec'].split('(')[0], "value_id": 0, "no": 0}]},
        )
    return productsk


def save(document, poi_id, name, description, cookie):
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
    try:
        attrList = set_attribute(document['attrList01'], document['attrList02'])
        wmProductSkuVos = set_wmProductSkuVos(document['wmProductSkuVos'])
        # break
        # print(attrList)
        # print(len(attributes))
        # break
        # 三个全黑
        bb = {"description": description, "name": name, "wm_poi_id": poi_id,
              "tag_id": document['tagId'],
              "tag_name": document['tagName'], "isShippingTimeSyncPoi": 2, "shipping_time_x": "-",
              "min_order_count": 1,
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
              "stockAndBoxPriceSkus": wmProductSkuVos,
              "unifiedPackagingFee": 2,
              "wmProductLadderBoxPrice": {"status": 1, "ladder_num": "", "ladder_price": ""},  # 包装费
              "wmProductStock": {"id": 0, "stock": "10000", "max_stock": "10000", "auto_refresh": 1},
              "productCardDisplayContent": "", "wmProductVideo": None, "singleOrderNoDelivery": 0,
              "onlySellInCombo": False,
              "id": document['proid'],
              "properties_values":
                  {"1000000003": [
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
        wmFoodVoJson02 = [bb]
        post_data = {
            'wmPoiId': poi_id,
            'entranceType': 2,
            'userType': 0,
            'wmFoodVoJson': json.dumps(wmFoodVoJson02)
        }

        response = while_fun(requests.post, url=url, headers=headers, data=post_data, time=5)
        json_data = response.json()
        if json_data['msg'] != 'success':
            print(json_data['msg'], name)
            reult += (str(json_data['msg']) + " " + name + '\n')
        print(json_data)
    except Exception as e:
        print(e)
        print(name)
        traceback.print_exc()
        # print(response.status_code, i)
        # print(response.json())

    return reult


def rep_name(poi_id, df, cookie):
    client = MongoClient('mongodb://localhost:27017/')
    db_pro = client['test']
    for i, val in df.iterrows():
        collect_pro = db_pro[poi_id]
        proid = val.iloc[0]
        name = val.iloc[2]
        dis = val.iloc[3]
        doc = collect_pro.find_one({'proid': int(proid)})
        if doc:
            save(doc, poi_id, name, dis, cookie)


if __name__ == '__main__':
    # client = MongoClient('mongodb://localhost:27017/')
    # db_pro = client['test']
    # arr = [
    #     {
    #         "poi_id": '19021228',
    #         "proid": "14869205793",
    #         "name": "甜蜜共享纸杯生日蛋糕🍒",
    #         "dis": " "
    #     }
    # ]
    # df = pd.DataFrame(arr)
    #
    # cookie = "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; wm_order_channel=sjzxpc; utm_source=60376; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; _ga_NMY341SNCF=GS1.3.1714902768.1.1.1714902798.0.0.0; acctId=97786666; token=0c13IljXjtIyG77Alt_zxFG0H3u-IsZAQAO3bo2rrDlI*; isOfflineSelfOpen=0; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=007ikcHy1UM5U02NYMNvDJmHO2RL6y6yC3JC2GD9ESMmjsNDchQuzEAkKsXJ8rwB6zVbIxCl3udgBInMPCP-NA; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; logistics_support=; setPrivacyTime=3_20240517; wmPoiId=19021228; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; JSESSIONID=seeufw8ygzy297zzoveyaddx; logan_session_token=tc3i9wo2zjndq37skkmg; _lxsdk_s=18f82c1e9ad-f07-744-8f5%7C97786666%7C3737"
    #
    # for i, val in df.iterrows():
    #     poi_id = str(int(val.iloc[0]))
    #     collect_pro = db_pro[poi_id]
    #     proid = val.iloc[1]
    #     name = val.iloc[2]
    #     dis = val.iloc[3]
    #     doc = collect_pro.find_one({'proid': int(proid)})
    #     print(doc)
    #     if doc:
    #         save(doc, poi_id, name, dis, cookie)

    """
    '简约威士J巧克力淋面创意生日蛋糕', '欧式奥利奥巧克力简约冰淇淋生日蛋糕',
    """
