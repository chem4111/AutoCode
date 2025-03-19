#!/bin/bash

# 从 /proc/meminfo 中读取总内存和空闲内存
total_memory=$(grep 'MemTotal:' /proc/meminfo | awk '{print $2}')
free_memory=$(grep 'MemFree:' /proc/meminfo | awk '{print $2}')

# 计算已使用的内存
used_memory=$((total_memory - free_memory))

# 计算已使用内存的百分比
used_percentage=$(echo "scale=2; ($used_memory / $total_memory) * 100" | bc)

# 设定阈值为 85%
threshold=85

# 判断是否超过阈值
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    # 同步数据到磁盘并清理缓存
    sync && echo 3 > /proc/sys/vm/drop_caches
    echo "物理内存已用率达到 $used_percentage%，已清理缓存。"
else
    echo "物理内存已用率为 $used_percentage%，未达到 $threshold%，无需清理。"
fi
    
