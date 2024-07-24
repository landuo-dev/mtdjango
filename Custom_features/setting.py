from requests.exceptions import InvalidHeader
import re
import time


def while_fun(func, *args, **kwargs):
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


def set_attribute(str1, attrs):
    attributes = []
    updatabase = []
    if len(attrs):
        for index, i in enumerate(attrs):
            attributes.append(
                {"name": i['name'], "name_id": i['name_id'], "price": i['price'], "value": i['value'],
                 "value_id": i['value_id'], "no": 0,
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
    # print(attributes)
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
                # print(name, price)
            else:
                name = nameval[0]
                price = 0
            # print(name, price)
            attributes.append(
                {"name": arr[0], "name_id": 0, "value": name, "value_id": 0, "price": price, "no": num + 1,
                 "mode": 1, "value_sequence": j, "weight": 0, "weightUnit": None, "sell_status": 0
                 })
            updatabase.append(
                {
                    "name": arr[0],
                    "price": 0,
                    'value': arr[j + 1]
                }
            )

    return attributes, updatabase


def set_wmProductSkuVos(sk):
    flog = 0
    productsk = []
    for i, val in enumerate(sk):
        if val['boxPrice'] >= 2:
            flog = 1
            price = str(int(val['boxPrice']))
        else:
            price = str(min(int(val['boxPrice']), 5))
            # price = "0"
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
    return productsk, flog


def set_bb(poi_id, document, description, name, product_info, proid=None):
    if not proid:
        proid = document['proid']
        attributes, updatadatabase = set_attribute(product_info, document['attrList01'])
    else:
        attributes, updatadatabase = set_attribute(product_info, document['attrList01'])

    productskuvos, flog = set_wmProductSkuVos(document['wmProductSkuVos'])
    result = ''
    min_order_count = document.get('min_order_count', 1)

    if flog:
        result = name
    bb = {"description": description, "name": name, "wm_poi_id": poi_id,
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

    return bb, updatadatabase
