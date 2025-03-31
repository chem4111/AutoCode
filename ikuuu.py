#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/3/27 13:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('ikuuu签到')

import requests
import os
import sys  # 添加sys库用于退出程序

# export ikuuu='邮箱1&密码1&备注1#邮箱2&密码2&备注2#邮箱3&密码3&备注3'

#你需要在环境变量中设置 PUSH_PLUS_TOKEN 和 PUSH_PLUS_USER。
#PUSH_PLUS_TOKEN：你的 Push Plus 个人令牌，用于一对一推送。
#PUSH_PLUS_USER：你的 Push Plus 群组编码，如果没有则可以留空。

def main():
    accounts = get_accounts()  # 获取所有账号信息
    print(f"共找到{len(accounts)}个账号")

    for account in accounts:
        email, passwd, remark = account.split('&')  # 分割出邮箱、密码和备注
        message = sign_in(email, passwd)  # 登录并签到
        print(f"{remark}的账号：{message}")  # 打印签到结果
        send_notification(remark, message)  # 发送通知

def get_accounts():
    """
    从环境变量中获取账号信息
    """
    ikuuu = os.getenv("ikuuu")
    if ikuuu:
        return ikuuu.split('#')  # 使用#分隔多个账号信息
    else:
        print("未添加ikuuu变量")
        sys.exit(1)  # 若未找到环境变量，则退出程序

def sign_in(email, passwd):
    """
    登录并签到
    """
    try:
        body = {"email": email, "passwd": passwd}
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        }
        session = requests.session()
        # 发送登录请求
        session.post('https://ikuuu.one/auth/login', headers=headers, data=body)
        # 发送签到请求
        response = session.post('https://ikuuu.one/user/checkin').json()
        return response.get('msg', '签到失败')  # 返回签到结果
    except Exception as e:
        return f'请检查账号配置是否错误: {e}'  # 捕获异常并返回错误信息

def send_notification(remark, message):
    """
    发送通知
    """
    try:
        push_plus_token = os.getenv("PUSH_PLUS_TOKEN")
        push_plus_user = os.getenv("PUSH_PLUS_USER")
        if not push_plus_token:
            print("未添加Push Plus的TOKEN")
            return
        
        url = "http://www.pushplus.plus/send"
        data = {
            "token": push_plus_token,
            "title": f"{remark}的账号签到结果",
            "content": message,
            "topic": push_plus_user if push_plus_user else ""
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"{remark}的账号通知发送成功")
        else:
            print(f"{remark}的账号通知发送失败，状态码：{response.status_code}")
    except Exception as e:
        print(f"{remark}的账号通知发送异常: {e}")

if __name__ == '__main__':
    main()
