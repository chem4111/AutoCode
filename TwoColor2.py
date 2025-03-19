import requests
from collections import Counter
from datetime import datetime
import random
import os
import json

PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN")
PUSH_PLUS_USER = os.getenv("PUSH_PLUS_USER")
PREDICTION_FILE = "predictions.json"  # 用于存储历史预测数据的文件

class Ssq:
    def __init__(self, code, red, blue):
        self.code = code
        self.red = red
        self.blue = blue

def get_recent_data():
    url = ("http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/"
           "findDrawNotice?name=ssq&issueCount=&issueStart=&issueEnd=&dayStart=&dayEnd=&pageNo=1&pageSize=30&week=&systemType=PC")
    try:
        res = requests.get(url)
        res.raise_for_status()
        obj = res.json()
    except requests.RequestException as e:
        print(f"请求数据失败: {e}")
        return []

    kjList = []
    for item in obj['result']:
        ssq = Ssq(item['code'], item['red'], item['blue'])
        kjList.append(ssq)

    return kjList

def calculate_probabilities(kjList):
    red_counter = Counter()
    blue_counter = Counter()
    total_records = len(kjList)

    for record in kjList:
        red_counter.update(record.red.split(','))
        blue_counter.update(record.blue.split(','))

    red_probabilities = {num: count / total_records for num, count in red_counter.items()}
    blue_probabilities = {num: count / total_records for num, count in blue_counter.items()}

    return red_probabilities, blue_probabilities

def send_notice(content, token, topic):
    title = "双色球预测"
    url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template=html&topic={topic}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"发送通知失败: {e}")

def check_winning_level(prediction, actual):
    red_match = set(prediction["红球"]).intersection(set(actual.red.split(',')))
    blue_match = (prediction["蓝球"] == actual.blue)
    
    red_count = len(red_match)
    if red_count == 6:
        if blue_match:
            return "一等奖"
        else:
            return "二等奖"
    elif red_count == 5:
        if blue_match:
            return "三等奖"
        else:
            return "四等奖"
    elif red_count == 4:
        if blue_match:
            return "四等奖"
        else:
            return "五等奖"
    elif red_count == 3:
        if blue_match:
            return "五等奖"
        else:
            return "六等奖"
    elif red_count == 2 or red_count == 1 or red_count == 0:
        if blue_match:
            return "六等奖"
        else:
            return "未中奖"

def load_predictions():
    # 读取保存的预测数据
    if os.path.exists(PREDICTION_FILE):
        with open(PREDICTION_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_predictions(predictions):
    # 保存预测数据
    with open(PREDICTION_FILE, 'w', encoding='utf-8') as file:
        json.dump(predictions, file, ensure_ascii=False, indent=4)

# 获取当前日期
current_date = datetime.now()

# 获取最新一期的数据
kjList = get_recent_data()

if not kjList:
    print("未能获取开奖数据。")
else:
    # 预测下一期的五组数据
    predicted_data = []
    for i in range(5):
        # 生成红球
        red_balls = random.sample(range(1, 34), 6)
        red_balls.sort()

        # 生成蓝球
        blue_ball = random.randint(1, 16)

        predicted_data.append({"红球": red_balls, "蓝球": blue_ball})

    # 打印预测的下一期五组号码
    print("\n预测下一期的五组数据:")
    predicted_content = ""
    for i, data in enumerate(predicted_data, 1):
        predicted_content += f"预测第 {i} 组号码:\n"
        predicted_content += "红球: " + ", ".join(map(str, data["红球"])) + "\n"
        predicted_content += "蓝球: " + str(data["蓝球"]) + "\n"
        
        # 打印每组号码
        print(f"预测第 {i} 组号码:")
        print("红球: " + ", ".join(map(str, data["红球"])))
        print("蓝球:", data["蓝球"])
        print()

    # 获取上一期的预测数据
    last_pred = load_predictions()

    if last_pred:
        # 计算中奖等级并对比
        print("\n上次五期中奖等级:")
        for i, data in enumerate(predicted_data, 1):
            for record in kjList:
                level = check_winning_level(data, record)
                print(f"预测第 {i} 组号码: 中奖等级: {level}")
    else:
        print("本期没有预测数据，无法计算中奖等级")

    # 获取最新一期的开奖信息
    latest_record = kjList[0]
    latest_content = (f"\n最新一期的开奖信息：\n期数: {latest_record.code}, 红球: {latest_record.red}, "
                      f"蓝球: {latest_record.blue}\n")

    # 保存当前预测
    save_predictions(predicted_data)

    # 发送 PushPlus 通知
    send_notice(predicted_content + latest_content, PUSH_PLUS_TOKEN, PUSH_PLUS_USER)
