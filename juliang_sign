import requests
import os

# 读取环境变量
def get_env_vars():
    if "juliang_account" in os.environ:
        accounts = os.environ["juliang_account"].split('#')
        return accounts
    else:
        print("未添加 juliang_account 变量")
        exit(1)

def send_notice(content):
    token = os.getenv("TOKEN")
    if not token:
        print("未设置 TOKEN 环境变量，无法发送通知")
        return
    
    title = "巨量IP 签到"
    url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template=html"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("通知发送成功")
    except requests.RequestException as e:
        print(f"通知发送失败: {e}")

def sign_in(email, password):
    session = requests.Session()
    login_url = "https://www.juliangip.com/user/login"
    checkin_url = "https://www.juliangip.com/user/checkin"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    login_data = {
        "username": email,
        "password": password
    }
    
    try:
        # 登录
        login_response = session.post(login_url, headers=headers, data=login_data)
        login_response.raise_for_status()
        
        # 签到
        checkin_response = session.post(checkin_url, headers=headers)
        checkin_response.raise_for_status()
        
        result = checkin_response.json()
        return result.get("msg", "签到失败，未获取到消息")
    
    except requests.RequestException as e:
        print(f"请求失败: {e}")
        return "签到失败，请检查账号配置。"

def main():
    accounts = get_env_vars()
    all_messages = []
    
    for account in accounts:
        email, password = account.split('&')
        message = sign_in(email, password)
        all_messages.append(message)
    
    notice_content = "<br>".join(all_messages)
    send_notice(notice_content)

if __name__ == '__main__':
    main()
