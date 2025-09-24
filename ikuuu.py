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
import sys
import time
import random
from urllib.parse import urlparse

# 域名配置（支持多个域名）
DOMAINS = ['https://ikuuu.de', 'https://ikuuu.one', 'https://ikuuu.boo']
CURRENT_DOMAIN = DOMAINS[0]  # 默认使用第一个域名

class IkuuuSign:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': CURRENT_DOMAIN,
            'Referer': f'{CURRENT_DOMAIN}/auth/login',
            'X-Requested-With': 'XMLHttpRequest'
        })
        self.login_url = f'{CURRENT_DOMAIN}/auth/login'
        self.user_url = f'{CURRENT_DOMAIN}/user'
        self.checkin_url = f'{CURRENT_DOMAIN}/user/checkin'
        self.max_retries = 7
        self.timeout = 10

    def check_login_status(self):
        """检查登录状态"""
        try:
            response = self.session.get(self.user_url, timeout=self.timeout, allow_redirects=False)
            # 如果重定向到登录页面，说明未登录
            if response.status_code == 302 or 'login' in response.url:
                return False
            return True
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            return False

    def login(self, email, password):
        """登录账号"""
        login_data = {
            'email': email,
            'passwd': password
        }
        
        try:
            response = self.session.post(self.login_url, data=login_data, timeout=self.timeout)
            if response.status_code == 200:
                result = response.json()
                if result.get('ret') == 1:
                    print("登录成功")
                    return True
                else:
                    print(f"登录失败: {result.get('msg', '未知错误')}")
                    return False
            else:
                print(f"登录请求失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"登录过程中发生错误: {e}")
            return False

    def sign_in(self, email, password, remark=""):
        """执行签到流程"""
        print(f"\n开始处理账号: {remark or email}")
        
        # 首先检查是否已登录
        if not self.check_login_status():
            print("未登录，尝试登录...")
            if not self.login(email, password):
                return "登录失败，请检查账号密码"
        
        # 执行签到（带重试机制）
        for retry in range(self.max_retries):
            try:
                # 随机延迟1-5秒（模拟原脚本行为）
                delay = 1 + random.random() * 4
                time.sleep(delay)
                
                response = self.session.post(self.checkin_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    msg = result.get('msg', '签到成功')
                    print(f"签到结果: {msg}")
                    return msg
                else:
                    print(f"签到请求失败，状态码: {response.status_code}，第{retry + 1}次重试")
                    
            except requests.exceptions.Timeout:
                print(f"请求超时，第{retry + 1}次重试")
            except requests.exceptions.RequestException as e:
                print(f"网络错误: {e}，第{retry + 1}次重试")
            except Exception as e:
                print(f"未知错误: {e}，第{retry + 1}次重试")
            
            # 最后一次重试后仍然失败
            if retry == self.max_retries - 1:
                return "签到失败：超过最大重试次数"
            
            # 重试间隔
            time.sleep(3)
        
        return "签到流程异常结束"

    def try_different_domains(self, email, password, remark=""):
        """尝试不同的域名"""
        for domain in DOMAINS:
            print(f"\n尝试域名: {domain}")
            self.login_url = f'{domain}/auth/login'
            self.user_url = f'{domain}/user'
            self.checkin_url = f'{domain}/user/checkin'
            self.session.headers.update({
                'Origin': domain,
                'Referer': f'{domain}/auth/login'
            })
            
            result = self.sign_in(email, password, remark)
            if "登录失败" not in result and "签到失败" not in result:
                return result
        
        return "所有域名尝试均失败"

def get_accounts():
    """从环境变量中获取账号信息"""
    ikuuu = os.getenv("ikuuu")
    if ikuuu:
        return ikuuu.split('#')
    else:
        print("未找到ikuuu环境变量")
        print("请在环境变量中设置ikuuu，格式：邮箱1&密码1&备注1#邮箱2&密码2&备注2")
        sys.exit(1)

def send_notification(remark, message):
    """发送通知"""
    try:
        push_plus_token = os.getenv("PUSH_PLUS_TOKEN")
        push_plus_user = os.getenv("PUSH_PLUS_USER")
        
        if not push_plus_token:
            print("未设置PUSH_PLUS_TOKEN，跳过通知")
            return
        
        url = "http://www.pushplus.plus/send"
        data = {
            "token": push_plus_token,
            "title": f"iKuuu签到结果 - {remark}",
            "content": f"账号: {remark}\n结果: {message}",
            "template": "txt"
        }
        
        if push_plus_user:
            data["topic"] = push_plus_user
            
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("通知发送成功")
        else:
            print(f"通知发送失败: {response.status_code}")
    except Exception as e:
        print(f"发送通知时出错: {e}")

def main():
    """主函数"""
    print("开始执行iKuuu签到脚本")
    
    accounts = get_accounts()
    print(f"找到 {len(accounts)} 个账号")
    
    signer = IkuuuSign()
    
    for account in accounts:
        parts = account.split('&')
        if len(parts) >= 2:
            email = parts[0].strip()
            password = parts[1].strip()
            remark = parts[2].strip() if len(parts) > 2 else email
            
            print(f"\n{'='*50}")
            print(f"处理账号: {remark} ({email})")
            print(f"{'='*50}")
            
            # 执行签到
            result = signer.try_different_domains(email, password, remark)
            
            # 发送通知
            send_notification(remark, result)
            
            # 清理会话状态，为下一个账号准备
            signer.session = requests.Session()
            signer.session.headers.update(signer.session.headers)
        else:
            print(f"账号格式错误: {account}")
    
    print("\n所有账号处理完成")

if __name__ == '__main__':
    main()
