import requests
import os
import sys

# 环境变量设置
# export WP_APP_TOKEN_ONE='your_wxpusher_app_token'
# export WXPUSHER_UIDS='UID1,UID2,UID3'

def main():
    gold_price, silver_price = get_metals_prices()
    if gold_price and silver_price:
        message = f"实时黄金价格: {gold_price} CNY/克\n实时白银价格: {silver_price} CNY/克"
        print(message)
        send_notification(message)
    else:
        print("获取价格失败")

def get_metals_prices():
    """
    获取实时黄金和白银价格
    """
    url_gold = "https://hq.sinajs.cn/?list=hf_GC"  # 新浪财经黄金
    url_silver = "https://hq.sinajs.cn/?list=hf_SI"  # 新浪财经白银

    try:
        response_gold = requests.get(url_gold)
        response_silver = requests.get(url_silver)
        
        if response_gold.status_code == 200 and response_silver.status_code == 200:
            data_gold = response_gold.text.split(',')
            data_silver = response_silver.text.split(',')
            gold_price = data_gold[1]  # 获取黄金价格
            silver_price = data_silver[1]  # 获取白银价格
            return gold_price, silver_price
        else:
            print(f"请求失败，状态码: {response_gold.status_code}, {response_silver.status_code}")
            return None, None
    except Exception as e:
        print(f"请求异常: {e}")
        return None, None

def send_notification(message):
    """
    发送微信通知
    """
    try:
        app_token = os.getenv("WP_APP_TOKEN_ONE")
        uids = os.getenv("WXPUSHER_UIDS")

        if not app_token or not uids:
            print("未添加Wxpusher的APP_TOKEN或UIDS")
            return

        uid_list = uids.split(',')

        url = "https://wxpusher.zjiecode.com/api/send/message"
        data = {
            "appToken": app_token,
            "content": message,
            "contentType": 1,
            "uids": uid_list
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200 and response.json().get("code") == 1000:
            print("通知发送成功")
        else:
            print(f"通知发送失败，错误信息：{response.json()}")
    except Exception as e:
        print(f"通知发送异常: {e}")

if __name__ == '__main__':
    main()
