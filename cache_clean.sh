#!/bin/bash

# 定义日志文件
LOG_FILE="/root/cache_clean.log"  

# 记录执行时间和状态
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始执行缓存清理脚本" >> "$LOG_FILE"

# 原有脚本逻辑（读取内存、计算使用率、清理缓存）
total_mem=$(free -h | grep 'Mem:' | awk '{print $2}')
free_mem=$(free -h | grep 'Mem:' | awk '{print $4}')
used_mem=$((total_mem - free_mem))  # 假设单位为 MiB（需根据实际情况调整）
used_percentage=$(echo "scale=2; $used_mem / $total_mem * 100" | bc)

echo "物理内存总计：$total_mem Mi" >> "$LOG_FILE"
echo "空闲内存：$free_mem Mi" >> "$LOG_FILE"
echo "已用内存：$used_mem Mi" >> "$LOG_FILE"
echo "物理内存使用率：$used_percentage%" >> "$LOG_FILE"

threshold=85.0
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "已用内存超过 $threshold%，正在清理缓存..." >> "$LOG_FILE"
    sync; echo 3 > /proc/sys/vm/drop_caches
else
    echo "未达到 $threshold%，无需清理。" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 脚本执行完成" >> "$LOG_FILE"
echo "---------------------------" >> "$LOG_FILE"
