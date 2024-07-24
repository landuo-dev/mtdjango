import requests


def get_product(session):
    num = 0
    while 3 > num:
        try:
            response = session.get(
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
        "mapSpuExtendList": json_data['wmProductSpu']['mapSpuExtendList'],
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


if __name__ == '__main__':
    cookie = "WEBDFPID=1719905543652IQCQSKWfd79fef3d01d5e9aadc18ccd4d0c95072521-1719905543652-1719905543652IQCQSKWfd79fef3d01d5e9aadc18ccd4d0c95072521; _lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; _lxsdk=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!12fd30cd-bbd3-45d4-973d-ca03b91e7466; uuid_update=true; acctId=97786666; token=09AYv1uic3k41UssyQIjORAP2oPosNjCoTyahwwJsbE4*; brandId=-1; isOfflineSelfOpen=0; city_id=0; isChain=1; existBrandPoi=true; ignore_set_router_proxy=true; region_id=; region_version=0; newCategory=false; bsid=efOollWSo0PyKfc0DhTcmtRYoZhIRPGqB3OXO8Vd6M9tE1Rgp8tjURDYG60N-ANeBsCN-1cKcLbTtPI9I4XXFQ; city_location_id=0; location_id=0; cityId=440300; provinceId=440000; pushToken=09AYv1uic3k41UssyQIjORAP2oPosNjCoTyahwwJsbE4*; setPrivacyTime=1_20240702; logistics_support=; JSESSIONID=hqzcyskhiz7p7xjy5482vruw; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=b1dejb1wud8cylfm3045; _lxsdk_s=190725be632-6da-b17-335%7C%7C515"

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Pragma': 'no-cache',
        'Referer': 'https://e.waimai.meituan.com/gw/static_resource/product',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'spuId': '15630824174',
        'wmPoiId': "19021228",
        'clientId': '2',
        'v2': '1',
    }

    session = requests.session()
    session.headers = headers
    session.params = params
    proid = '15512472320'
    poid = '19021228'
    res = get_product(session)
    print(res)

