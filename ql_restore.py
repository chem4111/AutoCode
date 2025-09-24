#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time   : 2025/9/24
# -------------------------------

import os
import json
import subprocess
import requests

# ================= 配置 =================
QL_CONFIG = {
    "url": os.getenv("QL_URL", "http://127.0.0.1:5700"),
    "client_id": os.getenv("QL_CLIENT_ID", ""),
    "client_secret": os.getenv("QL_CLIENT_SECRET", "")
}

# 仓库配置（已改为 gitee + master）
REPO_CONFIG = {
    "path": os.getenv("QL_REPO_PATH", "/ql/data/repo/AutoCode"),
    "branch": os.getenv("QL_REPO_BRANCH", "master"),
}

# 模式选择：
# False = 清空重建（完全一致，最保险）
# True  = 更新追加（存在则更新，不存在则新增）
UPDATE_MODE = True
# =======================================


def get_token():
    url = f"{QL_CONFIG['url']}/open/auth/token"
    params = {
        "client_id": QL_CONFIG["client_id"],
        "client_secret": QL_CONFIG["client_secret"]
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["data"]["token"]


def git_pull_repo():
    print("🔄 拉取仓库最新内容...")
    if not os.path.exists(REPO_CONFIG["path"]):
        raise FileNotFoundError(f"仓库路径不存在: {REPO_CONFIG['path']}")

    subprocess.run(
        ["git", "-C", REPO_CONFIG["path"], "pull", "origin", REPO_CONFIG["branch"]],
        check=True
    )
    print("✅ 仓库更新成功")


def load_envs_from_repo():
    env_file = os.path.join(REPO_CONFIG["path"], "env.json")
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"仓库里没有 env.json: {env_file}")

    with open(env_file, "r", encoding="utf-8") as f:
        envs = json.load(f)

    print(f"✅ 成功加载 {len(envs)} 条环境变量")
    return envs


def get_current_envs(token):
    url = f"{QL_CONFIG['url']}/open/envs"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data.get("data", [])


def restore_envs_to_ql(token, envs):
    headers = {"Authorization": f"Bearer {token}"}
    current_envs = get_current_envs(token)

    print(f"📋 获取当前环境变量... 共 {len(current_envs)} 条")

    # 构建索引：name -> {value, id/_id}
    current_envs_dict = {}
    for env in current_envs:
        env_id = env.get("id") or env.get("_id")
        current_envs_dict[env["name"]] = {
            "value": env["value"],
            "id": env_id
        }

    if not UPDATE_MODE:
        # 🔥 清空重建模式
        print("🧹 清理旧的环境变量...")
        env_ids = [env.get("id") or env.get("_id") for env in current_envs if (env.get("id") or env.get("_id"))]
        if env_ids:
            delete_url = f"{QL_CONFIG['url']}/open/envs"
            response = requests.delete(delete_url, headers=headers, json=env_ids, timeout=10)
            response.raise_for_status()
        print("✅ 旧环境变量清理完成")

        # 添加新变量
        add_url = f"{QL_CONFIG['url']}/open/envs"
        response = requests.post(add_url, headers=headers, json=envs, timeout=10)
        response.raise_for_status()
        print(f"✅ 成功恢复 {len(envs)} 条环境变量")
        return True

    else:
        # 🟢 更新追加模式
        add_list = []
        update_count = 0
        for env in envs:
            name = env["name"]
            value = env["value"]

            if name in current_envs_dict and current_envs_dict[name]["id"]:
                # 已存在 → 更新
                env_id = current_envs_dict[name]["id"]
                put_url = f"{QL_CONFIG['url']}/open/envs"
                response = requests.put(put_url, headers=headers, json=[{
                    "name": name,
                    "value": value,
                    "id": env_id
                }], timeout=10)
                response.raise_for_status()
                update_count += 1
            else:
                # 不存在 → 新增
                add_list.append(env)

        if add_list:
            add_url = f"{QL_CONFIG['url']}/open/envs"
            response = requests.post(add_url, headers=headers, json=add_list, timeout=10)
            response.raise_for_status()

        print(f"✅ 更新 {update_count} 条，新增 {len(add_list)} 条")
        return True


if __name__ == "__main__":
    print("🚀 开始从 Gitee 恢复青龙环境变量...")

    # Step 1: 检查配置
    if not all([QL_CONFIG["url"], QL_CONFIG["client_id"], QL_CONFIG["client_secret"]]):
        raise SystemExit("❌ 请先配置 QL_URL / QL_CLIENT_ID / QL_CLIENT_SECRET")

    # Step 2: 获取 token
    ql_token = get_token()
    print("✅ 成功获取青龙令牌")

    # Step 3: 更新仓库
    git_pull_repo()

    # Step 4: 加载仓库 env.json
    envs = load_envs_from_repo()

    # Step 5: 恢复/更新变量
    restore_envs_to_ql(ql_token, envs)
