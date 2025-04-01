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

# 直接删除日志文件
if find "$LOG_DIR" -name "*.log" -exec rm -f {} +; then
    echo "日志文件删除成功。"
else
    echo "错误：删除日志文件时出现问题。"
    exit 1
fi

echo "清理日志完成"    
