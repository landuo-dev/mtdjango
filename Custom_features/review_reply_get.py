import requests
from datetime import datetime, timedelta

from Custom_features.review_reply_put import fs
from Custom_features.setting import while_fun


def set_query(ctime, page, wmpid):
    query_data = {
        'ignoreSetRouterProxy': 'true',
        'acctId': 97786666,
        'wmPoiId': wmpid,
        'token': '0c13IljXjtIyG77Alt_zxFG0H3u-IsZAQAO3bo2rrDlI*',
        'appType': 3,
        'commScore': 0,
        'commType': 0,
        'hasContent': -1,
        'periodType': 4,
        'beginTime': ctime,
        'endTime': ctime,
        'pageNum': page,
        'onlyAuditNotPass': 0,
        'pageSize': 10,
        'source': 1
    }
    return query_data


def review_rep(poi_id, cookie, content):
    now = datetime.now()
    yesterday = datetime(now.year, now.month, now.day, 0, 0, 0) - timedelta(days=1)
    url = "https://waimaieapp.meituan.com/gw/customer/comment/list"
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://e.waimai.meituan.com',
        "cookie": cookie,
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

    res = while_fun(requests.get, url=url, params=set_query(int(yesterday.timestamp()), 1, poi_id), headers=headers)
    total = res.json()['data']['total'] // 10

    k = 1
    for i in range(1, total + 2):
        print(i)
        # res = requests.get(url, params=set_query(int(yesterday.timestamp()), i, poi_id), headers=headers)
        res = while_fun(requests.get, url=url, params=set_query(int(yesterday.timestamp()), i, poi_id), headers=headers)
        # print(res.json())
        hp_list = res.json()['data']['list']
        for j in hp_list:
            cid = j['id']
            ctime = j['createTime']
            num = 0
            while 3 > num:
                try:
                    fs(cid, ctime, poi_id, cookie, content)
                    print(k)
                    k += 1
                    break
                except Exception as e:
                    print(e)
                    num += 1
        # print(i[''])
