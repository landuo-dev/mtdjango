import re
import json
from pymongo import MongoClient


def set_attribute(attrList01, attrList02, chenCheng=''):
    attributes = []
    if not len(attrList01):
        return '错误'
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


def set_aa(names, l, bb, sr1, arr):
    # arr = []
    # arr.append({"name": "份量", "name_id": 0, "value": val, "value_id": 0, "no": 0}):

    if len(names) <= l:
        arr01 = []
        key = ''
        for i in sr1:
            if i[1]:
                key += str(i[1]) + "·"
                value = str(i[1])
            else:
                key = '1个' + "·"
                value = '1个'
            if i[0] == '份量':
                arr01.append({"name": i[0], "name_id": 0, "value": value, "value_id": 0, "no": 0})
            else:
                arr01.append({"name": i[0], "name_id": 0, "value": i[1], "value_id": 0})
        else:
            key = key[:-1]

        # print(key, arr01)
        arr[key] = arr01
        return 0

    for i in bb[names[l]]:
        sr1.append((names[l], i))
        set_aa(names, l + 1, bb, sr1, arr)
        sr1.pop()


# def set_wmProductSkuVos(sk, dic1):
#     # print(dic1)
#     sr1 = []
#     arr = {}
#     set_aa(list(dic1.keys()), 0, dic1, sr1, arr)
#     # print(arr)
#     productsk = []
#     pattern = r'\([^()]*\)'
#     for i, val in enumerate(sk):
#         dic2 = {"unit": '1个', "box_price": str(int(val['boxPrice'])), "spec": val['spec'],
#                 "weight": "1",
#                 "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['boxNum'],
#                                             "ladder_price": str(int(val['boxPrice']))},
#                     "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
#                                    "auto_refresh": 1},
#                 }
#         if "·" in val['spec']:
#             key = re.sub(pattern, '', val['spec'])
#             dic2['attrList'] = arr[key]
#         else:
#             dic2['attrList'] = [
#                 {"name": "份量", "name_id": 0, "value": val['spec'].split('(')[0], "value_id": 0, "no": 0}]
#  加密
#         productsk.append(dic2)
#     return productsk


def set_wmProductSkuVos1(sk):
    productsk = []
    for i, val in enumerate(sk):
        dic2 = {"unit": val['unit'], "box_price": str(int(val['boxPrice'])), "spec": val['spec'],
                "weight": val['weight'],
                "wmProductLadderBoxPrice": {"status": 1, "ladder_num": val['ladder_num'],
                                            "ladder_price": str(int(val['ladder_price']))},
                "wmProductStock": {"id": "0", "stock": -1, "max_stock": -1,
                                   "auto_refresh": 1},
                "attrList": val['attrList']
                }

        productsk.append(dic2)
    return productsk


def set_post_data(poi_id, document, doc, name, chenCheng=''):
    description = document.get('description', '')
    min_order_count = document.get('min_order_count', 1)
    newSpuAttrs, dic1 = set_attribute(document['attrList01'], document['attrList02'], chenCheng)
    # print(dic1)
    # print(newSpuAttrs)
    # wmProductSkuVos = set_wmProductSkuVos(document['wmProductSkuVos'], dic1)
    wmProductSkuVos = set_wmProductSkuVos1(document['wmProductSkuVos'])
    # print(wmProductSkuVos)
    wmFoodVoJson = [{"description": description, "name": name, "wm_poi_id": poi_id, "tag_id": document['tagId'],
                     "tag_name": document['tagName'], "isShippingTimeSyncPoi": 2,
                     "shipping_time_x": document['shippingTimeX'],
                     "min_order_count": min_order_count,
                     "wmProductPics": [
                         {"aestheticsScore": "", "blur_result": 1, "blur_score": 0.999, "border_result": 1,
                          "border_score": 1, "ctime": 1719822810, "detailList": [{"extra": "", "picPropaganda": {
                             "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                             "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                             "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                             "setTypeName": True, "suggestion": "商品图片翻拍,建议重新上传图片",
                             "type": "recapture", "typeName": "翻拍"}, "result": 1, "score": 1, "setExtra": True,
                                                                                  "setPicPropaganda": True,
                                                                                  "setResult": True,
                                                                                  "setScore": True, "setType": True,
                                                                                  "setTypeName": True,
                                                                                  "type": "recapture",
                                                                                  "typeName": "图片翻拍"},
                                                                                 {"extra": "", "picPropaganda": {
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
                                                                                  "result": 1, "score": 0.999,
                                                                                  "setExtra": True,
                                                                                  "setPicPropaganda": True,
                                                                                  "setResult": True,
                                                                                  "setScore": True, "setType": True,
                                                                                  "setTypeName": True,
                                                                                  "type": "blur",
                                                                                  "typeName": "图片模糊"},
                                                                                 {"extra": "", "picPropaganda": {
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
                                                                                  "result": 1, "score": 1,
                                                                                  "setExtra": True,
                                                                                  "setPicPropaganda": True,
                                                                                  "setResult": True,
                                                                                  "setScore": True, "setType": True,
                                                                                  "setTypeName": True,
                                                                                  "type": "border",
                                                                                  "typeName": "图片有边框"}],
                          "detailListIterator": [{"extra": "", "picPropaganda": {
                              "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                              "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                              "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                              "setTypeName": True, "suggestion": "商品图片翻拍,建议重新上传图片",
                              "type": "recapture", "typeName": "翻拍"}, "result": 1, "score": 1, "setExtra": True,
                                                  "setPicPropaganda": True, "setResult": True, "setScore": True,
                                                  "setType": True, "setTypeName": True, "type": "recapture",
                                                  "typeName": "图片翻拍"}, {"extra": "", "picPropaganda": {
                              "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                              "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                              "setBadPicUrl": True, "setGoodPicUrl": True, "setSuggestion": True, "setType": True,
                              "setTypeName": True, "suggestion": "商品图片模糊，建议重新上传图", "type": "blur",
                              "typeName": "模糊"}, "result": 1, "score": 0.999, "setExtra": True,
                                                                            "setPicPropaganda": True,
                                                                            "setResult": True, "setScore": True,
                                                                            "setType": True, "setTypeName": True,
                                                                            "type": "blur", "typeName": "图片模糊"},
                                                 {"extra": "", "picPropaganda": {
                                                     "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                                                     "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                                                     "setBadPicUrl": True, "setGoodPicUrl": True,
                                                     "setSuggestion": True, "setType": True, "setTypeName": True,
                                                     "suggestion": "商品图片周围存在边框，建议重新上传图片",
                                                     "type": "border", "typeName": "图片周围有边框"}, "result": 1,
                                                  "score": 1, "setExtra": True, "setPicPropaganda": True,
                                                  "setResult": True, "setScore": True, "setType": True,
                                                  "setTypeName": True, "type": "border", "typeName": "图片有边框"}],
                          "detailListSize": 3, "id": 234937397591, "isMaster": 0, "is_quality_low": False,
                          "is_scored": 1, "picExtend": "",
                          "pic_large_url": document['defaultPicUrl'],

                          "pic_small_url": document['picUrl'], "quality_score": 1, "recapture_result": 1,
                          "recapture_score": 1,
                          "sequence": 0, "setAestheticsScore": True, "setBlur_result": True, "setBlur_score": True,
                          "setBorder_result": True, "setBorder_score": True, "setCtime": True,
                          "setDetailList": True, "setId": True, "setIsMaster": True, "setIs_quality_low": True,
                          "setIs_scored": True, "setPicExtend": True, "setPic_large_url": True,
                          "setPic_small_url": True, "setQuality_score": True, "setRecapture_result": True,
                          "setRecapture_score": True, "setSequence": True, "setSpOverrided": True,
                          "setSpecialEffectBigUrl": True, "setSpecialEffectEnable": True,
                          "setSpecialEffectUrl": True, "setUtime": True, "setValid": True,
                          "setWhite_rate_score": True, "setWmProductPicMaterialList": False,
                          "setWm_food_spu_id": True, "setWm_poi_id": True, "setWm_product_sku_id": True,
                          "spOverrided": False, "specialEffectBigUrl": "", "specialEffectEnable": 0,
                          "specialEffectUrl": "", "utime": 1719822810, "valid": 1, "white_rate_score": 1,
                          "wmProductPicMaterialList": None, "wmProductPicMaterialListIterator": None,
                          "wmProductPicMaterialListSize": 0, "wm_food_spu_id": 15630824174, "wm_poi_id": 19021228,
                          "wm_product_sku_id": 24282668273, "picPropagandaList": [{
                             "badPicUrl": "http://p0.meituan.net/wmproductdwm/72a1d552290012f83bd9eb47cc0acf5a448050.jpg",
                             "goodPicUrl": "http://p0.meituan.net/xianfu/bf616611fd610ab0d3100113140346de76679.jpg",
                             "setBadPicUrl": True,
                             "setGoodPicUrl": True,
                             "setSuggestion": True,
                             "setType": True,
                             "setTypeName": True,
                             "suggestion": "商品图片翻拍,建议重新上传图片",
                             "type": "recapture",
                             "typeName": "翻拍"}, {
                             "badPicUrl": "http://p1.meituan.net/wmproductdwm/3e71604928c625676f39e7857409925965729.jpg",
                             "goodPicUrl": "http://p0.meituan.net/xianfu/9df73a7781e51d848d4c04f40b97abf8333771.jpg",
                             "setBadPicUrl": True,
                             "setGoodPicUrl": True,
                             "setSuggestion": True,
                             "setType": True,
                             "setTypeName": True,
                             "suggestion": "商品图片模糊，建议重新上传图",
                             "type": "blur",
                             "typeName": "模糊"}, {
                             "badPicUrl": "http://p0.meituan.net/wmproduct/960ef4b268590602b6796fe58f1c3bfc202945.jpg",
                             "goodPicUrl": "http://p0.meituan.net/wmproduct/018ca93eb5e1cad8d759e1e1bf834ba557993.jpg",
                             "setBadPicUrl": True,
                             "setGoodPicUrl": True,
                             "setSuggestion": True,
                             "setType": True,
                             "setTypeName": True,
                             "suggestion": "商品图片周围存在边框，建议重新上传图片",
                             "type": "border",
                             "typeName": "图片周围有边框"}]}],
                     "specialEffectPic": None, "category_id": document['spTagId'],
                     "labelList": document['wmProductLabelVos'],
                     "newSpuAttrs":
                         newSpuAttrs,
                     "stockAndBoxPriceSkus": wmProductSkuVos,
                     "unifiedPackagingFee": 2,
                     "wmProductLadderBoxPrice": {"status": 1, "ladder_num": 1, "ladder_price": ""},
                     "wmProductStock": {"id": 0, "stock": 10000, "max_stock": 10000, "auto_refresh": 1},
                     "productCardDisplayContent": "", "wmProductVideo": None, "singleOrderNoDelivery": 0,
                     "onlySellInCombo": False, "id": doc['proid'],
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
                              "is_required": 2, "level": 3, "maxLength": -1, "multiSelect": 0,
                              "parent_tag_id": 1000000003,
                              "prompt_document": "", "sequence": 2, "wm_product_lib_tag_id": 99,
                              "wm_product_lib_tag_name": "甜",
                              "wm_product_property_template_id": 5510, "value_id": 101, "value": "甜味"},
                             {"customized": 0, "enumLimit": -1, "id": 161724, "inputTypeLimit": "", "input_type": 1,
                              "is_leaf": 2,
                              "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0, "parent_tag_id": 0,
                              "prompt_document": "",
                              "sequence": 6, "wm_product_lib_tag_id": 1000000003, "wm_product_lib_tag_name": "口味",
                              "wm_product_property_template_id": 5510, "value_id": 99, "value": "甜"}],
                             "1000000006": [
                                 {"customized": 0, "enumLimit": -1, "id": 161723, "inputTypeLimit": "",
                                  "input_type": 1,
                                  "is_leaf": 1,
                                  "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0,
                                  "parent_tag_id": 0,
                                  "prompt_document": "",
                                  "sequence": 5, "wm_product_lib_tag_id": 1000000006,
                                  "wm_product_lib_tag_name": "制作方法",
                                  "wm_product_property_template_id": 5510, "value_id": 256, "value": "烘焙"}],
                             "1000000015": [
                                 {"customized": 0, "enumLimit": 1, "id": 161719, "inputTypeLimit": "",
                                  "input_type": 7,
                                  "is_leaf": 1,
                                  "is_required": 1, "level": 2, "maxLength": -1, "multiSelect": 1,
                                  "parent_tag_id": 0,
                                  "prompt_document": "",
                                  "sequence": 1, "wm_product_lib_tag_id": 1000000015,
                                  "wm_product_lib_tag_name": "主料",
                                  "wm_product_property_template_id": 5510, "value": "蛋糕胚", "value_id": 112331}],
                             "1000000027": [
                                 {"customized": 0, "enumLimit": -1, "id": 161727, "inputTypeLimit": "",
                                  "input_type": 1,
                                  "is_leaf": 1,
                                  "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0,
                                  "parent_tag_id": 0,
                                  "prompt_document": "",
                                  "sequence": 9, "wm_product_lib_tag_id": 1000000027,
                                  "wm_product_lib_tag_name": "包装特色",
                                  "wm_product_property_template_id": 5510, "value_id": 110309,
                                  "value": "定制设计"}],
                             "1000000048": [
                                 {"customized": 0, "enumLimit": -1, "id": 161728, "inputTypeLimit": "",
                                  "input_type": 1,
                                  "is_leaf": 1,
                                  "is_required": 1, "level": 2, "maxLength": -1, "multiSelect": 0,
                                  "parent_tag_id": 0,
                                  "prompt_document": "",
                                  "sequence": 10, "wm_product_lib_tag_id": 1000000048,
                                  "wm_product_lib_tag_name": "是否自制",
                                  "wm_product_property_template_id": 5510, "value_id": 113857, "value": "自制"}],
                             "1200004473": [
                                 {"customized": 0, "enumLimit": -1, "id": 161726, "inputTypeLimit": "",
                                  "input_type": 1,
                                  "is_leaf": 1,
                                  "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0,
                                  "parent_tag_id": 0,
                                  "prompt_document": "",
                                  "sequence": 8, "wm_product_lib_tag_id": 1200004473,
                                  "wm_product_lib_tag_name": "制作时长~蛋糕",
                                  "wm_product_property_template_id": 5510, "value_id": 1300019364,
                                  "value": "0~半小时"}],
                             "1200189639": [
                                 {"customized": 0, "enumLimit": -1, "id": 161729, "inputTypeLimit": "",
                                  "input_type": 1,
                                  "is_leaf": 1,
                                  "is_required": 2, "level": 2, "maxLength": -1, "multiSelect": 0,
                                  "parent_tag_id": 0,
                                  "prompt_document": "",
                                  "sequence": 11, "wm_product_lib_tag_id": 1200189639,
                                  "wm_product_lib_tag_name": "蛋糕场景用途",
                                  "wm_product_property_template_id": 5510, "value_id": 1300019431,
                                  "value": "以上场景通用"}]},
                     "suggestTraceInfoList": [
                         {"setTraceId": True, "setTraceType": True, "traceId": "1430998252906039959",
                          "traceType": 100002}]
                     }]
    post_data = {
        'wmPoiId': poi_id,
        'entranceType': 2,
        'userType': 0,
        'wmFoodVoJson': json.dumps(wmFoodVoJson)
    }
    return post_data


if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db_pro = client['test']
    db_act = client['actproduct']
    poi_id = '11496467'
    # poi_id = '19021228'
    collect_pro = db_pro[poi_id]
    doc_x = collect_pro.find_one({'name': "动物奶油生日蛋糕"})
    post_data = set_post_data(poi_id, doc_x, doc_x, "动物奶油生日蛋糕", '')
