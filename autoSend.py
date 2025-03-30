import json
import os

def update_ck_file(input_db_path, output_file_path):
    # 初始化结果字典：pt_pin -> set(Uid)
    result_dict = {}

    # 1. 读取现有 JSON 文件
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            for entry in existing_data:
                pt_pin = entry['pt_pin']
                uid = entry['Uid']
                if pt_pin not in result_dict:
                    result_dict[pt_pin] = set()
                result_dict[pt_pin].add(uid)

    # 2. 解析环境变量数据库
    with open(input_db_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            # 仅处理 JD_COOKIE 记录
            if data.get('name') != 'JD_COOKIE':
                continue

            value = data.get('value', '')
            remarks = data.get('remarks', '')

            # 提取 pt_pin
            if 'pt_pin=' in value:
                pt_pin = value.split('pt_pin=')[1].split(';')[0].strip()
            else:
                continue  # 无 pt_pin 则跳过

            # 提取 Uid
            if remarks.startswith('UID_'):
                uid = remarks[len('UID_'):].strip()
            else:
                continue  # 无 Uid 则跳过

            # 更新结果字典
            if pt_pin not in result_dict:
                result_dict[pt_pin] = set()
            result_dict[pt_pin].add(uid)

    # 3. 转换为列表格式
    output_list = []
    for pt_pin, uids in result_dict.items():
        for uid in uids:
            output_list.append({
                "pt_pin": pt_pin,
                "Uid": uid
            })

    # 4. 写入文件（仅当内容变化时更新）
    if os.path.exists(output_file_path):
        with open(output_file_path, 'r', encoding='utf-8') as f:
            existing_content = json.load(f)
            if existing_content == output_list:
                print("文件内容无变化，无需更新")
                return

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=4, ensure_ascii=False)
    print(f"成功更新文件：{output_file_path}，当前包含 {len(output_list)} 条记录")

# 配置路径（根据实际情况修改）
INPUT_DB = "/db/env.db"
OUTPUT_FILE = "/scripts/CK_WxPusherUid.json"

update_ck_file(INPUT_DB, OUTPUT_FILE)
