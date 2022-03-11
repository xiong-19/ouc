import requests
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys

# 时间很重要
DATE = '2022-03-11'
# 羽毛球场的id
typeId = '2885ee0a-31a0-4a0b-a38f-b6867f9a6393' #台球场id
#typeId = '3bf3df97-53a8-46bf-b334-90a0bc6235d9'
head = {
    xxx:'xxx'
}

def getInformation():
    '''
    url: 查询所有球场的场馆id
    '''
    url = 'http://hqcggl.ouc.edu.cn/website/findPlaceList'
    # date可填 ‘今天‘ ，或者是下一天的日期
    form_data ={
        'typeId': typeId,
        'date': DATE
    }
    res = requests.post(url, data=form_data, headers=head)
    text = eval(((res.text).replace('false', 'False')).replace('null', 'None')) # 因为返回的一个键的值为flase,无法转换
    place = text['data']['allList']
    available_time = text['data']['list']
    for i in place:
        print(i)
    for i in available_time:
        print(i)
    return place, available_time

def judge(placeId, sT='18', eT='19', date=DATE):
    '''
    查询某个时间的场是否可用
    data的值为 -6： 不可用；1 可用；2 已被预约; -1 已过改时间（应该是）
    '''
    form_data = {
        'typeId': typeId,
        'placeId': placeId,
        'sTime': sT,
        'eTime': eT,
        'date': DATE
    }
    url = 'http://hqcggl.ouc.edu.cn/website/findPlaceStatus'
    res = requests.post(url, data=form_data, headers=head)
    text = eval(((res.text).replace('false', 'False')).replace('null', 'None'))
    return text['data']



def send(mess):
    mail = smtplib.SMTP()
    mail.connect("smtp.qq.com")
    mail.login("xxxx@qq.com", "xxxx")  # 发送邮箱,授权码(在设置的pop3/IMAP中开IMAP项)
    print('ok!\n')
    message = MIMEText(mess)
    message['Subject'] = Header("羽毛球场预约提醒")
    mail.sendmail("xxxx@qq.com", ["xxxx@qq.com"], message.as_string())  # 接受邮箱


def form(placeId, sT, eT, choose=1):
    url = 'http://hqcggl.ouc.edu.cn/website/addReserveAndRecord'
    if choose == 1:
        form_data = {
            'placeIds[]': placeId,
            'dates[]': DATE,
            'sTimes[]': sT,
            'eTimes[]': eT,
            'amounts[]': '20.00',
            'placeTypeId': typeId
        }
    # 同时约两个场(有问题)
    else:
        form_data = {
            'placeIds[]': placeId,
            'placeIds[]': placeId,
            'dates[]': DATE,
            'dates[]': DATE,
            'sTimes[]': sT,
            'sTimes[]': str(int(sT)+1),
            'eTimes[]': eT,
            'eTimes[]': str(int(eT)+1),
            'amounts[]': '10.00',
            'amounts[]': '10.00',
            'placeTypeId': typeId
        }
    res = requests.post(url, data=form_data, headers=head)
    print(res.text)
    text = eval(((res.text).replace('false', 'False')).replace('null', 'None'))  # 因为返回的一个键的值为flase,无法转换
    return text['status'], text['data']['id']


def makeForm(ID):
    url = 'http://hqcggl.ouc.edu.cn/website/absAmountByAmount'
    form_data = {
        'amount': '10.00',
        'reserveId': ID
    }
    res = requests.post(url, data=form_data, headers=head)
    print(res)
    print(res.text)


def m():
    starTime = '16'
    endTime = '19'
    choose = 1  # or 2; 预约一个场或者是两个场
    place, time = getInformation()
    if choose == 1:
        for k in range(int(starTime), int(endTime)):
            for m in range(len(place)):
                status, formId = form(place[m]['id'], str(k), str(k+1))
                if status == 'success':
                    makeForm(formId)
                    send('预约成功')
                    return
    if choose == 2:
        for k in range(int(starTime), int(endTime)-1):
            for m in range(len(place)):
                if judge(place[m]['id'],str(k),str(k+1)) == 1 and judge(place[m]['id'], str(k+1), str(k+2)) == 1:
                    status1, formId1 = form(place[m]['id'], str(k), str(k+1))
                    status2, formId2 = form(place[m]['id'], str(k+1), str(k+2))
                    if status1=='success' and status2=='success':
                        makeForm(formId1)
                        makeForm(formId2)
                        send('预约成功')
                        return

    send('预约失败')
if __name__ == '__main__':
    m()