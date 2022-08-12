__version__ = '0.1.0'


import pathlib
import smtplib
from datetime import date
from email.message import EmailMessage
from configparser import ConfigParser
import requests

def Sendmail(header: str, content: str, receiver: str, u: str , pw: str ):
    smtpObj = smtplib.SMTP("smtp.office365.com", 587)
    message = EmailMessage()
    message.set_content(content)
    message["Subject"] = header
    message["From"] = "aa-TS01"
    message["To"] = f"{receiver}"
    smtpObj.starttls()
    smtpObj.login(user=u, password=pw)
    smtpObj.send_message(msg=message, from_addr=u, to_addrs=receiver)

def owoLogin(user: str, password: str):
    head = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    formdata = {"email":user, "passwd":password}
    response = requests.post("https://owo.ecycloud.com/auth/login", formdata, headers=head)
    return response.cookies.get_dict()

def checkin(cookie):
    response = requests.post("https://owo.ecycloud.com/user/checkin", cookies=cookie)
    return response.json()

if __name__ == "__main__":
    # 获取路径
    path = pathlib.Path(__file__).parent

    # 读取config.ini
    config = ConfigParser()
    config.read(path / "config.ini")

    # 读取最后签到日期
    lastCheckin = date.fromisoformat(config["checkinDate"]["lastcheckin"])
    if date.today() <= lastCheckin:
        print("今日已签到.")
        quit()


    # 进行签到.
    try: 
        response = checkin(owoLogin(config["owo"]["user"], config["owo"]["password"]))
    except requests.Timeout:
        print("请求超时...")
        quit()
        
    if response["ret"] == 1:
        msg = f"""{response['msg']}

剩余流量：{response['trafficInfo']['unUsedTraffic']}
-----
今日使用：{response['trafficInfo']['todayUsedTraffic']}
累计使用：{response['trafficInfo']['lastUsedTraffic']}
累计获得：{response['traffic']}"""

        Sendmail(f"{date.today().strftime('%Y年-%m月-%d日')}|签到通知", msg, config["emailMessage"]["receiver"], config["emailMessage"]["sender"], config["emailMessage"]["password"] )
    else:
        print("您今天签到过了！")
