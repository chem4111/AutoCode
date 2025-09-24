#!/usr/bin/env python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/4/1 13:23
# -------------------------------
# cron "0 9 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('下个节假日')

import requests
import notify

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

def main():
    holiday = get_json(DATE_URL)
    holiday_days = get_json(DAYS_URL)

    if not holiday or not holiday_days:
        notify.send(title, "获取节假日信息失败 ❌")
        return

    daytime = holiday.get("data", {}).get("date", "未知日期")
    dayname = holiday.get("data", {}).get("name", "未知节日")
    remain = holiday_days.get("data", "未知天数")

    info = f"下个节假日是 {remain} 天后的 {dayname}（{daytime}）"
    print(info)
    notify.send(title, info)

if __name__ == "__main__":
    main()
