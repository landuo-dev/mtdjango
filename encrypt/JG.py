# utf - 8

import requests

from pymongo import MongoClient


class JG():
    def __init__(self, poi_id, cookie):
        self.poi_id = str(poi_id)
        self.cookie = cookie
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': cookie,
            'Origin': 'https://e.waimai.meituan.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
            # ... 其他 headers 字段
        }
        self.client = MongoClient('mongodb://localhost:27017/')
        # 选择数据库和集合（相当于 SQL 中的表）
        self.db = self.client['test']
        # collection = db[str(poi_id)]
        self.collection = self.db[self.poi_id]
        self.session = requests.session()
        self.session.headers = self.headers







