import requests
from collections import Counter
from datetime import datetime
import random
import os
import json

PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN")
PUSH_PLUS_USER = os.getenv("PUSH_PLUS_USER")
PREDICTION_FILE = "predictions.json"  # 存储预测数据的文件


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


def load_previous_predictions():
    """加载之前的预测数据"""
    if os.path.exists(PREDICTION_FILE):
        with open(PREDICTION_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_predictions(predictions):
    """保存本次预测数据"""
    data = {
        "期数": str(int(current_issue) + 1),  # 预测下一期
        "预测": predictions,
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(PREDICTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def check_winning(predicted_numbers, actual_red, actual_blue):
    """检查预测号码的中奖情况"""
    actual_red_set = set(actual_red.split(","))
    actual_blue = int(actual_blue)
    
    results = []
    for idx, group in enumerate(predicted_numbers, 1):
        red_match = len(set(group["红球"]) & actual_red_set)
        blue_match = (group["蓝球"] == actual_blue)

        if red_match == 6 and blue_match:
            level = "一等奖"
        elif red_match == 6:
            level = "二等奖"
        elif red_match == 5 and blue_match:
            level = "三等奖"
        elif red_match == 5 or (red_match == 4 and blue_match):
            level = "四等奖"
        elif red_match == 4 or (red_match == 3 and blue_match):
            level = "五等奖"
        elif blue_match:
            level = "六等奖"
        else:
            level = "未中奖"
        
        results.append(f"预测第 {idx} 组号码: 中奖等级: {level}")

    return "\n".join(results)


def send_notice(content, token, topic):
    """发送通知"""
    title = "双色球预测"
    url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template=html&topic={topic}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"发送通知失败: {e}")


# 获取当前日期
current_date = datetime.now()

# 获取最新一期的数据
kjList = get_recent_data()

if not kjList:
    print("未能获取开奖数据。")
else:
    # 获取当前开奖期号
    latest_record = kjList[0]
    current_issue = latest_record.code

    # 读取上次预测数据
    previous_data = load_previous_predictions()
    last_pred_issue = previous_data.get("期数")
    last_pred_numbers = previous_data.get("预测", [])

    # 预测下一期的五组数据
    next_issue = str(int(current_issue) + 1)
    predicted_data = []
    for i in range(5):
        red_balls = random.sample(range(1, 34), 6)
        red_balls.sort()
        blue_ball = random.randint(1, 16)
        predicted_data.append({"红球": red_balls, "蓝球": blue_ball})

    # 打印预测的五组数据
    predicted_content = f"\n预测期数: {next_issue}\n"
    for i, data in enumerate(predicted_data, 1):
        predicted_content += f"\n预测第 {i} 组号码:\n红球: {', '.join(map(str, data['红球']))}\n蓝球: {data['蓝球']}\n"

    # 计算上次预测的中奖情况
    if last_pred_issue and last_pred_issue == current_issue:
        winning_results = check_winning(last_pred_numbers, latest_record.red, latest_record.blue)
        last_winning_content = f"\n上次预测期数 {last_pred_issue} 的中奖情况:\n{winning_results}\n"
    else:
        last_winning_content = "\n上次五期中奖等级: 本期没有预测\n"

    # 最新开奖信息
    latest_content = (f"\n最新一期的开奖信息：\n期数: {latest_record.code}, 红球: {latest_record.red}, "
                      f"蓝球: {latest_record.blue}\n")

    # 保存当前预测
    save_predictions(predicted_data)

    # 发送 PushPlus 通知
    send_notice(predicted_content + last_winning_content + latest_content, PUSH_PLUS_TOKEN, PUSH_PLUS_USER)

    # 打印最终结果
    print(predicted_content)
    print(last_winning_content)
    print(latest_content)

    # 每月清理一次预测数据
    if datetime.now().day == 1:
        if os.path.exists(PREDICTION_FILE):
            os.remove(PREDICTION_FILE)
            print("预测数据已清理")
