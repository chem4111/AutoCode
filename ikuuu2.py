import requests
import os
import sys  # 添加sys库用于退出程序

# export ikuuu='邮箱1&密码1&UID1&备注1#邮箱2&密码2&UID2&备注2#邮箱3&密码3&UID3&备注3'
# WP_APP_TOKEN_ONE: Wxpusher 的 APP_TOKEN

def main():
    accounts = get_accounts()  # 获取所有账号信息
    print(f"共找到{len(accounts)}个账号")

    for account in accounts:
        email, passwd, uid, remark = account.split('&')  # 分割出邮箱、密码、UID和备注
        message = sign_in(email, passwd)  # 登录并签到
        print(f"{remark}的账号：{message}")  # 打印签到结果
        send_notification(remark, message, uid)  # 发送通知

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

def send_notification(remark, message, uid):
    """
    发送微信通知
    """
    try:
        app_token = os.getenv("WP_APP_TOKEN_ONE")

        if not app_token:
            print("未添加Wxpusher的APP_TOKEN")
            return

        url = "https://wxpusher.zjiecode.com/api/send/message"
        data = {
            "appToken": app_token,
            "content": f"{remark}的账号签到结果：{message}",
            "contentType": 1,
            "uids": [uid]  # 使用单个UID
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200 and response.json().get("code") == 1000:
            print(f"{remark}的账号通知发送成功")
        else:
            print(f"{remark}的账号通知发送失败，错误信息：{response.json()}")
    except Exception as e:
        print(f"{remark}的账号通知发送异常: {e}")

if __name__ == '__main__':
    main()
