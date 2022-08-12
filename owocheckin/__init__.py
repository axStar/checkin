__version__ = '0.1.0'

import logging
import logging.config
import pathlib
import smtplib
import time
from email.message import EmailMessage
from configparser import ConfigParser
import requests

path = pathlib.Path(__file__)
config = ConfigParser()

config.read(path.parent / "config.ini")
logging.config.fileConfig(path.parent / 'logging.conf')

# create logger
logger = logging.getLogger('first')

def Sendmail(header: str, content: str, receiver: str = config["emailMessage"]["receiver"], u: str = config["emailMessage"]["sender"], pw: str = config["emailMessage"]["password"]):

    smtpObj = smtplib.SMTP("smtp.office365.com", 587)
    logger.debug("构造smtp对象成功.")
    message = EmailMessage()
    logger.debug("构造EmailMessage对象成功.")

    message.set_content(content)
    logger.debug("设置message内容成功.")

    message["Subject"] = header
    message["From"] = "aa-TS01"
    message["To"] = f"{receiver}"
    logger.debug("设置message标题成功.")

    smtpObj.starttls()
    logger.debug("更改协议成功.")

    smtpObj.login(user=u, password=pw)
    logger.debug(f"登录用户{u}成功.")

    smtpObj.send_message(msg=message, from_addr=u, to_addrs=receiver)
    logger.info(f"成功向{receiver}发送邮件.")

def owoLogin(user: str, password: str):
    head = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    formdata = {"email":user, "passwd":password}
    response = requests.post("https://owo.ecycloud.com/auth/login", formdata, headers=head)
    logger.info(f"发送登录请求，响应代码：{response.status_code}")
    return response.cookies.get_dict()

def checkin(cookie):
    response = requests.post("https://owo.ecycloud.com/user/checkin", cookies=cookie)
    logger.info(f"发送签到请求，响应代码：{response.status_code}")
    return response.json()

if __name__ == "__main__":
    logger.info("脚本开始运行...")

    response = checkin(owoLogin(config["owo"]["user"], config["owo"]["password"]))
    if response["ret"] == 1:
        msg = f"""{response['msg']}

剩余流量：{response['trafficInfo']['unUsedTraffic']}
-----
今日使用：{response['trafficInfo']['todayUsedTraffic']}
累计使用：{response['trafficInfo']['lastUsedTraffic']}
累计获得：{response['traffic']}"""

        Sendmail(f"{time.asctime(time.localtime())}|签到通知", msg, "2272613209@qq.com")
    else:
        logger.warning("您今天签到过了！")
