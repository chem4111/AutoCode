import requests
import os
import random
from dataclasses import dataclass
from collections import Counter
from datetime import datetime
from typing import List


# 配置信息（建议通过环境变量设置）
PUSH_PLUS_TOKEN = os.getenv("PUSH_PLUS_TOKEN")
PUSH_PLUS_TOPIC = os.getenv("PUSH_PLUS_TOPIC")

@dataclass
class LotteryResult:
    code: str
    red_balls: list[int]
    blue_ball: int

def fetch_lottery_data() -> list[LotteryResult]:
    """获取最近30期开奖数据"""
    url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
    params = {
        "name": "ssq"，
        "pageNo": 1，
        "pageSize": 30，
        "systemType": "PC"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [
            LotteryResult(
                code=item["code"],
                red_balls=list(map(int, item["red"].split(","))),
                blue_ball=int(item["blue"])
            )
            for item in data.get("result", [])
        ]
    except Exception as e:
        print(f"数据获取失败: {e}")
        return []

def calculate_probabilities(results: list[LotteryResult]) -> tuple[dict, dict]:
    """计算号码出现概率"""
    red_counter = Counter()
    blue_counter = Counter()
    
    for result in results:
        red_counter.update(result.red_balls)
        blue_counter.update([result.blue_ball])
    
    total = len(results)
    red_prob = {num: count/total for num, count in red_counter.items()}
    blue_prob = {num: count/total for num, count in blue_counter.items()}
    return red_prob, blue_prob

def weighted_select(numbers: list[int], weights: list[float], count: int) -> list[int]:
    """加权随机选择不重复号码"""
    selected = []
    candidates = numbers.copy()
    candidate_weights = weights.copy()
    
    for _ in range(count):
        total = sum(candidate_weights)
        if total == 0:
            return random.sample(numbers, count)
        probabilities = [w/total for w in candidate_weights]
        chosen_idx = random.choices(range(len(candidates)), weights=probabilities, k=1)[0]
        selected.append(candidates[chosen_idx])
        del candidates[chosen_idx]
        del candidate_weights[chosen_idx]
    return sorted(selected)

def generate_prediction(red_prob: dict, blue_prob: dict, num_sets=5) -> list[dict]:
    """生成预测结果"""
    red_numbers = list(red_prob.keys())
    red_weights = [red_prob[num] for num in red_numbers]
    blue_numbers = list(blue_prob.keys())
    blue_weights = [blue_prob[num] for num in blue_numbers]

    predictions = []
    for _ in range(num_sets):
        red = weighted_select(red_numbers, red_weights, 6)
        blue = random.choices(blue_numbers, weights=blue_weights, k=1)[0]
        predictions.append({
            "red": red,
            "blue": blue,
            "combined": ", ".join(f"{n:02d}" for n in red) + f" + {blue:02d}"
        })
    return predictions

def format_message(predictions: list[dict], latest: LotteryResult) -> str:
    """格式化推送消息"""
    html_content = """
    <style>
        .lottery-table {border-collapse: collapse; margin: 20px 0;}
        .lottery-table td, .lottery-table th {padding: 10px; border: 1px solid #ddd;}
        .red-ball {color: #c00; font-weight: bold;}
        .blue-ball {color: #00c; font-weight: bold;}
    </style>
    <h2>双色球预测结果</h2>
    <h3>最新开奖信息</h3>
    <p>期号：{latest_code}</p>
    <p>红球：<span class="red-ball">{latest_red}</span></p>
    <p>蓝球：<span class="blue-ball">{latest_blue:02d}</span></p>
    <h3>下期预测号码</h3>
    <table class="lottery-table">
        <tr><th>序号</th><th>预测号码</th></tr>
    """.format(
        latest_code=latest.code,
        latest_red=" ".join(f"{n:02d}" for n in latest.red_balls),
        latest_blue=latest.blue_ball
    )

    for i, pred in enumerate(predictions, 1):
        html_content += f"""
        <tr>
            <td>{i}</td>
            <td>
                <span class="red-ball">{pred['combined'].split(' + ')[0]}</span>
                <span class="blue-ball">+ {pred['combined'].split(' + ')[1]}</span>
            </td>
        </tr>
        """
    html_content += "</table>"
    return html_content

def send_pushplus_notification(content: str):
    """发送PushPlus通知"""
    api_url = "http://www.pushplus.plus/send"
    payload = {
        "token": PUSH_PLUS_TOKEN,
        "title": "双色球预测分析",
        "content": content,
        "template": "html",
        "topic": PUSH_PLUS_TOPIC
    }
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        print("通知发送状态:", response.status_code)
    except Exception as e:
        print(f"通知发送失败: {e}")

if __name__ == "__main__":
    # 获取历史数据
    history_data = fetch_lottery_data()
    if not history_data:
        print("未获取到开奖数据，请检查网络连接")
        exit()

    # 计算概率
    red_prob, blue_prob = calculate_probabilities(history_data)
    
    # 生成预测
    predictions = generate_prediction(red_prob, blue_prob)
    
    # 准备通知内容
    latest_result = history_data[0]
    message = format_message(predictions, latest_result)
    
    # 发送通知
    send_pushplus_notification(message)
    print("预测结果已发送")
