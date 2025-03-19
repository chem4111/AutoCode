#!/bin/bash

# 使用 free -h 获取内存数据并解析
free_output=$(free -h | grep Mem)

# 从输出中提取总内存、空闲内存等信息
total_mem=$(echo $free_output | awk '{print $2}' | sed 's/Mi//')
free_mem=$(echo $free_output | awk '{print $4}' | sed 's/Mi//')

# 计算已使用内存
used_mem=$((total_mem - free_mem))

# 计算物理内存使用百分比
used_percentage=$(echo "scale=2; $used_mem / $total_mem * 100" | bc)

# 输出内存使用情况
echo "物理内存总计：$total_mem Mi"
echo "空闲内存：$free_mem Mi"
echo "已用内存：$used_mem Mi"
echo "物理内存使用率：$used_percentage%"

# 设置阈值，判断是否清理缓存
threshold=85.0
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "已用内存超过 $threshold%，正在清理缓存..."
    sync; echo 3 > /proc/sys/vm/drop_caches
else
    echo "未达到 $threshold%，无需清理。"
fi
