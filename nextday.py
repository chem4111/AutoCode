#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/24 13:23
# -------------------------------
# cron "0 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('下个节假日')


import requests
import json
import os
import notify

title = "下个节假日"
CACHE_FILE = "/ql/data/scripts/chem4111_AutoCode/last_holiday.json"

def get_json(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ 请求失败: {url} | 错误: {e}")
        return None

def save_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ 缓存写入失败: {e}")

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# 解析函数（按接口类型）
def parse_timor(holiday):
    try:
        h = holiday.get("holiday", {})
        return {
            "name": h.get("name"),
            "date": holiday.get("date"),
            "remain": holiday.get("remain", "未知天数"),
            "source": "Timor Tech"
        }
    except Exception:
        return None

def parse_appworlds(holiday, days):
    try:
        data = holiday.get("data", {})
        return {
            "name": data.get("name"),
            "date": data.get("date"),
            "remain": days.get("data"),
            "source": "AppWorlds"
        }
    except Exception:
        return None

def parse_jiejiari(holiday):
    try:
        return {
            "name": holiday.get("name"),
            "date": holiday.get("date"),
            "remain": holiday.get("remain", "未知天数"),
            "source": "节假日API"
        }
    except Exception:
        return None

def parse_oneapi(holiday):
    try:
        data = holiday.get("data", {})
        return {
            "name": data.get("holiday"),
            "date": data.get("date"),
            "remain": data.get("distance"),
            "source": "OneAPI"
        }
    except Exception:
        return None

def parse_nager(holiday):
    try:
        first = holiday[0]
        return {
            "name": first.get("localName"),
            "date": first.get("date"),
            "remain": "未知",
            "source": "Nager.Date"
        }
    except Exception:
        return None

def main():
    print("🚀 开始获取节假日信息...")

    sources = [
        ("Timor Tech", "https://timor.tech/api/holiday/next", parse_timor, None),
        ("AppWorlds", "https://date.appworlds.cn/next", parse_appworlds, "https://date.appworlds.cn/next/days"),
        ("节假日API", "https://api.jiejiariapi.com/next", parse_jiejiari, None),
        ("OneAPI", "https://oneapi.coderbox.cn/openapi/public/holiday/next", parse_oneapi, None),
        ("Nager.Date", "https://date.nager.at/api/v3/NextPublicHolidays/CN", parse_nager, None),
    ]

    result = None

    for name, url, parser, extra_url in sources:
        print(f"🔍 尝试接口: {name} ...")
        data = get_json(url)
        if not data:
            continue

        extra_data = get_json(extra_url) if extra_url else None
        result = parser(data) if not extra_url else parser(data, extra_data)

        if result and result.get("name") and result.get("date"):
            print(f"✅ 使用接口: {result['source']}")
            save_cache(result)
            break

    # 若所有接口都失败，则尝试读取缓存
    if not result:
        print("⚠️ 所有接口均失败，尝试读取缓存 ...")
        result = load_cache()
        if result:
            result["source"] = f"{result.get('source', '缓存')}（缓存）"

    # 输出 / 通知
    if result:
        info = f"下个节假日是 {result.get('remain')} 天后的 {result.get('name')}（{result.get('date')}） 来源：{result.get('source')}"
        print(info)
        notify.send(title, info)
    else:
        msg = "所有接口均失败且无缓存 ❌"
        print(msg)
        notify.send(title, msg)

    print("✅ 任务完成。")

if __name__ == "__main__":
    main()
