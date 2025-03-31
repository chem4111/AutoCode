#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : github@wd210010 https://github.com/wd210010/just_for_happy
# @Time : 2023/2/27 13:23
# -------------------------------
# cron "30 7 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('天气推送')

import requests, json ,os,notify

# 城市code 自己城市的code https://fastly.jsdelivr.net/gh/Oreomeow/checkinpanel@master/city.json 这个网址查看
# city_code = '101190404'

# 青龙变量 city_code
city_code = os.getenv("city_code")


r = requests.get(
    f"http://t.weather.itboy.net/api/weather/city/{city_code}"
)
d = json.loads(r.text)
result2 = json.loads(r.text)['cityInfo']

msg = (
    f' 城市：{d["cityInfo"]["parent"]} {d["cityInfo"]["city"]}\n'
    f' 日期：{d["data"]["forecast"][0]["ymd"]} {d["data"]["forecast"][0]["week"]}\n'
    f' 天气：{d["data"]["forecast"][0]["type"]}\n'
    f' 温度：{d["data"]["forecast"][0]["high"]} {d["data"]["forecast"][0]["low"]}\n'
    f' 湿度：{d["data"]["shidu"]}\n'
    f' 空气质量：{d["data"]["quality"]}\n'
    f' PM2.5：{d["data"]["pm25"]}\n'
    f' PM10：{d["data"]["pm10"]}\n'
    f' 风力风向 {d["data"]["forecast"][0]["fx"]} {d["data"]["forecast"][0]["fl"]}\n'
    f' 感冒指数：{d["data"]["ganmao"]}\n'
    f' 温馨提示：{d["data"]["forecast"][0]["notice"]}\n'
    f' 更新时间：{d["time"]}'
)


w_list = []
for i in range(7):
    list = [
        d['data']['forecast'][i]['ymd'],
        d['data']['forecast'][i]['week'],
        d['data']['forecast'][i]['type'],
        d['data']['forecast'][i]['low'],
        d['data']['forecast'][i]['high'],
        d['data']['forecast'][i]['notice']
    ]
    w_list.append(list)
seven_days_weather = str(w_list).replace('], [','\n').replace(', ','').replace('[','').replace(']','').replace('\'',' ')
msg_total = (msg + '\n\n'+ seven_days_weather)
print(msg_total)
notify.send("保定天气", msg_total)
