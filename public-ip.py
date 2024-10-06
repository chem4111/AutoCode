import requests
import os

# 定义存储 IP 地址的文件路径
IP_FILE_PATH = 'public_ip.txt'

# 直接设置 wxpush API 地址和 UID，PUSH_TOKEN 仍然从环境变量中获取
WXPUSH_URL = "https://wxpusher.zjiecode.com/api/send/message"  # 固定 wxpush API 地址
PUSH_TOKEN = os.getenv("WP_APP_TOKEN_ONE")  # 从环境变量中获取 wxpush token
UID = "YOUR_UID_HERE"  # 替换成实际的 UID

def get_public_ip():
    """
    获取当前公网IP
    """
    try:
        # 使用 checkip.amazonaws.com 服务来获取公网 IP
        response = requests.get('https://checkip.amazonaws.com/')
        response.raise_for_status()  # 检查请求是否成功
        public_ip = response.text.strip()  # 去除多余的换行符
        return public_ip
    except requests.RequestException as e:
        print(f"获取公网IP失败: {e}")
        return None

def read_stored_ip():
    """
    读取已存储的 IP 地址
    """
    if os.path.exists(IP_FILE_PATH):
        try:
            with open(IP_FILE_PATH, 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"读取旧公网IP失败: {e}")
    return None

def store_ip(ip):
    """
    将 IP 存入文件
    """
    try:
        with open(IP_FILE_PATH, 'w') as file:
            file.write(ip)
    except Exception as e:
        print(f"存储公网IP失败: {e}")

def notify_ip_change(old_ip, new_ip):
    """
    发送IP变化通知
    """
    if not PUSH_TOKEN:
        print("未添加 Wxpusher 的 APP_TOKEN")
        return

    if not UID:
        print("未设置推送 UID")
        return

    try:
        # 构造发送通知的 payload 数据
        data = {
            "appToken": PUSH_TOKEN,
            "content": f"IP has changed from {old_ip} to {new_ip}!",
            "contentType": 1,  # 文本类型
            "uids": [UID]  # 使用单个UID进行推送
        }

        headers = {
            'Content-Type': 'application/json'
        }

        # 发送 POST 请求
        response = requests.post(WXPUSH_URL, json=data, headers=headers)
        
        # 判断请求结果
        if response.status_code == 200 and response.json().get("code") == 1000:
            print(f"IP 变化通知发送成功")
        else:
            print(f"IP 变化通知发送失败，错误信息：{response.json()}")
    except Exception as e:
        print(f"IP 变化通知发送异常: {e}")

def check_ip_change():
    """
    检查IP是否变化，若变化则发送通知
    """
    current_ip = get_public_ip()
    if not current_ip:
        print("无法获取当前 IP")
        return  # 无法获取当前 IP，终止操作

    stored_ip = read_stored_ip()

    if stored_ip:
        if stored_ip != current_ip:
            print(f"IP 变化，旧 IP: {stored_ip}, 新 IP: {current_ip}")
            notify_ip_change(stored_ip, current_ip)
            store_ip(current_ip)  # 更新存储的 IP
        else:
            print("IP 没有变化。")
    else:
        # 如果没有存储的 IP，则存储当前 IP
        print("没有存储的 IP，保存当前 IP。")
        store_ip(current_ip)

if __name__ == "__main__":
    check_ip_change()
