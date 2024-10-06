import requests
import os

# 定义存储 IP 地址的文件路径
IP_FILE_PATH = 'public_ip.txt'

# 使用环境变量获取 wxpush token 或者其他相关推送接口地址
WXPUSH_URL = os.getenv("WXPUSH_URL")  # 替换成实际的 wxpush API 地址
PUSH_TOKEN = os.getenv("PUSH_TOKEN")  # 替换成你的 wxpush token

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
        print(f"Failed to get public IP: {e}")
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
            print(f"Failed to read stored IP: {e}")
    return None

def store_ip(ip):
    """
    将 IP 存入文件
    """
    try:
        with open(IP_FILE_PATH, 'w') as file:
            file.write(ip)
    except Exception as e:
        print(f"Failed to store IP: {e}")

def notify_ip_change(old_ip, new_ip):
    """
    发送IP变化通知
    """
    message = f"IP has changed from {old_ip} to {new_ip}!"
    print(message)  # 打印信息（可选）
    
    payload = {
        "token": PUSH_TOKEN,
        "content": message,
        "topicIds": [],
        "uids": [],
        "url": ""  # 可以设置一个点击通知后跳转的链接
    }

    try:
        response = requests.post(WXPUSH_URL, json=payload)
        response.raise_for_status()  # 检查请求是否成功
        if response.json().get("code") == 1000:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification: {response.json()}")
    except requests.RequestException as e:
        print(f"Error sending notification: {e}")

def check_ip_change():
    """
    检查IP是否变化，若变化则发送通知
    """
    current_ip = get_public_ip()
    if not current_ip:
        return  # 无法获取当前 IP，终止操作

    stored_ip = read_stored_ip()

    if stored_ip:
        if stored_ip != current_ip:
            notify_ip_change(stored_ip, current_ip)
            store_ip(current_ip)  # 更新存储的 IP
        else:
            print("IP has not changed.")
    else:
        # 如果没有存储的 IP，则存储当前 IP
        print("No IP stored. Saving the current IP.")
        store_ip(current_ip)

if __name__ == "__main__":
    check_ip_change()
