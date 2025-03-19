#!/bin/bash

# 获取总内存和空闲内存信息
total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
free_mem=$(grep MemFree /proc/meminfo | awk '{print $2}')

# 计算已使用的内存
used_mem=$((total_mem - free_mem))

# 计算内存使用百分比
used_percentage=$(echo "scale=2; $used_mem / $total_mem * 100" | bc)

# 输出内存使用情况
echo "物理内存总计：$((total_mem / 1024)) MB"
echo "空闲内存：$((free_mem / 1024)) MB"
echo "已用内存：$((used_mem / 1024)) MB"
echo "物理内存使用率：$used_percentage%"

# 设置阈值，判断是否清理缓存
threshold=85.0
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "已用内存超过 $threshold%，正在清理缓存..."
    sync; echo 3 > /proc/sys/vm/drop_caches
else
    echo "未达到 $threshold%，无需清理。"
fi
