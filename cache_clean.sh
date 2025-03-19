#!/bin/bash

# 定义日志文件（使用系统标准日志目录）
LOG_FILE="/root/cache_clean.log"

# 检查日志目录权限
if [ ! -w "$(dirname "$LOG_FILE")" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 日志目录不可写，脚本退出。" >&2
    exit 1
fi

# 记录执行开始
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行缓存清理脚本" >> "$LOG_FILE"

# 1. 读取内存数据（使用绝对路径避免环境问题）
FREE_CMD="/usr/bin/free"
mem_line=$($FREE_CMD -h | grep 'Mem:')  # 示例输出："Mem: 989Mi 408Mi 580Mi ..."

# 2. 提取并清理单位（使用正则保留数字）
total_mem_raw=$(echo "$mem_line" | awk '{print $2}')  # 原始值："989Mi"
free_mem_raw=$(echo "$mem_line" | awk '{print $4}')    # 原始值："580Mi"

total_num=$(echo "$total_mem_raw" | sed 's/[^0-9.]//g')  # 提取数字：989
free_num=$(echo "$free_mem_raw" | sed 's/[^0-9.]//g')    # 提取数字：580

# 3. 验证数据有效性
if [[ -z "$total_num" || -z "$free_num" || ! "$total_num" =~ ^[0-9]+$ || ! "$free_num" =~ ^[0-9]+$ ]]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 内存值解析失败（total: $total_mem_raw, free: $free_mem_raw）" >> "$LOG_FILE"
    exit 1
fi

# 4. 计算内存使用
used_mem=$((total_num - free_num))                          # 整数运算
used_percentage=$(echo "scale=2; $used_mem / $total_num * 100" | bc)  # 浮点运算

# 5. 输出带单位的结果（保留原始单位）
unit="${total_mem_raw//[0-9.]/}"  # 提取单位（如 "Mi"）
echo "物理内存总计：${total_num}${unit}" >> "$LOG_FILE"    # 正确格式：989Mi
echo "空闲内存：${free_num}${unit}" >> "$LOG_FILE"          # 正确格式：580Mi
echo "已用内存：${used_mem}${unit}" >> "$LOG_FILE"          # 正确格式：409Mi
echo "物理内存使用率：${used_percentage}%" >> "$LOG_FILE"

# 6. 阈值判断（85%）
threshold=85.0
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "已用内存超过 ${threshold}%，正在清理缓存..." >> "$LOG_FILE"
    sync && echo 3 > /proc/sys/vm/drop_caches
    if [ $? -ne 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 清理缓存失败（权限不足或内核限制）" >> "$LOG_FILE"
    fi
else
    echo "未达到 ${threshold}%，无需清理。" >> "$LOG_FILE"
fi

# 记录执行完成
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 脚本执行完成" >> "$LOG_FILE"
echo "---------------------------" >> "$LOG_FILE"
