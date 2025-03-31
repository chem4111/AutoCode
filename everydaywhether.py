#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('天气推送')

import requests
import json
import os
import notify


def get_city_code():
    """
    获取城市代码，优先从环境变量中获取
    """
    return os.getenv("city_code")


def fetch_weather_data(city_code):
    """
    根据城市代码获取天气数据
    """
    try:
        response = requests.get(f"http://t.weather.itboy.net/api/weather/city/{city_code}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
    return None


def generate_weather_message(data):
    """
    生成当前天气信息的消息
    """
    if not data:
        return ""
    city_info = data["cityInfo"]
    today_forecast = data["data"]["forecast"][0]
    return (
        f' 城市：{city_info["parent"]} {city_info["city"]}\n'
        f' 日期：{today_forecast["ymd"]} {today_forecast["week"]}\n'
        f' 天气：{today_forecast["type"]}\n'
        f' 温度：{today_forecast["high"]} {today_forecast["low"]}\n'
        f' 湿度：{data["data"]["shidu"]}\n'
        f' 空气质量：{data["data"]["quality"]}\n'
        f' PM2.5：{data["data"]["pm25"]}\n'
        f' PM10：{data["data"]["pm10"]}\n'
        f' 风力风向 {today_forecast["fx"]} {today_forecast["fl"]}\n'
        f' 感冒指数：{data["data"]["ganmao"]}\n'
        f' 温馨提示：{today_forecast["notice"]}\n'
        f' 更新时间：{data["time"]}'
    )


def generate_seven_days_weather(data):
    """
    生成未来七天的天气信息
    """
    if not data:
        return ""
    weather_list = []
    for forecast in data["data"]["forecast"]:
        weather_list.append([
            forecast["ymd"],
            forecast["week"],
            forecast["type"],
            forecast["low"],
            forecast["high"],
            forecast["notice"]
        ])
    return str(weather_list).replace('], [', '\n').replace(', ', '').replace('[', '').replace(']', '').replace('\'', ' ')


if __name__ == "__main__":
    city_code = get_city_code()
    if not city_code:
        print("未获取到城市代码，请设置环境变量 city_code。")
    else:
        weather_data = fetch_weather_data(city_code)
        current_weather_msg = generate_weather_message(weather_data)
        seven_days_weather_msg = generate_seven_days_weather(weather_data)
        total_msg = f"{current_weather_msg}\n\n{seven_days_weather_msg}"
        print(total_msg)
        notify.send("昆山天气", total_msg)
    
