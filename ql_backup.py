#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time   : 2025/9/23 13:23
# -------------------------------
# cron "30 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙环境变量备份')

import requests
import json
import os
import time
import subprocess

# 使用前先导出 GitHub PAT:
# export GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxxxxxx

QL_CONFIG = {
    "url": "http://127.0.0.1:5700",
    "client_id": "QYWVF1968Um_",
    "client_secret": "YmpfcuGoTUf3-8r7ywRh3kTz"
}

# 读取 GitHub PAT
GITHUB_PAT = os.getenv("GITHUB_PAT")
if not GITHUB_PAT:
    raise RuntimeError("❌ 未设置 GITHUB_PAT 环境变量，请先执行: export GITHUB_PAT=xxxx")

REPO_CONFIG = {
    "path": "./ql-env-backup",
    "repo_url": f"https://chem4111:{GITHUB_PAT}@github.com/chem4111/ql-env-backup.git",
    "file_name": "env_backup.json",
    "branch": "main"
}


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
        data = response.json()["data"]
        return data["token"]
    except requests.RequestException as e:
        print(f"❌ 获取青龙令牌失败: {e}")
        return None


def get_ql_envs(ql_token):
    """获取青龙环境变量"""
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {"Authorization": f"Bearer {ql_token}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["data"]
    except requests.RequestException as e:
        print(f"❌ 获取环境变量失败: {e}")
        return None


def run_git(cmd_list, cwd=None):
    """执行 git 命令，强制 HTTP/1.1"""
    try:
        subprocess.run(["git", "-c", "http.version=HTTP/1.1"] + cmd_list, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 命令失败: {' '.join(cmd_list)}\n  {e}")
        return False


def has_upstream(repo_path):
    """检查当前分支是否有 upstream"""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return result.returncode == 0


def backup_envs_to_repo(envs):
    repo_path = REPO_CONFIG["path"]
    repo_url = REPO_CONFIG["repo_url"]
    file_name = REPO_CONFIG["file_name"]
    branch = REPO_CONFIG["branch"]

    # 首次 clone
    if not os.path.exists(repo_path):
        print("📥 首次运行，正在克隆仓库...")
        if not run_git(["clone", "-b", branch, repo_url, repo_path]):
            return

    # 检查仓库状态
    head_file = os.path.join(repo_path, ".git", "HEAD")
    is_empty_repo = not os.path.exists(head_file)
    if is_empty_repo:
        print("⚠️ 仓库为空或没有有效分支，跳过 pull")
    else:
        # 切换本地到远程默认分支 main
        run_git(["checkout", "-B", branch], cwd=repo_path)
        # pull 并允许不同历史合并
        run_git(["pull", "origin", branch, "--allow-unrelated-histories"], cwd=repo_path)

    # 写入 JSON 文件
    file_path = os.path.join(repo_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(envs, f, ensure_ascii=False, indent=2)

    # 提交
    run_git(["add", file_name], cwd=repo_path)
    commit_msg = f"Backup envs at {time.strftime('%Y-%m-%d %H:%M:%S')} | 共 {len(envs)} 条环境变量"
    run_git(["commit", "-m", commit_msg], cwd=repo_path)

    # 推送
    if is_empty_repo or not has_upstream(repo_path):
        run_git(["push", "--set-upstream", "origin", branch], cwd=repo_path)
    else:
        run_git(["push"], cwd=repo_path)

    print(f"✅ 环境变量已备份到仓库，提交信息: {commit_msg}")


if __name__ == "__main__":
    ql_token = get_ql_token()
    if not ql_token:
        exit(1)
    envs = get_ql_envs(ql_token)
    if envs:
        backup_envs_to_repo(envs)
