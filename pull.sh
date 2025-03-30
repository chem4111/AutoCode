#!/bin/bash

# 源脚本目录
SOURCE_DIR="/ql/scripts"

# GitHub 仓库目录
REPO_DIR="$HOME"

# 进入仓库目录
cd "$REPO_DIR"

# 检查文件是否有修改
if ! git diff --quiet || ! git diff --cached --quiet; then
    # 添加文件到暂存区
    git add .
    # 提交更改
    git commit -m "Add or update script files"
    # 推送到远程仓库
    git push origin main
    echo "脚本文件已成功拷贝并提交到 GitHub 仓库。"
else
    echo "没有文件修改，无需提交。"
fi   
