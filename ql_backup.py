#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/23 13:23
# -------------------------------
# cron "30 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙环境变量备份')

# ql_backup.py
import requests
import json
import os
import time
from git import Repo
from requests.exceptions import RequestException
from git.exc import GitCommandError

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
    "file_name": "env_backup.json"
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
    except RequestException as e:
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
    except RequestException as e:
        print(f"❌ 获取环境变量失败: {e}")
        return None


def backup_envs_to_repo(envs):
    """把环境变量备份到 GitHub 仓库"""
    if not os.path.exists(REPO_CONFIG["path"]):
        print("📥 首次运行，正在克隆仓库...")
        Repo.clone_from(REPO_CONFIG["repo_url"], REPO_CONFIG["path"])

    repo = Repo(REPO_CONFIG["path"])
    file_path = os.path.join(REPO_CONFIG["path"], REPO_CONFIG["file_name"])

    # 写入 JSON 文件
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(envs, f, ensure_ascii=False, indent=2)

    # 提交与推送
    try:
        if repo.is_dirty(untracked_files=True):
            repo.git.add(file_path)
            commit_msg = (
                f"Backup envs at {time.strftime('%Y-%m-%d %H:%M:%S')} | "
                f"共 {len(envs)} 条环境变量"
            )
            repo.git.commit("-m", commit_msg)
            repo.remote(name="origin").push()
            print(f"✅ 环境变量已备份到仓库，提交信息: {commit_msg}")
        else:
            print("ℹ️ 没有变化，跳过提交")
    except GitCommandError as e:
        print(f"❌ Git 操作失败: {e}")


if __name__ == "__main__":
    ql_token = get_ql_token()
    if not ql_token:
        exit(1)
    envs = get_ql_envs(ql_token)
    if envs:
        backup_envs_to_repo(envs)
