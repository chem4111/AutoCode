#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/24 13:23
# -------------------------------
# cron "30 5 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('ikuuu签到')


import requests
import os
import sys
import time
import random
import re
import notify


title = "ikuuu签到"

# 域名配置
DOMAINS = ['https://ikuuu.de', 'https://ikuuu.one', 'https://ikuuu.boo']

class IkuuuSign:
    def __init__(self, domain):
        self.domain = domain
        self.session = requests.Session()
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': domain,
            'Referer': f'{domain}/auth/login',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.session.headers.update(self.default_headers)
        self.login_url = f'{domain}/auth/login'
        self.user_url = f'{domain}/user'
        self.checkin_url = f'{domain}/user/checkin'
        self.max_retries = 3
        self.timeout = 10

    def reset_session(self):
        """重置 session 并恢复默认 headers"""
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def check_login_status(self):
        """检查登录状态"""
        try:
            response = self.session.get(self.user_url, timeout=self.timeout, allow_redirects=False)
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
            # 访问登录页获取初始 cookie
            self.session.get(f'{self.domain}/auth/login', timeout=self.timeout)

            response = self.session.post(self.login_url, data=login_data, timeout=self.timeout)
            print(f"登录响应状态码: {response.status_code}")

            # 原始响应（可读中文）
            raw_text = response.text.encode('utf-8').decode('unicode_escape', errors='ignore')
            print(f"登录原始响应: {raw_text[:500]}...")  # 截取前500字符

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('ret') == 1:
                        print("登录成功")
                        return True
                    else:
                        print(f"登录失败: {result.get('msg', '未知错误')}")
                        return False
                except:
                    # 非 JSON 响应，通过 URL 判断登录是否成功
                    if 'user' in response.url or 'dashboard' in response.url:
                        print("登录成功（通过 URL 判断）")
                        return True
                    else:
                        print("登录失败：无法解析响应")
                        return False
            else:
                print(f"登录请求失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"登录过程中发生错误: {e}")
            return False

    def sign_in(self):
        """执行签到"""
        for retry in range(self.max_retries):
            try:
                delay = 1 + random.random() * 4
                time.sleep(delay)

                response = self.session.post(self.checkin_url, timeout=self.timeout)

                # 尝试解析 JSON
                try:
                    result = response.json()
                    msg = result.get('msg', '签到成功')
                    ret = result.get('ret', 0)
                    parsed_info = f"[ret={ret}] {msg}"
                except Exception:
                    parsed_info = "解析失败"

                # 原始响应文本（可读中文）
                raw_text = response.text.encode('utf-8').decode('unicode_escape', errors='ignore')

                # 输出两部分
                print(f"签到解析信息: {parsed_info}")
                print(f"原始响应: {raw_text[:500]}")  # 截取前500字符，可调整

                return parsed_info

            except requests.exceptions.Timeout:
                print(f"签到请求超时，第{retry + 1}次重试...")
            except Exception as e:
                print(f"签到过程中发生错误: {e}，第{retry + 1}次重试...")

            if retry < self.max_retries - 1:
                time.sleep(3)

        return "签到失败：超过最大重试次数"

def get_accounts():
    """从环境变量中获取账号信息，返回 [(email, password, remark), ...]"""
    ikuuu = os.getenv("ikuuu")
    if not ikuuu:
        print("未找到 ikuuu 环境变量")
        print("请在环境变量中设置 ikuuu，格式示例：邮箱1&密码1&备注1#邮箱2&密码2&备注2")
        sys.exit(1)

    raw = ikuuu.strip().strip('"').strip("'")
    # 用 #、换行、; 分割
    entries = re.split(r'[#;\n]+', raw)

    accounts = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split('&', 2)
        if len(parts) < 2:
            print(f"忽略无效账号条目: {entry}")
            continue
        email = parts[0].strip()
        password = parts[1].strip()
        remark = parts[2].strip() if len(parts) > 2 and parts[2].strip() else email
        accounts.append((email, password, remark))
    if not accounts:
        print("未解析到有效账号，请检查 ikuuu 环境变量格式。")
        sys.exit(1)
    return accounts

def main():
    print("开始执行iKuuu签到脚本")
    accounts = get_accounts()
    print(f"找到 {len(accounts)} 个账号")

    for i, (email, password, remark) in enumerate(accounts, 1):
        print(f"\n{'='*60}")
        print(f"账号 {i}: {remark}")
        print(f"邮箱: {email}")
        print(f"密码长度: {len(password)}")
        print(f"{'='*60}")

        for domain in DOMAINS:
            print(f"\n尝试域名: {domain}")
            signer = IkuuuSign(domain)
            if not signer.check_login_status():
                print("未登录，尝试登录...")
                if signer.login(email, password):
                    result = signer.sign_in()
                    break
                else:
                    print(f"在域名 {domain} 上登录失败")
            else:
                print("已登录，直接签到")
                result = signer.sign_in()
                break
        else:
            result = "所有域名尝试均失败"
            print(result)

        print(f"\n账号 {i} 签到结果: {result}")
        print(f"{'='*60}\n")
        notify.send(f"{title} - {remark}", f"{email}\n{result}")

        # 账号间延迟
        if i < len(accounts):
            delay = 5
            print(f"等待 {delay} 秒后处理下一个账号...")
            time.sleep(delay)

if __name__ == '__main__':
    main()



