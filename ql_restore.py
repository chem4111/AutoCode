#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/23 13:23
# -------------------------------
# cron "35 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙环境变量同步')

# ql_restore_gitee.py
import requests
import json
import os
import sys
from git import Repo
from requests.exceptions import RequestException

# ================== 从环境变量获取配置（与备份脚本保持一致） ==================
QL_CONFIG = {
    "url": os.getenv('QL_URL', 'http://127.0.0.1:5700'),
    "client_id": os.getenv('QL_CLIENT_ID'),
    "client_secret": os.getenv('QL_CLIENT_SECRET')
}

REPO_CONFIG = {
    "path": os.getenv('BACKUP_PATH', './ql-env-backup'),
    "repo_url": os.getenv('GITEE_REPO_URL'),
    "file_name": os.getenv('BACKUP_FILE_NAME', 'env_backup.json'),
    "branch": os.getenv('GIT_BRANCH', 'master')
}
# ================== 配置区 ==================


def check_config():
    """检查必要的环境变量是否配置"""
    required_envs = ['QL_CLIENT_ID', 'QL_CLIENT_SECRET', 'GITEE_REPO_URL']
    missing_envs = []
    
    for env in required_envs:
        if not os.getenv(env):
            missing_envs.append(env)
    
    if missing_envs:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_envs)}")
        print("请在青龙面板的环境变量中配置以下变量:")
        print("QL_CLIENT_ID: 青龙应用的Client ID")
        print("QL_CLIENT_SECRET: 青龙应用的Client Secret") 
        print("GITEE_REPO_URL: Gitee仓库地址（包含token）")
        return False
    
    print("✅ 环境变量配置检查通过")
    return True


def get_ql_token():
    """获取青龙面板 API 令牌"""
    url = f"{QL_CONFIG['url']}/open/auth/token"
    params = {
        "client_id": QL_CONFIG["client_id"],
        "client_secret": QL_CONFIG["client_secret"]
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json().get("data", {})
        token = data.get("token")
        if not token:
            print("❌ 获取青龙令牌失败: 响应中未找到token")
            return None
        print("✅ 成功获取青龙令牌")
        return token
    except Exception as e:
        print(f"❌ 获取青龙令牌失败: {e}")
        return None


def load_envs_from_repo():
    """从 Gitee 仓库获取最新的 env_backup.json"""
    repo_path = REPO_CONFIG["path"]
    repo_url = REPO_CONFIG["repo_url"]
    file_name = REPO_CONFIG["file_name"]
    branch = REPO_CONFIG["branch"]
    
    if not os.path.exists(repo_path):
        print("📥 本地没有仓库，正在克隆...")
        try:
            Repo.clone_from(repo_url, repo_path, branch=branch)
            print("✅ 仓库克隆成功")
        except Exception as e:
            print(f"❌ 克隆仓库失败: {e}")
            return None

    try:
        repo = Repo(repo_path)
        print("🔄 拉取仓库最新内容...")
        origin = repo.remote(name="origin")
        origin.pull(branch)
        print("✅ 仓库更新成功")
    except Exception as e:
        print(f"⚠️ 拉取更新失败: {e}")
        # 继续尝试读取本地文件

    file_path = os.path.join(repo_path, file_name)
    if not os.path.exists(file_path):
        print(f"❌ 仓库里没有找到 {file_name}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            envs = json.load(f)
        print(f"✅ 成功加载 {len(envs)} 条环境变量")
        return envs
    except Exception as e:
        print(f"❌ 读取环境变量文件失败: {e}")
        return None


def restore_envs_to_ql(ql_token, envs):
    """把 Gitee 仓库里的环境变量同步到青龙"""
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {
        "Authorization": f"Bearer {ql_token}", 
        "Content-Type": "application/json"
    }

    # 先获取当前的环境变量
    try:
        print("📋 获取当前环境变量...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        current_envs = response.json().get("data", [])
        print(f"当前有 {len(current_envs)} 条环境变量")
    except Exception as e:
        print(f"❌ 获取当前环境变量失败: {e}")
        return False

    # 删除所有现有环境变量
    if current_envs:
        print("🧹 清理旧的环境变量...")
        try:
            # 构建删除请求
            env_ids = [env["id"] for env in current_envs if "id" in env]
            if env_ids:
                delete_url = f"{QL_CONFIG['url']}/open/envs"
                delete_data = env_ids
                response = requests.delete(delete_url, headers=headers, json=delete_data, timeout=10)
                response.raise_for_status()
                print("✅ 旧环境变量清理完成")
        except Exception as e:
            print(f"❌ 清理环境变量失败: {e}")
            return False

    # 批量添加新的环境变量
    print("📤 添加新的环境变量...")
    success_count = 0
    
    # 分批处理，避免请求过大
    batch_size = 10
    for i in range(0, len(envs), batch_size):
        batch = envs[i:i + batch_size]
        try:
            # 清理每个环境变量对象，移除id字段（如果有的话）
            clean_batch = []
            for env in batch:
                clean_env = env.copy()
                clean_env.pop('id', None)  # 移除id字段
                clean_env.pop('created', None)  # 移除创建时间字段
                clean_env.pop('updated', None)  # 移除更新时间字段
                clean_env.pop('status', None)  # 移除状态字段
                clean_batch.append(clean_env)
            
            response = requests.post(url, headers=headers, json=clean_batch, timeout=10)
            response.raise_for_status()
            success_count += len(clean_batch)
            print(f"✅ 已添加 {success_count}/{len(envs)} 条变量")
        except Exception as e:
            print(f"❌ 批量添加变量失败（跳过该批次）: {e}")
            continue

    print(f"🎉 恢复完成！成功添加 {success_count}/{len(envs)} 条环境变量")
    return success_count > 0


if __name__ == "__main__":
    print("🚀 开始从Gitee恢复青龙环境变量...")
    
    # 检查环境变量配置
    if not check_config():
        sys.exit(1)

    # 获取青龙令牌
    ql_token = get_ql_token()
    if not ql_token:
        print("❌ 无法获取青龙令牌，恢复终止")
        sys.exit(1)

    # 从仓库加载环境变量
    envs = load_envs_from_repo()
    if not envs:
        print("❌ 无法从仓库加载环境变量，恢复终止")
        sys.exit(1)

    # 恢复到青龙
    if restore_envs_to_ql(ql_token, envs):
        print("✅ 环境变量恢复成功！")
    else:
        print("❌ 环境变量恢复失败")
        sys.exit(1)
