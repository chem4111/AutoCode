#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/9/23 13:23
# -------------------------------
# cron "35 8 * * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('青龙环境变量同步')



# ql_restore.py
import requests
import json
import os
from git import Repo
from requests.exceptions import RequestException

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


def load_envs_from_repo():
    """从 GitHub 仓库获取最新的 env_backup.json"""
    if not os.path.exists(REPO_CONFIG["path"]):
        print("📥 本地没有仓库，正在克隆...")
        Repo.clone_from(REPO_CONFIG["repo_url"], REPO_CONFIG["path"])

    repo = Repo(REPO_CONFIG["path"])
    print("🔄 拉取仓库最新内容...")
    repo.remote(name="origin").pull()

    file_path = os.path.join(REPO_CONFIG["path"], REPO_CONFIG["file_name"])
    if not os.path.exists(file_path):
        print("❌ 仓库里没有 env_backup.json")
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def restore_envs_to_ql(ql_token, envs):
    """把 GitHub 里的环境变量同步到青龙"""
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {"Authorization": f"Bearer {ql_token}", "Content-Type": "application/json"}

    # 清空旧的再添加（保险做法）
    try:
        print("🧹 清理青龙旧的环境变量...")
        requests.delete(url, headers=headers, timeout=10)
    except RequestException as e:
        print(f"⚠️ 清理旧变量失败: {e}")

    # 逐个写入
    success = 0
    for env in envs:
        try:
            payload = [env] if isinstance(env, dict) else env
            r = requests.post(url, headers=headers, json=payload, timeout=10)
            r.raise_for_status()
            success += 1
        except RequestException as e:
            print(f"❌ 添加变量失败: {e}")

    print(f"✅ 恢复完成，共写入 {success}/{len(envs)} 条变量")


if __name__ == "__main__":
    ql_token = get_ql_token()
    if not ql_token:
        exit(1)

    envs = load_envs_from_repo()
    if not envs:
        exit(1)

    restore_envs_to_ql(ql_token, envs)
