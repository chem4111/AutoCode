#!/bin/bash
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/24 13:23
# -------------------------------
# cron "0 0 1 * *" script-path=xxx.sh,tag=匹配cron用
# const $ = new Env('青龙日志清理改进版')

LOG_DIR="/ql/log"
BACKUP_DAYS=30  # 保留最近30天的日志
COMPRESS_DAYS=7 # 7天前的日志进行压缩

echo "开始智能清理青龙日志"
echo "当前目录: $(pwd)"

# 检查日志目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "错误：日志目录 $LOG_DIR 不存在。"
    exit 1
fi

# 1. 先压缩7天前的日志文件（保留原文件）
echo "压缩7天前的日志文件..."
find "$LOG_DIR" -name "*.log" -type f -mtime +$COMPRESS_DAYS -exec gzip {} \;

# 2. 删除30天前的压缩日志
echo "删除30天前的旧日志..."
find "$LOG_DIR" -name "*.log.gz" -type f -mtime +$BACKUP_DAYS -delete

# 3. 清理空目录（可选）
find "$LOG_DIR" -type d -empty -delete

# 4. 显示清理结果
echo "清理完成！当前日志文件统计："
find "$LOG_DIR" -name "*.log" -type f | wc -l | xargs echo "当前日志文件数量："
find "$LOG_DIR" -name "*.log.gz" -type f | wc -l | xargs echo "压缩日志文件数量："
du -sh "$LOG_DIR" | awk '{print "日志目录总大小：" $1}'

echo "智能日志清理完成"
