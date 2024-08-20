from pymongo import MongoClient

def push_json(poi_id, startTime, endTime):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['jt_log']
    wmpoi = db[poi_id]
    document = []
    query = {
        "$and": [
            {"stime": {"$gte": startTime}},  # 时间大于startTime
            {"stime": {"$lte": endTime}}  # 时间小于endTime
        ]
    }
    for i in wmpoi.find(query).sort("stime", 1):
        dic = {"ctime": i.get("ctime", 0), "stime": i.get("stime", 0), "推广进店量": i.get("clickCount", 0),
               "推广曝光量": i.get("showCount", 0), "推广花费": float(i.get("debit", 0)) / 100,
               "单次进店成本": round(float(i.get("avgPrice", 0)) / 100, 2),
               "进店率": float(i.get("clickRate", 0)), "点击成本": float(i.get("clickCost", 0)),
               "收入": float(i.get("revenue", 0)),
               "营业额": float(i.get("turnover", 0)), "支出": float(i.get('expenditure', 0)),
               "有效订单": int(i.get('validOrders', 0)),
               "实付单均价": round(float(i.get('AVGparce', 0)), 2), "曝光人数": float(i.get('numberOfImpressions', 0)),
               "入店转换率": float(i.get('InStoreConversionRate', 0)),
               "下单转换率": float(i.get('ConversionRateOfOrders', 0)),
               '刷单量': i.get('invalidOrders', 0)}

        if 'MerchantListings' in i:
            dic['商家列表'] = i['MerchantListings']
            dic['搜索'] = i['search']
        document.append(dic)

    # 按stime时间戳排序顺序排序
    dbuser = client['other']
    users = dbuser['jt_all']
    user = users.find_one({"ID号码": int(poi_id)})
    response = {"data": document, 'user': user, "poi_id": poi_id}
    return response
