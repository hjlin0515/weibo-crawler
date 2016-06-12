#!/usr/bin/env python
#-*- coding:utf-8 -*-
import MySQLdb
import datetime
from weiboPost import weiboPostData
import time
import random
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class postData():
    username = ''
    password = ''
    interest = ''
    def __init__(self,username,password,interest,liveness):
        self.username = username
        self.password = password
        self.interest = interest
        self.liveness = liveness
        self.conn = MySQLdb.connect('127.0.0.1','lhj','1234','weibo_srp',charset='utf8')
        self.weibo = weiboPostData(username,password)
    def post(self):
        stmt = "SELECT weibo_id,content FROM weibo,target WHERE weibo.user_id=target.user_id and category = "  + "'" + self.interest + "'"
        cursor = self.conn.cursor()
        cursor.execute(stmt)
        weibos_temp = cursor.fetchall()
        weibos_temp = list(weibos_temp)
        weibos = []

        for i in weibos_temp:
            weibo = {}
            weibo['weibo_id'] = i[0].encode('utf-8')
            weibo['weibo'] = i[1].encode('utf-8')
            weibos.append(weibo)

        numbers = min(self.liveness,len(weibos_temp))

        i=0
	while i<numbers:
            i=i+1
            weibo = random.choice(weibos)
            if int(weibo['weibo_id'])%3 == 0:
                if self.weibo.forwardWeibo(weibo['weibo_id'],weibo['weibo'][:10]):
                    status = 'SUCCESSFULLY'
                else:
                    status = 'FAILLY'
                    i=i-1#若发送失败则再发一条
                self.record('forward',weibo['weibo'][:10],weibo['weibo_id'],\
                weibo['weibo'],datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S'),status)
            elif int(weibo['weibo_id'])%3 == 1:
                if self.weibo.sendWeibo(weibo['weibo'][:10]):
                    status='SUCCESSFULLY'
                else:
                    status = 'FAILLY'
                    i=i-1
                self.record('send',weibo['weibo'][:10],'',\
                '',datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S'),status)
            elif int(weibo['weibo_id'])%3 == 2:
                if self.weibo.commentWeibo(weibo['weibo_id'],weibo['weibo'][:10]):
                    status='SUCCESSFULLY'
                else:
                    status = 'FAILLY'
                    i=i-1
                self.record('comment',weibo['weibo'][:10],weibo['weibo_id'],\
                weibo['weibo'],datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S'),status)
            weibos.remove(weibo)#删除已经转发的微博，避免重复
            time.sleep(180)


    def record(self,type,text,weibo_id,weibo,date,status):
        cur = self.conn.cursor()
        stmt = 'INSERT INTO record VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
        cur.execute(stmt,(self.username,self.interest,type,text,weibo_id,weibo,date,status))
        self.conn.commit()


def main():
    conn = MySQLdb.connect('127.0.0.1','lhj','1234','weibo_srp')
    cur = conn.cursor()
    stmt = 'SELECT username,password,interest,liveness FROM control_account WHERE now() BETWEEN start_time AND end_time'
    cur.execute(stmt)
    accounts_temp = cur.fetchall()
    accounts = []

    for i in accounts_temp:
            account = {}
            account['username'] = i[0].encode('utf-8')
            account['password'] = i[1].encode('utf-8')
            account['interest'] = i[2].encode('utf-8')
            account['liveness'] = i[3]
            accounts.append(account)

    for i in accounts:
        postData(i['username'],i['password'],i['interest'],i['liveness']).post()

if __name__ == '__main__':
    main()
