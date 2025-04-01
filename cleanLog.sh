#!/usr/bin/bash
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/4/1 13:23
# -------------------------------
# cron "30 0 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙日志清理')

#!/bin/bash
echo "开始清理日志"
pwd
# ls ../log
find ../log -mtime +10 -name "*.log"
find ../log -mtime +10 -name "*.log" -exec rm -rf {} \;
echo "清理日志完成"
