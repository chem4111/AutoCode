#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/10/10
# -------------------------------
# cron "0 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('下个节假日')

import requests
import json
import os
import notify

title = "下个节假日"
CACHE_FILE = "/ql/data/scripts/chem4111_AutoCode/last_holiday.json"
TIMOR_URL = "https://timor.tech/api/holiday/next"

def get_json(url):
    """带UA的GET请求，防止403"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ 请求失败: {url} | 错误: {e}")
        return None

def save_cache(data):
    """写入缓存文件"""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 缓存写入失败: {e}")

def load_cache():
    """读取缓存"""
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def parse_timor(data):
    """解析Timor返回数据"""
    try:
        h = data.get("holiday", {})
        return {
            "name": h.get("name", "未知节日"),
            "date": data.get("date", "未知日期"),
            "remain": data.get("remain", "未知天数"),
            "source": "Timor Tech"
        }
    except Exception:
        return None

def main():
    print("🚀 开始获取节假日信息...")

    data = get_json(TIMOR_URL)
    result = None

    if data:
        result = parse_timor(data)
        if result and result.get("name") and result.get("date"):
            print(f"✅ 获取成功: {result['name']} {result['date']}")
            save_cache(result)
    else:
        print("⚠️ Timor接口访问失败，尝试读取缓存...")
        result = load_cache()
        if result:
            result["source"] = f"{result.get('source', 'Timor Tech')}（缓存）"

    # 输出和通知
    if result:
        info = f"下个节假日是 {result.get('remain')} 天后的 {result.get('name')}（{result.get('date')}） 来源：{result.get('source')}"
        print(info)
        notify.send(title, info)
    else:
        msg = "❌ 无法获取节假日信息，也没有缓存。"
        print(msg)
        notify.send(title, msg)

    print("✅ 任务完成。")

if __name__ == "__main__":
    main()

