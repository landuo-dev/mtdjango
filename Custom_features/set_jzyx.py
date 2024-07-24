import pandas as pd

from Custom_features.push_cup import push_cup


def main(df):
    result = set()
    type_list = {
        "粉丝顾客": 0,
        "昨日进店未下单顾客": 1,
        "写点评内容的顾客": 2,
        "不评价顾客": 3,
        "高价值顾客": 4,
        "潜力高价值顾客": 5,
        "需提升客单顾客": 6,
        "需促复购顾客": 7,
        "流失的高价值顾客": 8,
        "流失的需提升客单客户": 9,

    }
    # print(df)
    for i, data in df.iterrows():
        cookie = data.iloc[0]
        poi_id = data.iloc[1]
        try:
            print(data.iloc[2])
            type_select = type_list[data.iloc[2]]

        except KeyError as e:
            print('没有改优惠券选项')
            result.add('没有改优惠券选项')
            return result
        except Exception as e:
            print(e)
            return result
        limit = data.iloc[3]
        price = data.iloc[4]
        tim = data.iloc[5]
        valid_time = int(tim) * 24 * 60 * 60

        push_cup(poi_id, cookie, limit, price, type_select, valid_time)

    return result
