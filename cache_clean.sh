#!/bin/bash

# 获取总内存
total_memory=$(grep 'MemTotal:' /proc/meminfo | awk '{print $2}')
# 获取可用内存
available_memory=$(grep 'MemAvailable:' /proc/meminfo | awk '{print $2}')

# 计算实际内存使用率
used_percentage=$(echo "scale=2; (1 - $available_memory / $total_memory) * 100" | bc)

# 判断内存使用率是否大于 85%
if (( $(echo "$used_percentage > 85" | bc -l) )); then
    # 同步数据到磁盘并清理缓存
    sync && echo 3 > /proc/sys/vm/drop_caches
    echo "物理内存使用率达到 $used_percentage%，已清理缓存。"
else
    echo "物理内存使用率为 $used_percentage%，未达到 85%，无需清理。"
fi    
