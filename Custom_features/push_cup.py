import requests
import re
from Custom_features.setting import while_fun


def labelid(poi_id, cookie, type_select):
    cookie = re.sub(' ', '', cookie)
    token = re.findall(".*;token=(.*?);", cookie)[0]
    query_data = {
        'token': token,
        'wmPoiId': poi_id,
        'acctId': 97786666,
        'appType': 3,
        'yodaReady': 'h5',
        'csecplatform': 4,
        'csecversion': '2.4.0',

    }
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
    if type_select >= 4:
        type_select -= 4
        url = "https://waimaieapp.meituan.com/bizdata/marketing/targetCoupon/getSystemLabel"
    else:
        url = 'https://waimaieapp.meituan.com/bizdata/marketing/targetCoupon/getSceneLabel'

    res = while_fun(requests.get, url, headers=headers, params=query_data)
    # resp = requests.get()
    # print(res.json())
    if res and res.status_code == 200:
        json_data = res.json()
        return json_data['data']['labelList'][type_select]


def push_cup(poi_id, cookie, limit_price, price, type_select, ctime):
    label1 = labelid(poi_id, cookie, type_select)
    label_id = label1['id']
    labeltype = label1['labelType']
    print(label_id, labeltype)
    url = "https://waimaieapp.meituan.com/bizdata/marketing/targetCoupon/sendTargetCoupon"

    query_data = {
        'yodaReady': 'h5',
        'csecplatform': 4,
        'csecversion': '2.4.0',
    }
    cookie = re.sub(' ', '', cookie)
    token = re.findall(".*;token=(.*?);", cookie)[0]
    post_data = {
        'token': token,
        'wmPoiId': poi_id,
        'acctId': '97786666',
        'appType': '3',
        'label_id': label_id,
        'labelType': labeltype,
        # 'coupon_name': 'Toni私人订制网红生日蛋糕（沈阳店）',
        'come_from': '0',
        'user_list': '0',
        'detail': {"beginDate": "", "endHour": "", "poly_latitude": "", "endDate": "", "beginHour": "", "minPrice": "",
                   "maxPrice": "", "poly_longitude": "", "compareResult": "", "itemType": "", "dateType": "",
                   "weekDayType": "", "hotLatLongInfos": "", "potentialLatLongInfos": ""},
        'comment': None,
        'coupon_type': 1,
        'saveTemplates': False,
        'valid_time': ctime,
        'send_time': 0,
        'price': price,
        'limit_price': limit_price,
        'request_code': None,
        'response_code': None,
    }

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

    res = while_fun(requests.post, url=url, headers=headers, params=query_data, data=post_data)
    print(res.text)


# if __name__ == '__main__':
#     cookie = "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; acctId=97786666; token=0c13IljXjtIyG77Alt_zxFG0H3u-IsZAQAO3bo2rrDlI*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=007ikcHy1UM5U02NYMNvDJmHO2RL6y6yC3JC2GD9ESMmjsNDchQuzEAkKsXJ8rwB6zVbIxCl3udgBInMPCP-NA; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; isOfflineSelfOpen=0; logistics_support=; wm_order_channel=appshare1; utm_source=5913; au_trace_key_net=default; openh5_uuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; isIframe=false; setPrivacyTime=3_20240524; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; _gid=GA1.3.81391873.1716602003; channelType={%22appshare1%22:%220%22}; _ga_NMY341SNCF=GS1.3.1716602003.3.1.1716603712.0.0.0; channelConfig={%22channel%22:%22default%22%2C%22type%22:0%2C%22fixedReservation%22:{%22reservationTimeStatus%22:0%2C%22startReservationTime%22:0%2C%22endReservationTime%22:0}}; _lx_utm=utm_source%3D5913; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; JSESSIONID=hoi1p00fpi06j2vo79t0mezi; logan_session_token=pjetq3w2xw86zhtn2y7r; _lxsdk_s=18fa73ba53c-723-2d6-9d3%7C97786666%7C10452"
#
#     push_cup('19021228', cookie, 98, 10, 9, 7)
