#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/11/26 13:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('阿里云盘签到')

import requests
import time
import random

API_CONFIG = {
    "SIGN_IN_API": "https://member.aliyundrive.com/v1/activity/sign_in_list",
    "GET_REWARD_API": "https://member.aliyundrive.com/v1/activity/sign_in_reward?_rx-s=mobile",
    "ACCESS_TOKEN_API": "https://auth.aliyundrive.com/v2/account/token"
}

def get_access_token(refresh_token):
    """通过 refresh_token 获取 access_token"""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    try:
        r = requests.post(API_CONFIG["ACCESS_TOKEN_API"], json=data, timeout=15)
        r.raise_for_status()
        js = r.json()

        if "access_token" not in js:
            print("❌ refresh_token 失效")
            return None
        
        print(f"👤 用户：{js.get('nick_name')}({js.get('user_name')})")
        return js["access_token"]
    except Exception as e:
        print("获取 access_token 出错：", e)
        return None


def sign_in(refresh_token, access_token):
    """签到"""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    try:
        r = requests.post(API_CONFIG["SIGN_IN_API"], json=data, headers=headers, timeout=15)
        r.raise_for_status()
        js = r.json()

        if js.get("success"):
            print("✔ 签到成功")
        else:
            print("❌ 签到失败")

        cnt = js["result"]["signInCount"]
        print(f"累计签到：{cnt} 天")
        return cnt
    except Exception as e:
        print("签到接口错误：", e)
        return None


def main(refresh_token):
    access_token = get_access_token(refresh_token)
    if not access_token:
        return
    time.sleep(random.uniform(1.2, 2.0))
    sign_in(refresh_token, access_token)


if __name__ == "__main__":
    # 多账号可放在列表里
    refresh_token_list = [
        "你的refresh_token"
    ]
    
    for idx, token in enumerate(refresh_token_list, 1):
        print(f"\n===== 账号 {idx} =====")
        main(token)
        time.sleep(random.uniform(2.3, 2.8))
