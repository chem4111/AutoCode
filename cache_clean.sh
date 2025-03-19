#!/bin/bash

# 从 /proc/meminfo 中获取总内存
total_memory=$(grep 'MemTotal:' /proc/meminfo | awk '{print $2}')
# 从 /proc/meminfo 中获取可用内存
available_memory=$(grep 'MemAvailable:' /proc/meminfo | awk '{print $2}')

# 计算真实内存使用率
used_percentage=$(echo "scale=2; (1 - $available_memory / $total_memory) * 100" | bc)

# 设定清理缓存的阈值（这里设为 85%）
threshold=85

# 判断真实内存使用率是否超过阈值
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    # 同步数据到磁盘并清理缓存
    sync && echo 3 > /proc/sys/vm/drop_caches
    echo "真实物理内存使用率达到 $used_percentage%，已清理缓存。"
else
    echo "真实物理内存使用率为 $used_percentage%，未达到 $threshold%，无需清理。"
fi
    
