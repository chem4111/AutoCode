#!/usr/bin/python3
# -- coding: utf-8 -- 
# const $ = new Env('恩山签到')
# cron "30 4 * * *" script-path=xxx.py,tag=匹配cron用
# enshanck 环境变量放所有的cookie
import requests
import re
import os
import notify

def get_enshan_credit():
    """
    获取恩山的恩山币和积分信息
    """
    # 从环境变量中获取恩山的cookie
    enshanck = os.getenv("enshanck")
    if not enshanck:
        print("未获取到恩山的cookie，请检查环境变量配置。")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
        "Cookie": enshanck
    }
    session = requests.session()
    try:
        # 发送请求获取页面内容
        response = session.get('https://www.right.com.cn/FORUM/home.php?mod=spacecp&ac=credit&showcredit=1', headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 解析恩山币和积分信息
        coin_match = re.search("恩山币: </em>(.*?)nb &nbsp;", response.text)
        point_match = re.search("<em>积分: </em>(.*?)<span", response.text)
        if coin_match and point_match:
            coin = coin_match.group(1)
            point = point_match.group(1)
            return f"恩山币：{coin}\n积分：{point}"
        else:
            print("未找到恩山币或积分信息，请检查页面结构是否有变化。")
            return None
    except requests.RequestException as e:
        print(f"网络请求出错: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    return None

if __name__ == "__main__":
    result = get_enshan_credit()
    if result:
        print(result)
        try:
            notify.send("恩山签到", result)
        except Exception as e:
            print(f"通知发送失败: {e}")
    
