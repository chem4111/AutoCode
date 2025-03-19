#!/bin/bash
mem_free=$(grep 'MemFree:' /proc/meminfo | awk '{print $2}')  # 单位：KB
threshold=50000  # 50MB（根据需求调整）

if [ "$mem_free" -lt "$threshold" ]; then
    echo "警告：空闲内存不足（$mem_free KB < $threshold KB）"
    # 可选：清理缓存（仅作为临时措施）
    sync && echo 3 > /proc/sys/vm/drop_caches
else
    echo "内存状态正常：空闲 $mem_free KB"
fi
