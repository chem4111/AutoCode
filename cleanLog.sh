#!/bin/bash
# -- coding: utf-8 --
# -------------------------------
# @Author : 青龙日志清理（只保留7天）
# @Time : 2025/9/23 13:23
# -------------------------------
# cron "0 0 1 * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙日志清理-保留7天')

LOG_DIR="/ql/log"
KEEP_DAYS=7  # 只保留最近7天的日志

echo "开始清理青龙日志（只保留最近${KEEP_DAYS}天）"
echo "当前目录: $(pwd)"

# 检查日志目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "错误：日志目录 $LOG_DIR 不存在。"
    exit 1
fi

# 1. 删除7天前的所有日志文件（包括.log和.log.gz）
echo "删除${KEEP_DAYS}天前的所有日志文件..."
find "$LOG_DIR" -name "*.log" -type f -mtime +$KEEP_DAYS -delete 2>/dev/null
find "$LOG_DIR" -name "*.log.gz" -type f -mtime +$KEEP_DAYS -delete 2>/dev/null

# 2. 清理空目录（兼容BusyBox版本）
echo "清理空目录..."
find "$LOG_DIR" -type d -exec rmdir {} \; 2>/dev/null || true

# 3. 显示清理结果
echo "清理完成！当前日志文件统计："
find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l | xargs echo "当前日志文件数量："
find "$LOG_DIR" -name "*.log.gz" -type f 2>/dev/null | wc -l | xargs echo "压缩日志文件数量："
du -sh "$LOG_DIR" 2>/dev/null | awk '{print "日志目录总大小：" $1}'

# 4. 显示最老的日志文件日期（用于验证）
oldest_file=$(find "$LOG_DIR" -name "*.log" -type f -exec ls -lt {} + 2>/dev/null | tail -1 | awk '{print $6, $7, $8}' || echo "无日志文件")
echo "最老日志文件日期：$oldest_file"

echo "日志清理完成（只保留最近${KEEP_DAYS}天）"
