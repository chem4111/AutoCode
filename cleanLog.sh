#!/bin/bash
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/4/1 13:23
# -------------------------------
# cron "30 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙日志清理')

# 定义日志目录
LOG_DIR="../log"

echo "开始清理日志"
pwd

# 检查日志目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "错误：日志目录 $LOG_DIR 不存在。"
    exit 1
fi

# 查找要删除的日志文件
LOG_FILES=$(find "$LOG_DIR" -name "*.log")

if [ -z "$LOG_FILES" ]; then
    echo "没有找到日志文件，无需清理。"
else
    # 输出要删除的日志文件列表
    echo "即将删除以下日志文件："
    echo "$LOG_FILES"

    # 删除日志文件
    if find "$LOG_DIR" -name "*.log" -exec rm -rf {} \; ; then
        echo "日志文件删除成功。"
    else
        echo "错误：删除日志文件时出现问题。"
        exit 1
    fi
fi

echo "清理日志完成"    
