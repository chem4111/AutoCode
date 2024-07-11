#!/bin/bash

# 检查是否具有超级用户权限
if [ "$EUID" -ne 0 ]; then
    echo "请以根用户身份运行此脚本"
    exit 1
fi

# 更新包列表
echo "更新包列表..."
if command -v apt-get &> /dev/null; then
    apt-get update
else
    echo "apt-get 未安装"
fi

# 清理APT缓存
echo "清理APT缓存..."
if command -v apt-get &> /dev/null; then
    apt-get clean
else
    echo "apt-get 未安装"
fi

# 清理无用的依赖包
echo "清理无用的依赖包..."
if command -v apt-get &> /dev/null; then
    apt-get autoremove -y
else
    echo "apt-get 未安装"
fi

# 清理旧版本的包文件
echo "清理旧版本的包文件..."
if command -v apt-get &> /dev/null; then
    apt-get autoclean
else
    echo "apt-get 未安装"
fi

# 清理系统日志
echo "清理系统日志..."
if command -v journalctl &> /dev/null; then
    journalctl --vacuum-time=2weeks
else
    echo "journalctl 未安装"
fi

# 清理孤立包
echo "清理孤立包..."
if command -v deborphan &> /dev/null; then
    orphans=$(deborphan)
    if [ -n "$orphans" ]; then
        echo "找到孤立的包:"
        echo "$orphans"
        apt-get -y remove --purge $(deborphan)
    else
        echo "没有找到孤立的包."
    fi
else
    echo "deborphan 未安装"
fi

# 清理残留的配置文件
echo "清理残留的配置文件..."
if command -v dpkg &> /dev/null; then
    dpkg -l | awk '/^rc/ {print $2}' | xargs apt-get purge -y
else
    echo "dpkg 未安装"
fi

# 清理用户缓存
echo "清理用户缓存..."
rm -rf ~/.cache/thumbnails/*
rm -rf ~/.cache/mozilla/firefox/*.default-release/cache2/*

# 使用BleachBit进行更深层次的清理
echo "使用BleachBit进行更深层次的清理..."
if command -v bleachbit &> /dev/null; then
    apt-get install -y bleachbit
    bleachbit --clean system.*
else
    echo "bleachbit 未安装"
fi

# 清理Docker镜像和容器
echo "清理Docker镜像和容器..."
if command -v docker &> /dev/null; then
    docker system prune -af
else
    echo "docker 未安装"
fi

# 提示完成
echo "系统清理完成！"
