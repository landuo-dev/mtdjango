
from pymongo import MongoClient
from Custom_features.review_reply_get import review_rep


# client = MongoClient('mongodb://localhost:37017/')
def auto_rep(poi_id, cookie):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['reply']
    collect = db['all']
    for i in collect.find({'wmpoid': poi_id}):
        review_rep(i['wmpoid'], cookie, i['content'])


