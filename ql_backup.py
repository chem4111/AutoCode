# ql_backup.py
import requests
import json
import os
import time
from git import Repo
from requests.exceptions import RequestException
from git.exc import GitCommandError

QL_CONFIG = {
    "url": "http://127.0.0.1:5700",
    "client_id": "你的client_id",
    "client_secret": "你的client_secret"
}

REPO_CONFIG = {
    "path": "./ql-env-backup",
    "repo_url": "https://github.com/chem4111/ql-env-backup.git",
    "file_name": "env_backup.json"
}


def get_ql_token():
    url = f"{QL_CONFIG['url']}/open/auth/token"
    params = {
        "client_id": QL_CONFIG["client_id"],
        "client_secret": QL_CONFIG["client_secret"]
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()["data"]
        return data["token"]
    except RequestException as e:
        print(f"获取令牌失败: {e}")
        return None


def get_ql_envs(token):
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["data"]
    except RequestException as e:
        print(f"获取环境变量失败: {e}")
        return None


def backup_envs_to_repo(envs):
    if not os.path.exists(REPO_CONFIG["path"]):
        Repo.clone_from(REPO_CONFIG["repo_url"], REPO_CONFIG["path"])

    repo = Repo(REPO_CONFIG["path"])
    file_path = os.path.join(REPO_CONFIG["path"], REPO_CONFIG["file_name"])

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(envs, f, ensure_ascii=False, indent=2)

    try:
        if repo.is_dirty(untracked_files=True):
            repo.git.add(file_path)
            repo.git.commit("-m", f"Backup envs at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            repo.remote(name="origin").push()
            print("✅ 环境变量已备份到仓库")
        else:
            print("ℹ️ 没有变化，跳过提交")
    except GitCommandError as e:
        print(f"Git 操作失败: {e}")


if __name__ == "__main__":
    token = get_ql_token()
    if not token:
        exit(1)
    envs = get_ql_envs(token)
    if envs:
        backup_envs_to_repo(envs)
