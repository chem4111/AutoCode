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

# ================== 从环境变量获取配置 ==================
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
# =======================================================


def check_config():
    """检查必要的环境变量是否配置"""
    required_envs = ['QL_CLIENT_ID', 'QL_CLIENT_SECRET', 'GITEE_REPO_URL']
    missing_envs = [env for env in required_envs if not os.getenv(env)]
    
    if missing_envs:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_envs)}")
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
    """逐条写入环境变量"""
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {
        "Authorization": f"Bearer {ql_token}",
        "Content-Type": "application/json"
    }

    # 获取当前变量并清理
    try:
        print("📋 获取当前环境变量...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        current_envs = response.json().get("data", [])
        print(f"当前有 {len(current_envs)} 条环境变量")
    except Exception as e:
        print(f"❌ 获取当前环境变量失败: {e}")
        return False

    if current_envs:
        print("🧹 清理旧的环境变量...")
        try:
            env_ids = [env["id"] for env in current_envs if "id" in env]
            if env_ids:
                delete_url = f"{QL_CONFIG['url']}/open/envs"
                response = requests.delete(delete_url, headers=headers, json=env_ids, timeout=10)
                response.raise_for_status()
                print("✅ 旧环境变量清理完成")
        except Exception as e:
            print(f"❌ 清理环境变量失败: {e}")
            return False

    # 逐条添加
    print("📤 添加新的环境变量...")
    success_count = 0
    for env in envs:
        clean_env = {
            "name": env.get("name"),
            "value": env.get("value"),
            "remarks": env.get("remarks", "")
        }
        try:
            response = requests.post(url, headers=headers, json=[clean_env], timeout=10)
            response.raise_for_status()
            success_count += 1
            print(f"✅ 已添加 {success_count}/{len(envs)} 条变量: {clean_env['name']}")
        except Exception as e:
            print(f"❌ 添加失败: {clean_env} | 错误: {e}")
            continue

    print(f"🎉 恢复完成！成功添加 {success_count}/{len(envs)} 条环境变量")
    return success_count > 0


if __name__ == "__main__":
    print("🚀 开始从Gitee恢复青龙环境变量...")
    
    if not check_config():
        sys.exit(1)

    ql_token = get_ql_token()
    if not ql_token:
        sys.exit(1)

    envs = load_envs_from_repo()
    if not envs:
        sys.exit(1)

    if restore_envs_to_ql(ql_token, envs):
        print("✅ 环境变量恢复成功！")
    else:
        print("❌ 环境变量恢复失败")
        sys.exit(1)
