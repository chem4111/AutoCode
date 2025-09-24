#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/23 13:23
# -------------------------------
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
    """更新或新增环境变量"""
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {
        "Authorization": f"Bearer {ql_token}",
        "Content-Type": "application/json"
    }

    # 获取当前变量
    try:
        print("📋 获取当前环境变量...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        current_envs = response.json().get("data", [])
        print(f"当前有 {len(current_envs)} 条环境变量")
    except Exception as e:
        print(f"❌ 获取当前环境变量失败: {e}")
        return False

    # 构建字典 {变量名: {id/_id, value, remarks}}
    current_envs_dict = {
        env["name"]: env for env in current_envs if "name" in env
    }

    print("📤 开始同步环境变量...")
    success_count = 0
    for env in envs:
        clean_env = {
            "name": env.get("name"),
            "value": env.get("value"),
            "remarks": env.get("remarks", "")
        }

        if clean_env["name"] in current_envs_dict:
            # 已存在 → 更新
            env_info = current_envs_dict[clean_env["name"]]
            env_id = env_info.get("id") or env_info.get("_id")
            if not env_id:
                print(f"⚠️ 跳过更新，未找到 id: {clean_env['name']}")
                continue
            try:
                put_url = f"{url}/{env_id}"
                response = requests.put(put_url, headers=headers, json=clean_env, timeout=10)
                response.raise_for_status()
                success_count += 1
                print(f"🔄 已更新: {clean_env['name']}")
            except Exception as e:
                print(f"❌ 更新失败: {clean_env} | 错误: {e}")
        else:
            # 不存在 → 新增
            try:
                response = requests.post(url, headers=headers, json=[clean_env], timeout=10)
                response.raise_for_status()
                success_count += 1
                print(f"➕ 已新增: {clean_env['name']}")
            except Exception as e:
                print(f"❌ 新增失败: {clean_env} | 错误: {e}")

    print(f"🎉 同步完成！成功处理 {success_count}/{len(envs)} 条环境变量")
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
        print("✅ 环境变量同步成功！")
    else:
        print("❌ 环境变量同步失败")
        sys.exit(1)
