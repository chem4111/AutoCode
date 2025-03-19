#!/bin/bash

# 获取总内存和空闲内存信息
total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
free_mem=$(grep MemFree /proc/meminfo | awk '{print $2}')
buffers_mem=$(grep Buffers /proc/meminfo | awk '{print $2}')
cached_mem=$(grep Cached /proc/meminfo | awk '{print $2}')

# 计算已使用的物理内存（不包括缓存和缓冲区）
used_mem=$((total_mem - free_mem - buffers_mem - cached_mem))

# 计算已使用内存百分比
used_percentage=$(echo "scale=2; $used_mem / $total_mem * 100" | bc)

# 设置阈值
threshold=85.0

# 判断是否超过阈值，如果是则清理缓存
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "Memory usage is over 85%, clearing cache..."
    sync; echo 3 > /proc/sys/vm/drop_caches
else
    echo "Memory usage is below 85%, no need to clear cache."
fi
