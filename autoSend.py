#!/usr/bin/python3
# -- coding: utf-8 --
# -------------------------------
# @Author : https://github.com/chem4111/AutoCode/
# @Time : 2025/3/27 13:23
# -------------------------------
# cron "0 * 24 * *" script-path=xxx.py,tag=匹配cron用
# const $ = new Env('自动匹配推送json')

import json
import os
import logging
from typing import Dict, Set, List, Any


#将环境变量的pin和uid自动组成json报文。uid填在对应pt_pin的备注里


# 配置常量
INPUT_DB_PATH = "/ql/db/env.db"
OUTPUT_FILE_PATH = "/ql/scripts/CK_WxPusherUid.json"
ENCODING = "utf-8"
JD_COOKIE_NAME = "JD_COOKIE"
UID_PREFIX = "UID_"

# 初始化日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def load_existing_data(file_path: str) -> Dict[str, Set[str]]:
    """加载现有JSON文件并返回字典结构"""
    result: Dict[str, Set[str]] = {}
    if not os.path.exists(file_path):
        return result

    try:
        with open(file_path, "r", encoding=ENCODING) as f:
            existing_data: List[Dict[str, str]] = json.load(f)
            for entry in existing_data:
                if "pt_pin" in entry and "Uid" in entry:
                    pt_pin = entry["pt_pin"]
                    uid = entry["Uid"]
                    result.setdefault(pt_pin, set()).add(uid)
                else:
                    logger.warning("忽略无效条目: %s", entry)
    except (json.JSONDecodeError, IOError) as e:
        logger.error("加载现有文件失败: %s", e)

    return result


def parse_env_db(file_path: str) -> Dict[str, Set[str]]:
    """解析环境变量数据库"""
    result: Dict[str, Set[str]] = {}

    if not os.path.exists(file_path):
        logger.error("输入文件不存在: %s", file_path)
        return result

    try:
        with open(file_path, "r", encoding=ENCODING) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data: Dict[str, Any] = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("行 %d: JSON解析失败", line_num)
                    continue

                if data.get("name") != JD_COOKIE_NAME:
                    continue

                value = data.get("value", "")
                remarks = data.get("remarks", "")

                # 提取pt_pin
                start_index = value.find("pt_pin=")
                if start_index != -1:
                    start_index += len("pt_pin=")
                    end_index = value.find(";", start_index)
                    if end_index == -1:
                        end_index = len(value)
                    pt_pin = value[start_index:end_index].strip()
                else:
                    continue

                # 提取UID，带上UID_前缀
                if remarks.startswith(UID_PREFIX):
                    uid = remarks
                else:
                    continue

                result.setdefault(pt_pin, set()).add(uid)

    except IOError as e:
        logger.error("读取环境数据库失败: %s", e)

    return result


def save_output(data: Dict[str, Set[str]], output_path: str) -> bool:
    """保存结果到文件"""
    output_list: List[Dict[str, str]] = [
        {"pt_pin": pin, "Uid": uid}
        for pin, uids in data.items()
        for uid in uids
    ]

    # 检查文件是否需要更新
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding=ENCODING) as f:
                existing = json.load(f)
                if existing == output_list:
                    logger.info("内容未变化，无需更新")
                    return False
        except (IOError, json.JSONDecodeError) as e:
            logger.warning("比较现有文件失败: %s", e)

    try:
        with open(output_path, "w", encoding=ENCODING) as f:
            json.dump(output_list, f, indent=4, ensure_ascii=False)
            logger.info("成功写入 %d 条记录到 %s", len(output_list), output_path)
            return True
    except IOError as e:
        logger.error("文件写入失败: %s", e)
        return False


def main():
    # 合并数据
    combined_data = load_existing_data(OUTPUT_FILE_PATH)
    new_data = parse_env_db(INPUT_DB_PATH)

    # 合并新数据
    for pt_pin, uids in new_data.items():
        combined_data.setdefault(pt_pin, set()).update(uids)

    # 保存结果
    save_output(combined_data, OUTPUT_FILE_PATH)


if __name__ == "__main__":
    main()
