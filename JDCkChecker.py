import os
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List

class JDCkChecker:
    def __init__(self):
        self.env = {
            "BEANCHANGE_USERGP2": os.getenv("BEANCHANGE_USERGP2", "").split('&'),
            "BEANCHANGE_USERGP3": os.getenv("BEANCHANGE_USERGP3", "").split('&'),
            "BEANCHANGE_USERGP4": os.getenv("BEANCHANGE_USERGP4", "").split('&'),
            "CHECKCK_SHOWSUCCESSCK": os.getenv("CHECKCK_SHOWSUCCESSCK", "false"),
            "CHECKCK_CKALWAYSNOTIFY": os.getenv("CHECKCK_CKALWAYSNOTIFY", "false"),
            "CHECKCK_CKAUTOENABLE": os.getenv("CHECKCK_CKAUTOENABLE", "false"),
            "CHECKCK_CKNOWARNERROR": os.getenv("CHECKCK_CKNOWARNERROR", "false"),
            "CHECKCK_CKAUTODEL": os.getenv("CHECKCK_CKAUTODEL", "false"),
            "WP_APP_TOKEN_ONE": os.getenv("WP_APP_TOKEN_ONE", "")
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.42",
            "Accept-Language": "zh-cn",
            "Referer": "https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&"
        }
        self.session = requests.Session()

    def get_cookies(self) -> List[Dict]:
        # 从环境变量或数据库获取CK列表，这里需要根据实际情况实现
        # 示例：假设从环境变量获取，每个CK用换行分隔
        return [{"id": "1", "value": os.getenv("JD_COOKIE_1"), "status": 0}]

    def is_login_valid(self, cookie: str) -> bool:
        """验证CK有效性"""
        try:
            # 使用接口1验证
            response = self.session.get(
                "https://me-api.jd.com/user_new/info/GetJDUserInfoUnion",
                headers=self.headers,
                cookies=self._parse_cookie(cookie),
                timeout=10
            )
            data = response.json()
            if data.get('retcode') == '1001':
                return False
            if data.get('retcode') == '0' and data.get('data') and data['data'].get('userInfo'):
                return True
            
            # 接口1验证失败，使用接口2加强验证
            response = self.session.get(
                "https://plogin.m.jd.com/cgi-bin/ml/islogin",
                headers={
                    **self.headers,
                    "Referer": "https://h5.m.jd.com/",
                    "User-Agent": "jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"
                },
                cookies=self._parse_cookie(cookie),
                timeout=10
            )
            data = response.json()
            return data.get('islogin') == '1'
        
        except Exception as e:
            print(f"验证失败: {str(e)}")
            return False

    def disable_ck(self, ck_id: str) -> bool:
        """禁用CK"""
        try:
            # 调用禁用接口，这里需要根据实际API实现
            response = self.session.post(
                f"https://your-api-domain.com/disable_ck/{ck_id}",
                headers={"Authorization": "Bearer YOUR_TOKEN"},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"禁用失败: {str(e)}")
            return False

    def auto_delete_old_ck(self, ck_updated_at: str) -> bool:
        """自动删除超过10天未更新的CK"""
        try:
            update_time = datetime.strptime(ck_updated_at, "%Y-%m-%dT%H:%M:%S.%fZ")
            if datetime.now() - update_time > timedelta(days=10):
                # 调用删除接口
                return True
            return False
        except Exception as e:
            print(f"时间计算错误: {str(e)}")
            return False

    def _parse_cookie(self, cookie_str: str) -> Dict:
        """解析Cookie字符串为字典"""
        return {item.split('=')[0]: item.split('=')[1] for item in cookie_str.split('; ') if item}

    def run(self):
        cks = self.get_cookies()
        for ck in cks:
            print(f"检测CK {ck['id']}...")
            if self.is_login_valid(ck['value']):
                print(f"CK {ck['id']} 有效")
                if ck['status'] == 1 and self.env["CHECKCK_CKAUTOENABLE"] == "true":
                    # 自动启用逻辑
                    pass
            else:
                print(f"CK {ck['id']} 失效，正在禁用...")
                if self.disable_ck(ck['id']):
                    print(f"CK {ck['id']} 禁用成功")
                    if self.env["CHECKCK_CKAUTODEL"] == "true":
                        # 自动删除逻辑
                        pass
                else:
                    print(f"CK {ck['id']} 禁用失败")
            time.sleep(2)

if __name__ == "__main__":
    checker = JDCkChecker()
    checker.run()
