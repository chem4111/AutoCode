import requests
import os
import sys
import json
from urllib3.exceptions import InsecureRequestWarning

# 禁用 InsecureRequestWarning 警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 常量配置
LOGIN_URL = "https://ikuuu.one/auth/login"
CHECKIN_URL = "https://ikuuu.one/user/checkin"
WXPUSHER_URL = "https://wxpusher.zjiecode.com/api/send/message"
DEFAULT_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def main():
    accounts = get_accounts()
    print(f"共找到 {len(accounts)} 个账号")

    for account in accounts:
        try:
            email, passwd, uid, remark = account.split('&')
        except ValueError:
            print(f"账号格式错误: {account}")
            continue

        message = sign_in(email, passwd)
        print(f"{remark} 的账号：{message}")
        send_notification(remark, message, uid)

def get_accounts():
    ikuuu = os.getenv("ikuuu")
    if not ikuuu:
        print("未找到环境变量 'ikuuu'")
        sys.exit(1)
    return ikuuu.split('#')

def sign_in(email, passwd):
    try:
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)
        
        # 登录
        login_data = {"email": email, "passwd": passwd}
        login_response = session.post(LOGIN_URL, data=login_data, verify=False)
        
        if login_response.status_code != 200:
            return f"登录失败: 状态码 {login_response.status_code}"

        # 检查登录是否成功（根据实际接口调整）
        login_json = login_response.json()
        if login_json.get("ret") != 1:
            return f"登录失败: {login_json.get('msg', '未知错误')}"

        # 签到
        checkin_response = session.post(CHECKIN_URL, verify=False)
        checkin_json = checkin_response.json()
        return checkin_json.get('msg', '签到失败（无返回消息）')

    except requests.exceptions.RequestException as e:
        return f"网络请求异常: {e}"
    except json.JSONDecodeError:
        return "响应解析失败"

def send_notification(remark, message, uid):
    app_token = os.getenv("WP_APP_TOKEN_ONE")
    if not app_token:
        print("未找到环境变量 'WP_APP_TOKEN_ONE'")
        return

    payload = {
        "appToken": app_token,
        "content": f"{remark} 签到结果：{message}",
        "contentType": 1,
        "uids": [uid]
    }

    try:
        response = requests.post(WXPUSHER_URL, json=payload, timeout=10)
        result = response.json()
        if response.status_code == 200 and result.get("code") == 1000:
            print(f"{remark} 通知发送成功")
        else:
            print(f"{remark} 通知发送失败，错误码：{result.get('code')}")
    except Exception as e:
        print(f"{remark} 通知发送异常: {e}")

if __name__ == '__main__':
    main()
