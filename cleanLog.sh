#!/bin/bash
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/4/1 13:23
# -------------------------------
# cron "0 0 1 * *" script-path=xxx.sh,tag=匹配cron用
# const $ = new Env('青龙日志清理')


#每月 1 日凌晨 0 点运行一次。

# 定义日志目录
LOG_DIR="/ql/log"

echo "开始清理日志"
pwd

# 检查日志目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "错误：日志目录 $LOG_DIR 不存在。"
    exit 1
fi

# 尝试更改文件权限
chmod -R 777 "$LOG_DIR"

# 查找所有文件并尝试删除
if find "$LOG_DIR" -type f -exec rm -f {} +; then
    echo "日志文件删除成功。"
else
    echo "错误：删除日志文件时出现问题。"
    # 尝试找出占用文件的进程
    lsof +D "$LOG_DIR"
    exit 1
fi

# 删除空目录
find "$LOG_DIR" -type d -empty -delete

echo "清理日志完成"
    
