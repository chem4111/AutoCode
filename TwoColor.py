import requests
from collections import Counter
from datetime import datetime, timedelta
import random
import os

class Ssq:
    def __init__(self, code, red, blue):
        self.code = code
        self.red = red
        self.blue = blue

def get_recent_data():
    url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=&issueStart" \
          "=&issueEnd=&dayStart=&dayEnd=&pageNo=1&pageSize=30&week=&systemType=PC"
    res = requests.get(url)
    obj = res.json()

    kjList = []
    for item in obj['result']:
        ssq = Ssq(item['code'], item['red'], item['blue'])
        kjList.append(ssq)

    return kjList

def calculate_probabilities(kjList):
    red_counter_all = Counter()
    blue_counter_all = Counter()
    total_records_all = len(kjList)

    for record in kjList:
        red_counter_all.update(record.red.split(','))
        blue_counter_all.update(record.blue.split(','))

    red_probabilities_all = {num: count / total_records_all for num, count in red_counter_all.items()}
    blue_probabilities_all = {num: count / total_records_all for num, count in blue_counter_all.items()}

    return red_probabilities_all, blue_probabilities_all

def send_notice(content):
    # 获取环境变量的值
    token = os.getenv("PUSH_PLUS_TOKEN")
    topic = os.getenv("PUSH_PLUS_TOPIC")
    title = "双色球预测"
    
    # 构造请求的 URL
    url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template=html&topic={topic}"
    
    # 发送 GET 请求
    response = requests.get(url)
    
    # 关闭 PushPlus 返回的消息
    response.close()

# 获取当前日期
current_date = datetime.now()

# 获取最新一期的数据
kjList = get_recent_data()

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
    print("红球:", ", ".join(map(str, data["红球"])))
    print("蓝球:", data["蓝球"])
    print()

# 打印最近五期的期数和对应的双色球信息
print("\n最近五期的期数和对应的双色球信息:")
recent_kjList = kjList[:5]
for record in recent_kjList:
    print(f"期数: {record.code}, 红球: {record.red}, 蓝球: {record.blue}")

# 计算最近五期的红球和蓝球出现概率
red_probabilities_recent, blue_probabilities_recent = calculate_probabilities(recent_kjList)

# 打印最近五期的红球和蓝球出现概率
print("\n最近五期的红球出现概率:")
for number, prob in sorted(red_probabilities_recent.items()):
    print(f"号码 {number}: {prob:.2%}")

print("\n最近五期的蓝球出现概率:")
for number, prob in sorted(blue_probabilities_recent.items()):
    print(f"号码 {number}: {prob:.2%}")

# 计算所有期数的红球和蓝球出现概率
red_probabilities_all, blue_probabilities_all = calculate_probabilities(kjList)

# 打印所有期数的红球和蓝球出现概率
print("\n所有期数的红球出现概率:")
for number, prob in sorted(red_probabilities_all.items()):
    print(f"号码 {number}: {prob:.2%}")

print("\n所有期数的蓝球出现概率:")
for number, prob in sorted(blue_probabilities_all.items()):
    print(f"号码 {number}: {prob:.2%}")

# 获取最新一期的开奖信息
latest_record = kjList[0]
latest_content = f"\n最新一期的开奖信息：\n期数: {latest_record.code}, 红球: {latest_record.red}, 蓝球: {latest_record.blue}\n"

# 发送 PushPlus 通知
send_notice(predicted_content + latest_content)
