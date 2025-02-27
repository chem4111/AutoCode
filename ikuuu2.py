import requests
from collections import Counter, defaultdict
from datetime import datetime
import random
import itertools
import time

token = "your_pushplus_token"
topic = "your_pushplus_topic"

class Ssq:
    def __init__(self, code, red, blue):
        self.code = code
        self.red = red  # 直接存储为列表
        self.blue = blue
        self.date = datetime.strptime(code[:8], "%Y%m%d")

def get_recent_data():
    """获取最近100期开奖数据，包含异常重试机制"""
    url = "http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
    params = {
        "name": "ssq",
        "pageNo": 1,
        "pageSize": 100,
        "systemType": "PC"
    }
    
    for _ in range(3):  # 最大重试3次
        try:
            res = requests.get(url, params=params, timeout=15)
            res.raise_for_status()
            data = res.json()
            return [
                Ssq(
                    code=item['code'],
                    red=item['red'].split(','),
                    blue=item['blue']
                ) for item in data['result']
            ]
        except Exception as e:
            print(f"数据获取失败，10秒后重试... 错误信息: {e}")
            time.sleep(10)
    return []

def analyze_trends(kjList, recent_periods=30):
    """深度趋势分析函数"""
    # 数据切片：最近30期和全部历史数据
    recent_data = kjList[:recent_periods]
    all_data = kjList
    
    # 红球分析
    red_counter = Counter(itertools.chain(*[ssq.red for ssq in all_data]))
    recent_red_counter = Counter(itertools.chain(*[ssq.red for ssq in recent_data]))
    
    # 蓝球分析
    blue_counter = Counter(ssq.blue for ssq in all_data)
    recent_blue_counter = Counter(ssq.blue for ssq in recent_data))
    
    # 连号分析（最近30期）
    consecutive_count = sum(
        1 for ssq in recent_data 
        if any(int(ssq.red[i+1]) - int(ssq.red[i]) == 1 
        for i in range(5)
    )
    
    # 奇偶比统计
    parity_ratios = Counter(
        f"{sum(1 for n in ssq.red if int(n)%2)}:{6-sum(1 for n in ssq.red if int(n)%2)}" 
        for ssq in all_data
    )
    
    return {
        "red": {
            "hot": recent_red_counter.most_common(6),
            "cold": recent_red_counter.most_common()[:-7:-1],
            "all_time_hot": red_counter.most_common(6)
        },
        "blue": {
            "trend": recent_blue_counter.most_common(3),
            "historical": blue_counter.most_common(3)
        },
        "patterns": {
            "consecutive_rate": consecutive_count / recent_periods,
            "common_parity": parity_ratios.most_common(3)
        }
    }

def generate_red_numbers(trend_data):
    """智能红球生成引擎"""
    def weighted_selection(candidates, base_weight=1.0, decay=0.9):
        """带衰减权重的选择器"""
        weights = []
        for idx, num in enumerate(candidates):
            weights.append(base_weight * (decay ** idx))
        return random.choices(candidates, weights=weights, k=1)[0]
    
    # 候选池配置
    hot_pool = [num for num, _ in trend_data['red']['hot']]
    cold_pool = [num for num, _ in trend_data['red']['cold']]
    historic_pool = [num for num, _ in trend_data['red']['all_time_hot']]
    
    # 动态权重分配
    selection_plan = [
        (hot_pool, 0.5),    # 近期热号
        (historic_pool, 0.3),# 历史热号
        (cold_pool, 0.2)     # 冷门号码
    ]
    
    selected = set()
    while len(selected) < 6:
        pool, prob = random.choices(
            selection_plan, 
            weights=[p[1] for p in selection_plan]
        )[0]
        
        if not pool: continue
        
        # 区间平衡：确保1-11/12-22/23-33每个区间至少1个
        current_ranges = {get_range(n) for n in selected}
        if len(current_ranges) < 3:
            required_range = ({1,2,3} - current_ranges).pop()
            candidate = next((n for n in pool if get_range(n) == required_range), None)
            if candidate:
                selected.add(candidate)
                continue
        
        # 连号生成：确保至少1组连号
        if len(selected) >= 2 and not has_consecutive(selected):
            base_num = random.choice(list(selected))
            candidate = str(int(base_num) + 1) if int(base_num) < 33 else str(int(base_num)-1)
            if candidate not in selected and 1 <= int(candidate) <= 33:
                selected.add(candidate)
                continue
        
        # 常规选择
        selected.add(weighted_selection(pool))
    
    # 奇偶平衡调整
    return adjust_parity(sorted(selected, key=int), trend_data['patterns']['common_parity'])

def get_range(number):
    """获取号码所属区间"""
    num = int(number)
    if 1 <= num <= 11: return 1
    if 12 <= num <= 22: return 2
    return 3

def has_consecutive(numbers):
    """检查是否包含连号"""
    nums = sorted(int(n) for n in numbers)
    return any(nums[i+1] - nums[i] == 1 for i in range(len(nums)-1))

def adjust_parity(numbers, parity_patterns):
    """智能奇偶平衡调整"""
    target_ratios = [ratio for ratio, _ in parity_patterns]
    current_odd = sum(1 for n in numbers if int(n)%2)
    
    if str(current_odd) + ":" + str(6-current_odd) in target_ratios:
        return numbers
    
    # 寻找最佳调整方案
    best_diff = float('inf')
    best_set = numbers
    for _ in range(20):
        temp = numbers.copy()
        replace_pos = random.randint(0,5)
        new_num = str(random.choice([
            n for n in range(1,34) 
            if str(n) not in temp and n%2 != int(temp[replace_pos])%2
        ]))
        temp[replace_pos] = new_num
        new_odd = sum(1 for n in temp if int(n)%2)
        diff = min(abs(new_odd - int(ratio.split(':')[0])) for ratio in target_ratios)
        
        if diff < best_diff:
            best_diff = diff
            best_set = temp
            
    return sorted(best_set, key=int)

def generate_blue_number(trend_data):
    """蓝球趋势预测引擎"""
    trend_weights = {
        num: (3 - idx)*0.5  # 近期趋势权重
        for idx, (num, _) in enumerate(trend_data['blue']['trend'])
    }
    history_weights = {
        num: (3 - idx)*0.3  # 历史权重
        for idx, (num, _) in enumerate(trend_data['blue']['historical'])
    }
    cold_weights = {
        str(n): 0.2 for n in range(1,17) 
        if str(n) not in trend_data['blue']['trend']
    }
    
    combined = defaultdict(float)
    for d in [trend_weights, history_weights, cold_weights]:
        for num, weight in d.items():
            combined[num] += weight
    
    candidates = list(combined.keys())
    weights = [combined[num] for num in candidates]
    
    return random.choices(candidates, weights=weights, k=1)[0]

def validate_prediction(prediction, history):
    """预测结果验证"""
    # 避免重复历史组合
    for ssq in history[:20]:
        if (prediction['red'] == ssq.red and 
            prediction['blue'] == ssq.blue):
            return False
    
    # 冷号数量不超过2个
    cold_count = sum(1 for n in prediction['red'] 
                    if n in trend_data['red']['cold'])
    return cold_count <= 2

def generate_predictions(kjList, count=5):
    """生成预测结果"""
    trend_data = analyze_trends(kjList)
    predictions = []
    
    for _ in range(count*2):  # 生成双倍数量用于筛选
        red = generate_red_numbers(trend_data)
        blue = generate_blue_number(trend_data)
        
        prediction = {
            "red": red,
            "blue": blue,
            "score": calculate_combination_score(red, blue, trend_data)
        }
        
        if validate_prediction(prediction, kjList):
            predictions.append(prediction)
            if len(predictions) >= count:
                break
    
    # 按评分降序排列
    return sorted(predictions, key=lambda x: x['score'], reverse=True)[:count]

def calculate_combination_score(red, blue, trend_data):
    """组合评分系统"""
    score = 0
    
    # 红球得分
    for num in red:
        if num in trend_data['red']['hot']:
            score += 2
        elif num in trend_data['red']['all_time_hot']:
            score += 1.5
        else:
            score += 0.5
    
    # 蓝球得分
    if blue in [num for num, _ in trend_data['blue']['trend']:
        score += 3
    elif blue in [num for num, _ in trend_data['blue']['historical']:
        score += 2
    else:
        score += 1
    
    # 模式加分
    if has_consecutive(red):
        score += 1.5 * trend_data['patterns']['consecutive_rate'] * 10
    
    current_parity = f"{sum(1 for n in red if int(n)%2)}:{6-sum(1 for n in red if int(n)%2)}"
    for ratio, count in trend_data['patterns']['common_parity']:
        if current_parity == ratio:
            score += count * 0.1
    
    return score

def format_report(kjList, predictions, trend_data):
    """生成详细分析报告"""
    latest = kjList[0]
    
    report = [
        "🏆 双色球智能预测报告 🏆",
        f"📅 数据更新日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"🗂️ 分析数据量：{len(kjList)}期（截止到{latest.code}期）",
        "\n🔥 最新开奖信息：",
        f"   期号：{latest.code}",
        f"   红球：{' '.join(latest.red)}",
        f"   蓝球：{latest.blue}",
        "\n📈 趋势分析摘要：",
        "   红球热号（近期）：" + ' '.join([num for num, _ in trend_data['red']['hot']]),
        "   红球冷号（近期）：" + ' '.join([num for num, _ in trend_data['red']['cold']]),
        "   蓝球趋势：" + ' '.join([num for num, _ in trend_data['blue']['trend']]),
        f"   连号出现频率：{trend_data['patterns']['consecutive_rate']:.0%}",
        "   常见奇偶比：" + ' | '.join([f"{ratio} ({count}次)" for ratio, count in trend_data['patterns']['common_parity']]),
        "\n🎯 本期智能推荐："
    ]
    
    for idx, pred in enumerate(predictions, 1):
        report.append(
            f"{idx}. 红球：{' '.join(pred['red'])} 蓝球：{pred['blue']} "
            f"（评分：{pred['score']:.1f}）"
        )
    
    report.extend([
        "\n💡 策略说明：",
        "1. 融合近期趋势与历史规律的多维度分析",
        "2. 动态平衡热号、冷号和区间分布",
        "3. 智能规避近期重复组合",
        "4. 包含连号生成和奇偶比优化机制",
        "\n⚠️ 温馨提示：彩票有风险，投注需理性！"
    ])
    
    return '\n'.join(report)

def send_pushplus_report(content, token, topic):
    """发送PushPlus通知"""
    url = f"http://www.pushplus.plus/send"
    data = {
        "token": token,
        "title": "双色球智能分析报告",
        "content": content.replace('\n', '<br>'),
        "template": "html",
        "topic": topic
    }
    
    try:
        res = requests.post(url, json=data, timeout=10)
        res.raise_for_status()
        print("报告推送成功！")
    except Exception as e:
        print(f"推送失败：{e}")

if __name__ == "__main__":
    # 数据获取
    kjList = get_recent_data()
    if not kjList:
        print("获取开奖数据失败，请检查网络连接")
        exit()
    
    # 生成预测
    trend_data = analyze_trends(kjList)
    predictions = generate_predictions(kjList)
    
    # 生成报告
    report = format_report(kjList, predictions, trend_data)
    print(report)
    
    # 推送结果
    send_pushplus_report(report, token, topic)
