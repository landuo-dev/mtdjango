import requests

from Custom_features.setting import while_fun


def push_cup(poi_id, cookie):
    url = "https://waimaieapp.meituan.com/bizdata/marketing/targetCoupon/sendTargetCoupon"

    query_data = {
        'yodaReady': 'h5',
        'csecplatform': 4,
        'csecversion': '2.4.0',
    }

    post_data = {
        'token': '0c13IljXjtIyG77Alt_zxFG0H3u-IsZAQAO3bo2rrDlI*',
        'wmPoiId': '19021228',
        'acctId': '97786666',
        'appType': '3',
        'label_id': '10321660',
        'labelType': '18',
        'coupon_name': 'SweetyMove思茉儿·蛋糕定制（玄武店）',
        'come_from': '0',
        'user_list': '0',
        'detail': {"beginDate": "", "endHour": "", "poly_latitude": "", "endDate": "", "beginHour": "", "minPrice": "",
                   "maxPrice": "", "poly_longitude": "", "compareResult": "", "itemType": "", "dateType": "",
                   "weekDayType": "", "hotLatLongInfos": "", "potentialLatLongInfos": ""},
        'comment': None,
        'coupon_type': 1,
        'saveTemplates': False,
        'valid_time': 604800,
        'send_time': 0,
        'price': 1,
        'limit_price': 99,
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
    print(res)