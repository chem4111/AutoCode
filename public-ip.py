import requests
import os

# 定义存储 IP 地址的文件路径
IP_FILE_PATH = 'public_ip.txt'

# wxpush token 或者其他相关推送接口地址
WXPUSH_URL = "https://wxpusher.your_api_url"  # 替换成实际的 wxpush API 地址
PUSH_TOKEN = "your_push_token"  # 替换成你的 wxpush token

def get_public_ip():
    try:
        # 获取公网 IP
        response = requests.get('https://checkip.amazonaws.com')
        data = response.json()
        return data['ip']
    except Exception as e:
        print(f"Failed to get public IP: {e}")
        return None

def read_stored_ip():
    # 如果存储 IP 文件存在，读取它
    if os.path.exists(IP_FILE_PATH):
        with open(IP_FILE_PATH, 'r') as file:
            return file.read().strip()
    return None

def store_ip(ip):
    # 将 IP 存入文件
    with open(IP_FILE_PATH, 'w') as file:
        file.write(ip)

def notify_ip_change(old_ip, new_ip):
    # 构造通知内容
    message = f"IP has changed from {old_ip} to {new_ip}!"
    
    # 打印信息（可选）
    print(message)
    
    # 调用 wxpush API 发送通知
    payload = {
        "token": PUSH_TOKEN,
        "content": message,
        "topicIds": [],
        "uids": [],
        "url": ""  # 可以设置一个点击通知后跳转的链接
    }
    
    try:
        response = requests.post(WXPUSH_URL, json=payload)
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Failed to send notification. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending notification: {e}")

if __name__ == "__main__":
    # 获取当前公网 IP
    current_ip = get_public_ip()
    if current_ip:
        # 读取存储的 IP
        stored_ip = read_stored_ip()

        # 比较 IP 是否发生变化
        if stored_ip:
            if stored_ip != current_ip:
                notify_ip_change(stored_ip, current_ip)
                # 更新存储的 IP
                store_ip(current_ip)
            else:
                print("IP has not changed.")
        else:
            # 如果没有存储的 IP，则存储当前 IP
            print("No IP stored. Saving the current IP.")
            store_ip(current_ip)
