#!/bin/bash

# 提取 total 和 free 的值
mem_line=$(free -h | grep 'Mem:')
total_mem=$(echo "$mem_line" | awk '{print $2}')  # 提取总内存（含单位 Mi）
free_mem=$(echo "$mem_line" | awk '{print $4}')    # 提取空闲内存（含单位 Mi）

# 去除单位，转换为纯数字
total_num=$(echo "$total_mem" | sed 's/Mi//')
free_num=$(echo "$free_mem" | sed 's/Mi//')

# 计算已用内存
used_mem=$((total_num - free_num))

# 计算使用率
used_percentage=$(echo "scale=2; $used_mem / $total_num * 100" | bc)

# 输出内存信息
echo "物理内存总计：$total_mem"
echo "空闲内存：$free_mem"
echo "已用内存：${used_mem}Mi"
echo "物理内存使用率：${used_percentage}%"

# 设定阈值并判断清理
threshold=85
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "已用内存超过 ${threshold}%，正在清理缓存..."
    sync && echo 3 > /proc/sys/vm/drop_caches
else
    echo "未达到 ${threshold}%，无需清理。"
fi
