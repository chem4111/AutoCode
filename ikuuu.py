import requests
import os

#export ikuuu='邮箱&密码'      多号#号隔开

#export REMARKS_1="账号1备注"
#export REMARKS_2="账号2备注"
#export REMARKS_3="账号3备注"

#pushplush 通知，单人不用填TOPIC
#https://www.pushplus.plus/push1.html
#export TOKEN="你的token"
#export TOPIC="你的群组编号"


def main():
    r = 1
    oy = ql_env()
    print("共找到" + str(len(oy)) + "个账号")
    # 获取环境变量的值
    remarks = {
        1: os.getenv("REMARKS_1"),
        2: os.getenv("REMARKS_2"),
        3: os.getenv("REMARKS_3")
    }
    all_messages = []  # 创建一个列表，用于存储所有的消息
    for i in oy:
        remark = remarks.get(r, str(r))  # 获取账号的备注，如果没有对应备注，则使用默认值
        all_messages.append(f"{remark}的账号：")  # 将消息添加到列表中
        print(f"{remark}的账号：")
        email = i.split('&')[0]
        passwd = i.split('&')[1]
        sign_in(email, passwd,all_messages)
        r += 1
    send_notice("\n".join(all_messages))  # 将所有消息组合成一个字符串并发送
def sign_in(email, passwd,all_messages):
    try:
        body = {"email" : email,"passwd" : passwd,}
        headers = {'user-agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'}
        resp = requests.session()
        resp.post(f'https://ikuuu.pw/auth/login', headers=headers, data=body)
        ss = resp.post(f'https://ikuuu.pw/user/checkin').json()
        #print(ss)
        if 'msg' in ss:
            all_messages.append(ss['msg'])  # 将消息添加到列表中
            print(ss['msg'])
    except:
        print('请检查帐号配置是否错误')
def ql_env():
    if "ikuuu" in os.environ:
        token_list = os.environ['ikuuu'].split('#')
        if len(token_list) > 0:
            return token_list
        else:
            print("ikuuu变量未启用")
            sys.exit(1)
    else:
        print("未添加ikuuu变量")
        sys.exit(0)

def send_notice(content):    # 通知消息发送函数
    # 获取环境变量的值
    token = os.getenv("TOKEN")
    topic = os.getenv("TOPIC")
    title = "iKUUU签到"
    url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template=html"   #单人推送
    #url = f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}&template=html&topic={topic}"  #群组推送
    response = requests.request("GET", url)
    #print(response.text)


if __name__ == '__main__':
    main()