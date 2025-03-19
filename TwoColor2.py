import requests
from collections import Counter
from datetime import datetime
import random
import os
import json

PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN")
PUSH_PLUS_USER = os.getenv("PUSH_PLUS_USER")
PREDICTION_FILE = "predictions.json"

class LotteryRecord:
    def __init__(self, code, red, blue):
        self.code = code
        self.red = red
        self.blue = blue

def fetch_lottery_data():
    url = "https://api.apiopen.top/getLottery"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == 200:
            return [LotteryRecord(d["expect"], d["red"], d["blue"]) for d in data["data"]]
    return []

def save_predictions(predictions):
    with open(PREDICTION_FILE, "w", encoding="utf-8") as f:
        json.dump(predictions, f, ensure_ascii=False, indent=4)

def load_previous_predictions():
    if os.path.exists(PREDICTION_FILE):
        with open(PREDICTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def get_frequent_numbers(kjList, top_n=10):
    red_counter = Counter()
    blue_counter = Counter()
    
    for record in kjList:
        red_counter.update(record.red.split(","))
        blue_counter.update([record.blue])

    most_common_reds = [int(num) for num, _ in red_counter.most_common(top_n)]
    most_common_blues = [int(num) for num, _ in blue_counter.most_common(top_n // 2)]

    return most_common_reds, most_common_blues

def adjust_by_last_draw(last_reds, last_blue, red_candidates):
    adjusted_reds = set()
    
    for red in last_reds:
        red = int(red)
        if red > 16:  
            candidates = [r for r in red_candidates if r < 17]
        else:  
            candidates = [r for r in red_candidates if r >= 17]

        if candidates:
            adjusted_reds.add(random.choice(candidates))

    while len(adjusted_reds) < 6:
        adjusted_reds.add(random.choice(red_candidates))

    adjusted_reds = sorted(adjusted_reds)

    blue_candidates = [b for b in range(1, 17) if b != int(last_blue)]
    adjusted_blue = random.choice(blue_candidates)

    return adjusted_reds, adjusted_blue

def check_prizes(predicted_data, current_result):
    prize_levels = []
    current_reds = set(map(int, current_result.red.split(",")))
    current_blue = int(current_result.blue)

    for prediction in predicted_data:
        red_match = len(set(prediction["红球"]) & current_reds)
        blue_match = (prediction["蓝球"] == current_blue)

        if red_match == 6 and blue_match:
            prize_levels.append("一等奖")
        elif red_match == 6:
            prize_levels.append("二等奖")
        elif red_match == 5 and blue_match:
            prize_levels.append("三等奖")
        elif red_match == 5 or (red_match == 4 and blue_match):
            prize_levels.append("四等奖")
        elif red_match == 4 or (red_match == 3 and blue_match):
            prize_levels.append("五等奖")
        else:
            prize_levels.append("未中奖")

    return prize_levels

def send_notice(message, token, user):
    if token and user:
        url = "http://www.pushplus.plus/send"
        data = {"token": token, "title": "双色球预测", "content": message, "topic": user}
        requests.post(url, json=data)

def main():
    start_time = datetime.now()
    print(f"\n## 开始执行... {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    kjList = fetch_lottery_data()
    if not kjList:
        print("无法获取开奖数据")
        return

    current_issue = kjList[0].code  
    previous_predictions = load_previous_predictions()

    if previous_predictions and previous_predictions["期数"] == str(int(current_issue) - 1):
        last_prizes = check_prizes(previous_predictions["预测"], kjList[0])
    else:
        last_prizes = ["本期没有预测"] * 5

    most_common_reds, most_common_blues = get_frequent_numbers(kjList)

    next_issue = str(int(current_issue) + 1)
    predicted_data = []

    for i in range(5):
        if len(kjList) > 1:
            last_reds = kjList[1].red.split(",")  
            last_blue = kjList[1].blue  
            red_balls, blue_ball = adjust_by_last_draw(last_reds, last_blue, most_common_reds)
        else:
            red_balls = sorted(random.sample(most_common_reds, 6))
            blue_ball = random.choice(most_common_blues)

        predicted_data.append({"红球": red_balls, "蓝球": blue_ball})

    message_content = f"预测期数: {next_issue}\n"
    for i, data in enumerate(predicted_data):
        message_content += (f"\n预测第 {i+1} 组号码:\n"
                            f"红球: {', '.join(map(str, data['红球']))}\n"
                            f"蓝球: {data['蓝球']}\n")

    message_content += "\n上次五期中奖等级:\n"
    for i, level in enumerate(last_prizes):
        message_content += f"预测第 {i+1} 组号码: 中奖等级: {level}\n"

    latest_record = kjList[0]
    message_content += (f"\n最新一期的开奖信息：\n期数: {latest_record.code}, 红球: {latest_record.red}, "
                        f"蓝球: {latest_record.blue}\n")

    print(message_content)

    save_predictions({"期数": next_issue, "预测": predicted_data})

    send_notice(message_content, PUSH_PLUS_TOKEN, PUSH_PLUS_USER)

    end_time = datetime.now()
    elapsed_time = (end_time - start_time).total_seconds()
    print(f"\n## 执行结束... {end_time.strftime('%Y-%m-%d %H:%M:%S')} 耗时 {elapsed_time:.2f} 秒")

if __name__ == "__main__":
    main()
