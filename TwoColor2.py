import requests
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# 配置参数
token = "your_pushplus_token"
topic = "your_pushplus_topic"
data_file = Path("ssq_data.json")
predict_file = Path("predictions.json")


class SsqData:
    def __init__(self, code, date, red, blue):
        self.code = code
        self.date = datetime.strptime(date, '%Y-%m-%d')
        self.red = list(map(int, red.split(',')))
        self.blue = int(blue)


class PredictionModel:
    def __init__(self):
        self.history = self.load_history()
        self.interval_weights = {
            '红球': {1: 0.4, 2: 0.35, 3: 0.25},  # 基于[[1][6]()的三区分布
            '蓝球': {1: 0.6, 2: 0.4}  # 大小区划分
        }
        self.exclude_rules = {
            'red_head_tail': True,  # 排除上期和值头尾[1]()
            'blue_recent': 5,  # 排除最近N期蓝球[1]()
            'same_period': True  # 排除去年同期号[1]()
        }

    # 数据加载与存储
    def load_history(self):
        try:
            with open(data_file, 'r') as f:
                return [SsqData(**item) for item in json.load(f)]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_history(self, new_data):
        combined = self.history + new_data
        with open(data_file, 'w') as f:
            json.dump([vars(d) for d in combined], f, default=str)

    # 核心预测算法
    def generate_prediction(self):
        red_probs = self._calculate_red_probability()
        blue_probs = self._calculate_blue_probability()

        predictions = []
        for _ in range(5):
            red = self._select_red(red_probs)
            blue = self._select_blue(blue_probs)
            predictions.append({'红球': red, '蓝球': blue})
        return predictions

    def _calculate_red_probability(self):
        # 融合区间权重和冷热分析[[2][5][6]()
        counter = Counter(n for d in self.history for n in d.red)
        period_data = [d for d in self.history if d.date.year == datetime.now().year - 1]
        period_exclude = set(n for d in period_data for n in d.red)  # [1]()

        probs = {}
        for n in range(1, 34):
            interval = 1 if n <= 11 else 2 if n <= 22 else 3
            base = counter[n] / len(self.history) if self.history else 1 / 33
            weight = self.interval_weights['红球'][interval]
            if n in period_exclude and self.exclude_rules['same_period']:
                weight *= 0.2  # 降低去年同期号概率[1]()
            probs[n] = base * weight
        return self._apply_exclusion_rules(probs)

    def _calculate_blue_probability(self):
        # 结合大小区分布和近期排除[[1][2]()
        counter = Counter(d.blue for d in self.history)
        recent_blue = [d.blue for d in self.history[:self.exclude_rules['blue_recent']]]

        probs = {}
        for n in range(1, 17):
            interval = 1 if n <= 8 else 2
            base = counter[n] / len(self.history) if self.history else 1 / 16
            weight = self.interval_weights['蓝球'][interval]
            if n in recent_blue and self.exclude_rules['blue_recent']:
                weight *= 0.3  # 降低近期出现过的蓝球概率[2]()
            probs[n] = base * weight
        return probs

    # 高级排除策略
    def _apply_exclusion_rules(self, probs):
        if self.exclude_rules['red_head_tail'] and self.history:
            last_sum = sum(self.history[0].red)
            head, tail = last_sum // 100 % 10, last_sum % 10  # [1]()
            for n in probs:
                if n in (head, tail):
                    probs[n] *= 0.2
        return probs

    # 选择算法
    def _select_red(self, probs):
        numbers = set()  # 使用 set 避免重复
        while len(numbers) < 6:
            candidates = random.choices(list(probs.keys()), weights=list(probs.values()), k=10)
            for n in candidates:
                numbers.add(n)
                if len(numbers) == 6:
                    break
        return sorted(numbers)

    def _select_blue(self, probs):
        return random.choices(list(probs.keys()), weights=list(probs.values()), k=1)[0]


# 数据获取与处理
def fetch_new_data():
    url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
    params = {
        "name": "ssq",
        "pageNo": 1,
        "pageSize": 30,
        "systemType": "PC"
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        new_data = [
            SsqData(
                code=item['code'],
                date=item['date'],
                red=item['red'],
                blue=item['blue']
            ) for item in res.json()['result']
        ]
        return new_data
    except Exception as e:
        print(f"数据获取失败: {e}")
        return []


# 预测验证与优化
def check_prediction(model):
    if not model.history or not predict_file.exists():
        return

    with open(predict_file, 'r') as f:
        last_pred = json.load(f)[0]

    latest = model.history[0]
    red_match = len(set(last_pred['红球']) & set(latest.red))
    blue_match = last_pred['蓝球'] == latest.blue

    # 根据命中情况动态调整权重[[5][7]()
    adjustment = 1 + red_match * 0.1 + blue_match * 0.2
    for k in model.interval_weights['红球']:
        model.interval_weights['红球'][k] *= adjustment


# 发送通知
def send_notice(content, token, topic):
    url = "http://pushplus.hxtrip.com/send"
    payload = {
        "token": token,
        "title": topic,
        "content": content,
        "template": "html"  # 根据需要设置不同的通知模板
    }
    try:
        res = requests.post(url, data=payload)
        res.raise_for_status()
        print("通知发送成功")
    except Exception as e:
        print(f"通知发送失败: {e}")


# 主流程
if __name__ == "__main__":
    # 初始化模型
    model = PredictionModel()

    # 获取新数据
    new_data = fetch_new_data()
    if new_data:
        model.save_history(new_data)
        model.history = model.load_history()  # 刷新数据

    # 生成预测
    predictions = model.generate_prediction()
    with open(predict_file, 'w') as f:
        json.dump(predictions, f)

    # 验证上次预测
    check_prediction(model)

    # 构建通知内容
    content = "最新预测结果：\n"
    for i, pred in enumerate(predictions, 1):
        content += f"第{i}组：红球{' '。join(map(str, pred['红球']))} | 蓝球{pred['蓝球']}\n"

    # 发送通知（需配置PushPlus）
    send_notice(content, token, topic)
