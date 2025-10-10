#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/10/10 13:23
# -------------------------------
# cron "0 9 * * *" script-path=xxx.py,tag=匹配cron用

import requests
import notify
from datetime import datetime

title = "下个节假日"
DATE_URL = "https://date.appworlds.cn/next"
DAYS_URL = "https://date.appworlds.cn/next/days"

def get_json(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ 请求失败: {url} | 错误: {e}")
        return None

def log_time(msg):
    """打印带时间戳的日志"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def main():
    log_time("🚀 开始获取节假日信息...")

    holiday = get_json(DATE_URL)
    holiday_days = get_json(DAYS_URL)

    # 打印原始返回数据，方便排查
    log_time("🧩 节假日接口 原始返回数据:")
    print(holiday)
    log_time("🧩 倒计时接口 原始返回数据:")
    print(holiday_days)

    # 判断数据有效性
    if not holiday or not holiday_days:
        log_time("❌ 无法获取节假日信息（请求失败或超时）")
        notify.send(title, "获取节假日信息失败 ❌")
        return

    # data字段为空的情况
    if not holiday.get("data") or not holiday_days.get("data"):
        log_time("⚠️ 接口无有效数据（可能所有节假日都过完了 🎉）")
        msg = "🎉 当前所有节假日已过完，等待官方发布新的放假安排。"
        notify.send(title, msg)
        return

    # 正常数据处理
    daytime = holiday.get("data", {}).get("date", "未知日期")
    dayname = holiday.get("data", {}).get("name", "未知节日")
    remain = holiday_days.get("data", "未知天数")

    info = f"下个节假日是 {remain} 天后的 {dayname}（{daytime}）"
    log_time(f"✅ {info}")
    notify.send(title, info)

    log_time("✅ 任务完成。")

if __name__ == "__main__":
    main()
