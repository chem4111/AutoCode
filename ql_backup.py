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

# ================== 配置区 ==================
QL_CONFIG = {
    "url": "http://127.0.0.1:5700",       # 青龙面板地址
    "client_id": "QYWVF1968Um_",          # 替换为你自己的
    "client_secret": "YmpfcuGoTUf3-8r7ywRh3kTz"
}

REPO_CONFIG = {
    "path": "./ql-env-backup",
    "repo_url": "https://back-cat:7cf2cfaa02fe518146e02648bdd63736@gitee.com/back-cat/ql-env-backup.git",
    "file_name": "env_backup.json",
    "branch": "master"
}
# ================== 配置区 ==================


def get_ql_token():
    url = f"{QL_CONFIG['url']}/open/auth/token"
    params = {"client_id": QL_CONFIG["client_id"], "client_secret": QL_CONFIG["client_secret"]}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        token = resp.json().get("data", {}).get("token")
        if not token:
            print(f"❌ 获取 token 失败: {resp.text}")
        return token
    except Exception as e:
        print(f"❌ 获取青龙令牌失败: {e}")


def get_ql_envs(ql_token):
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {"Authorization": f"Bearer {ql_token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("data", [])
    except Exception as e:
        print(f"❌ 获取环境变量失败: {e}")
        return []


def run_git(cmd_list, cwd=None, allow_fail=False):
    try:
        subprocess.run(["git", "-c", "http.version=HTTP/1.1"] + cmd_list, cwd=cwd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        if allow_fail:
            return False
        print(f"❌ Git 命令失败: {' '.join(cmd_list)}\n  {e}")
        sys.exit(1)


def has_upstream(repo_path):
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

    if not os.path.exists(repo_path):
        print("📥 首次运行，正在克隆仓库...")
        run_git(["clone", "--depth=1", "-b", branch, repo_url, repo_path])

    head_file = os.path.join(repo_path, ".git", "HEAD")
    is_empty_repo = not os.path.exists(head_file)

    if not is_empty_repo:
        run_git(["checkout", "-B", branch], cwd=repo_path)
        run_git(["pull", "origin", branch, "--allow-unrelated-histories"], cwd=repo_path, allow_fail=True)

    # 写入 JSON 文件
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

    print(f"✅ 环境变量已备份到 Gitee 仓库，提交信息: {commit_msg}")


if __name__ == "__main__":
    ql_token = get_ql_token()
    if not ql_token:
        sys.exit(1)

    envs = get_ql_envs(ql_token)
    if not envs:
        print("⚠️ 没有获取到任何环境变量，跳过备份。")
        sys.exit(0)

    backup_envs_to_repo(envs)
