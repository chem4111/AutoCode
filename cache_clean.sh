#!/bin/bash

# 获取总内存（KB）
mem_total=$(grep 'MemTotal:' /proc/meminfo | awk '{print $2}')

# 获取缓存（KB）
cache=$(grep 'Cache:' /proc/meminfo | awk '{print $2}')

# 计算缓存使用率（百分比）
cache_usage=$(( (cache * 100) / mem_total ))

echo "当前缓存使用率：$cache_usage%"

# 检查是否超过85%
if [ "$cache_usage" -gt 85 ]; then
    echo "清理缓存..."
    sync && echo 3 > /proc/sys/vm/drop_caches
    echo "缓存已清理。"
else
    echo "缓存使用率未超过85%，跳过清理。"
fi
