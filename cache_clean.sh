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

# 输出当前内存使用情况
echo "## 开始执行... $(date '+%Y-%m-%d %H:%M:%S')"
echo "物理内存使用率为 $used_percentage%，"

# 判断是否超过阈值，如果是则清理缓存
if (( $(echo "$used_percentage > $threshold" | bc -l) )); then
    echo "已用内存超过 $threshold%，正在清理缓存..."
    sync; echo 3 > /proc/sys/vm/drop_caches
else
    echo "未达到 $threshold%，无需清理。"
fi

# 执行结束输出
echo "## 执行结束... $(date '+%Y-%m-%d %H:%M:%S') 耗时 1 秒"
