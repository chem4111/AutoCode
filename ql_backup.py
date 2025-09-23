#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://gitee.com/chem4111/AutoCode/
# @Time   : 2025/9/23
# -------------------------------
# 功能：备份青龙环境变量到 Gitee
# 执行：可直接在青龙定时任务里运行

import requests
import json
import os
import time
import subprocess
import sys

# ================== 从环境变量获取配置 ==================
QL_CONFIG = {
    "url": os.getenv('QL_URL', 'http://127.0.0.1:5700'),       # 青龙面板地址
    "client_id": os.getenv('QL_CLIENT_ID'),                    # 从环境变量获取
    "client_secret": os.getenv('QL_CLIENT_SECRET')             # 从环境变量获取
}

REPO_CONFIG = {
    "path": os.getenv('BACKUP_PATH', './ql-env-backup'),
    "repo_url": os.getenv('GITEE_REPO_URL'),                   # 从环境变量获取
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
    
    # 检查Gitee仓库URL格式
    repo_url = REPO_CONFIG["repo_url"]
    if not repo_url or "gitee.com" not in repo_url:
        print("❌ Gitee仓库地址格式不正确")
        return False
        
    print("✅ 环境变量配置检查通过")
    return True


def get_ql_token():
    """获取青龙面板的访问令牌"""
    url = f"{QL_CONFIG['url']}/open/auth/token"
    params = {"client_id": QL_CONFIG["client_id"], "client_secret": QL_CONFIG["client_secret"]}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        token = resp.json().get("data", {}).get("token")
        if not token:
            print(f"❌ 获取token失败: {resp.text}")
            return None
        print("✅ 成功获取青龙令牌")
        return token
    except Exception as e:
        print(f"❌ 获取青龙令牌失败: {e}")
        return None


def get_ql_envs(ql_token):
    """获取青龙面板的所有环境变量"""
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {"Authorization": f"Bearer {ql_token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        envs = resp.json().get("data", [])
        print(f"✅ 成功获取 {len(envs)} 个环境变量")
        return envs
    except Exception as e:
        print(f"❌ 获取环境变量失败: {e}")
        return []


def run_git(cmd_list, cwd=None, allow_fail=False):
    """执行Git命令"""
    try:
        subprocess.run(["git", "-c", "http.version=HTTP/1.1"] + cmd_list, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        if allow_fail:
            return False
        print(f"❌ Git命令失败: {' '.join(cmd_list)}\n  {e}")
        sys.exit(1)


def has_upstream(repo_path):
    """检查是否有上游分支"""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.returncode == 0


def backup_envs_to_repo(envs):
    """备份环境变量到Git仓库"""
    repo_path = REPO_CONFIG["path"]
    repo_url = REPO_CONFIG["repo_url"]
    file_name = REPO_CONFIG["file_name"]
    branch = REPO_CONFIG["branch"]

    if not os.path.exists(repo_path):
        print("📥 首次运行，正在克隆仓库...")
        run_git(["clone", "--depth=1", "-b", branch, repo_url, repo_path])

    head_file = os.path.join(repo_path, ".git", "HEAD")
    is_empty_repo = not os.path.exists(head_file)

    if not is_empty_repo:
        run_git(["checkout", "-B", branch], cwd=repo_path)
        run_git(["pull", "origin", branch, "--allow-unrelated-histories"], cwd=repo_path, allow_fail=True)

    # 写入JSON文件
    file_path = os.path.join(repo_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(envs, f, ensure_ascii=False, indent=2)

    # 提交
    run_git(["add", file_name], cwd=repo_path)
    commit_msg = f"Backup envs at {time.strftime('%Y-%m-%d %H:%M:%S')} | 共 {len(envs)} 条环境变量"
    run_git(["commit", "-m", commit_msg], cwd=repo_path, allow_fail=True)

    if is_empty_repo or not has_upstream(repo_path):
        run_git(["push", "--set-upstream", "origin", branch], cwd=repo_path)
    else:
        run_git(["push"], cwd=repo_path)

    print(f"✅ 环境变量已备份到Gitee仓库，提交信息: {commit_msg}")


if __name__ == "__main__":
    # 检查环境变量配置
    if not check_config():
        sys.exit(1)

    # 获取青龙令牌
    ql_token = get_ql_token()
    if not ql_token:
        sys.exit(1)

    # 获取环境变量
    envs = get_ql_envs(ql_token)
    if not envs:
        print("⚠️ 没有获取到任何环境变量，跳过备份。")
        sys.exit(0)

    # 备份到仓库
    backup_envs_to_repo(envs)
