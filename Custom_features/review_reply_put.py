"""acctId: 97786666
wmPoiId: 21272738
token: 0c13IljXjtIyG77Alt_zxFG0H3u-IsZAQAO3bo2rrDlI*
appType: 3
toCommentId: 7557556966
comment: 蛋糕是生活中的仪式感，是岁月里的调味剂，感谢亲亲光临❥(
1.健康理念：
下单现做，当天现烤戚风蛋糕胚，保持松软的口感同时弹力十足持久不塌，采用新鲜水果🥭，丝滑牛奶奶油以及进口安佳动物奶油制作（不含反式脂肪）
2.专业理念：
每一位师傅都有8年以上裱花经验，尽最大的努力赋予它最真实且无添加的美
3.配送理念：
平台下单专人一对一配送，如遇问题第一时间为您排忧解难
小店集体员工祝您生日快乐，愿你无疾无忧、百岁安生、不离笑🎉
userCommentCtime: 2024-05-17
"""
import re

import requests


def set_postdata(cid, ctime, poi_id, content, token):
    post_data = {
        'acctId': 97786666,
        'wmPoiId': poi_id,
        'token': token,
        'appType': 3,
        'toCommentId': cid,
        'comment': content,
        'userCommentCtime': ctime
    }
    return post_data


def fs(cid, ctime, poi_id, cookie, content):
    url = "https://waimaieapp.meituan.com/gw/customer/comment/reply?ignoreSetRouterProxy=true"

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
    sr1 = re.sub(' ', '', cookie)
    token = re.findall(".*;token=(.*?);", sr1)[0]
    post_data = set_postdata(cid, ctime, poi_id, content, token)
    res = requests.post(url, post_data, headers=headers)
    print(res.json())

# if __name__ == '__main__':
# fs(7523108909, "2024-05-05", wmpoi_id, cookie)
