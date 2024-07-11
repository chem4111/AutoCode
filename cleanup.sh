#!/bin/bash

# 更新包列表
echo "更新包列表..."
sudo apt-get update

# 清理APT缓存
echo "清理APT缓存..."
sudo apt-get clean

# 清理无用的依赖包
echo "清理无用的依赖包..."
sudo apt-get autoremove -y

# 清理旧版本的包文件
echo "清理旧版本的包文件..."
sudo apt-get autoclean

# 清理系统日志
echo "清理系统日志..."
sudo journalctl --vacuum-time=2weeks

# 清理孤立包
echo "清理孤立包..."
orphans=$(deborphan)
if [ -n "$orphans" ]; then
    echo "找到孤立的包:"
    echo "$orphans"
    sudo apt-get -y remove --purge $(deborphan)
else
    echo "没有找到孤立的包."
fi

# 清理残留的配置文件
echo "清理残留的配置文件..."
sudo dpkg -l | awk '/^rc/ {print $2}' | xargs sudo apt-get purge -y

# 清理用户缓存
echo "清理用户缓存..."
rm -rf ~/.cache/thumbnails/*
rm -rf ~/.cache/mozilla/firefox/*.default-release/cache2/*

# 使用BleachBit进行更深层次的清理
echo "使用BleachBit进行更深层次的清理..."
sudo apt-get install -y bleachbit
sudo bleachbit --clean system.*

# 清理Docker镜像和容器
echo "清理Docker镜像和容器..."
docker system prune -af

# 提示完成
echo "系统清理完成！"
