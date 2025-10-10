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

def get_next_holiday():
    # 获取结构化信息
    next_info = get_json("http://timor.tech/api/holiday/next")
    # 获取人类友好的描述（TTS版）
    tts_info = get_json("http://timor.tech/api/holiday/tts/next")

    if not next_info or next_info.get("code") != 0:
        return None

    h = next_info.get("holiday", {})
    result = {
        "name": h.get("name"),
        "date": h.get("date"),
        "remain": h.get("rest"),
        "source": "Timor Tech",
    }

    # 附加自然语言描述
    if tts_info and tts_info.get("tts"):
        result["tts"] = tts_info["tts"]

    return result

def main():
    print("🚀 开始获取节假日信息...")

    result = get_next_holiday()

    if result:
        save_cache(result)
        msg = (
            f"下个节假日是 {result.get('remain')} 天后的 "
            f"{result.get('name')}（{result.get('date')}）\n"
            f"🗣 {result.get('tts', '')}\n来源：{result.get('source')}"
        )
        print("✅ 获取成功：Timor Tech")
        print(msg)
        notify.send(title, msg)
    else:
        print("⚠️ Timor API 失败，尝试读取缓存...")
        result = load_cache()
        if result:
            msg = f"（缓存）下个节假日：{result.get('name')} {result.get('date')}，剩余 {result.get('remain')} 天"
            notify.send(title, msg)
        else:
            msg = "❌ 无法获取节假日信息，也没有缓存。"
            notify.send(title, msg)

    print("✅ 任务完成。")

if __name__ == "__main__":
    main()
