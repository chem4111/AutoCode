#!/bin/bash

# 获取系统总内存和缓存使用情况
total_memory=$(free -m | awk 'NR==2 {print $2}')
cached_memory=$(free -m | awk 'NR==2 {print $6}')

# 计算缓存使用率
cache_usage=$(echo "scale=2; $cached_memory / $total_memory * 100" | bc)

# 判断缓存使用率是否大于 85%
if (( $(echo "$cache_usage > 85" | bc -l) )); then
    # 同步数据到磁盘并清理缓存
    sync && echo 3 > /proc/sys/vm/drop_caches
    echo "缓存使用率达到 $cache_usage%，已清理缓存。"
else
    echo "缓存使用率为 $cache_usage%，未达到 85%，无需清理。"
fi    
