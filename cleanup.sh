#!/bin/bash

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

# 提示完成
echo "系统清理完成！"

