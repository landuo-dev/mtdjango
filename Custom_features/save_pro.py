from pymongo import MongoClient
import json
import re
import time
import requests
import traceback

from Custom_features.set_yuan_bb import set_post_data

# from Custom_features import

def save(collect_pro, document, doc, poi_id, name, cookie, reult):
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
    flog = 0
    num = 0
    try:
        # break
        # print(attrList)
        # print(len(attributes))
        # break
        # 三个全黑

        post_data = set_post_data(poi_id, document, doc, name, '')

        while 3 > num:
            try:
                response = requests.post(url, headers=headers, data=post_data, timeout=5)
                json_data = response.json()
                print(json_data)
                if json_data['msg'] != 'success':
                    if '商品价格涨幅不可超过40%' in json_data['msg']:
                        print(json_data['msg'], document['name'])
                        post_data = set_post_data(poi_id, document, doc, name, '.')
                        num += 1
                        flog = 1
                        continue
                    post_data = set_post_data(poi_id, document, doc, name, '.')
                    reult.add(str(json_data['msg']) + " " + document['name'] + '\n')
                    num += 1
                    flog = 1
                    continue

                break
            except requests.exceptions.ReadTimeout:
                print("请求超时，请手动修改", name)
                num += 1
                time.sleep(1)
            except Exception as e:
                print(e)
                num += 1
    except Exception as e:
        print(e)
        print(name)
        traceback.print_exc()
        reult.add(str(e) + " " + name + '\n')
        # print(response.status_code, i)
        # print(response.json())

    if flog:
        post_data = set_post_data(poi_id, document, doc, name, '')
        response = requests.post(url, headers=headers, data=post_data, timeout=5)
        json_data = response.json()
        print(json_data, "还原")

    if num >= 3:
        return 1

    return 0


if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db_pro = client['test']
    poi_id = '19021228'
    collect_pro = db_pro[poi_id]
    doc_x = collect_pro.find_one({'name': "【护士节限定】zui美天使双层鲜花爱心生日蛋糕🎉"})
    doc_y = collect_pro.find_one({'name': "【护士节限定】zui美天使双层鲜花爱心生日蛋糕🎉"})
    cookie = "_lxsdk_cuid=18f141d9eb9c8-0033f3d2dbef57-26001d51-1fa400-18f141d9eb9c8; device_uuid=!24ae408e-dd29-4dd9-b274-43b9e9fe5091; uuid_update=true; pushToken=0I8JEqPcZddF4VYTy5hpYUJJRosvU8v-pSKS7LSoDJsY*; WEBDFPID=vzz7x78zu94w56v90z443u5zwu3704y881u809z0wxu97958z146219x-2029472078615-1714112078615UCKQYCCfd79fef3d01d5e9aadc18ccd4d0c95073581; iuuid=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _lxsdk=7ACAF630E8FA1E1C9247877A8297E026FCE715188DBAAD0E9A0B80DC655841F1; _ga=GA1.3.306699777.1714902768; acctId=97786666; token=0c13IljXjtIyG77Alt_zxFG0H3u-IsZAQAO3bo2rrDlI*; city_id=0; isChain=1; ignore_set_router_proxy=true; region_id=; region_version=0; bsid=007ikcHy1UM5U02NYMNvDJmHO2RL6y6yC3JC2GD9ESMmjsNDchQuzEAkKsXJ8rwB6zVbIxCl3udgBInMPCP-NA; city_location_id=0; location_id=0; has_not_waimai_poi=0; cityId=440300; provinceId=440000; wm_order_channel=appshare1; utm_source=5913; _ga_NMY341SNCF=GS1.3.1716602003.3.1.1716603712.0.0.0; _lx_utm=utm_source%3D5913; isOfflineSelfOpen=0; logistics_support=; JSESSIONID=1ebat5t2uot521s4bpi8z8e47a; wmPoiId=19021228; wmPoiName=SweetyMove%E6%80%9D%E8%8C%89%E5%84%BF%C2%B7%E8%9B%8B%E7%B3%95%E5%AE%9A%E5%88%B6%EF%BC%88%E7%8E%84%E6%AD%A6%E5%BA%97%EF%BC%89; wpush_server_url=wss://wpush.meituan.com; shopCategory=food; set_info=%7B%22wmPoiId%22%3A19021228%2C%22ignoreSetRouterProxy%22%3Atrue%7D; logan_session_token=zj1i04fymmkls863bum7; _lxsdk_s=18fc0fcf0b3-3ad-7e8-ae5%7C97786666%7C5724"

    """
    '简约威士J巧克力淋面创意生日蛋糕', '欧式奥利奥巧克力简约冰淇淋生日蛋糕',
    """
    save(collect_pro, doc_x, doc_x, poi_id, "【护士节限定】zui美天使双层鲜花爱心生日蛋糕🎉", " ", cookie, set())
    # saveAct(collect_pro, doc_y, doc_x, poi_id, cookie)
