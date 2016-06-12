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
        #保存发送微博的函数 0:comment,1:forward,2:send
        self.postFunc = [self.weibo.commentWeibo,self.weibo.forwardWeibo,self.weibo.sendWeibo]

    #将发送微博的记录存入数据库
    def record(self,type,text,weibo_id,weibo,date,status):
        if type == "send":
            weibo_id = ""#若为发送微博则不需要保存weibo_id
        cur = self.conn.cursor()
        stmt = 'INSERT INTO record VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            cur.execute(stmt,(self.username,self.interest,type,text,weibo_id,weibo,date,status))
            self.conn.commit()
        except:
            self.conn.rollback()

    #删除数据库中已被删除的原微博
    def clearDeletedWeibo(self,weibo_id):
        cur = self.conn.cursor()
        stmt = 'DELETE FROM weibo WHERE id = ' + weibo_id
        try:
            cur.execute(stmt)
            self.conn.commit
        except:
            self.conn.rollback()

    def postWeibo(self,weibo):
        postType = int(weibo["weibo_id"])%3 #0:comment,1:forward,2:send
        Type = ['comment','forward','send']
        statusCode = -1#发送微博后返回的状态码 10000:发送成功 10001:原微博已被删除
        if postType==0 or postType==1:
            statusCode = self.postFunc[postType](weibo['weibo_id'],weibo['weibo'])
        else:
            statusCode = self.postFunc[postType](weibo['weibo'])
        print statusCode
        if statusCode == "100000":
            self.record(Type[postType],weibo['weibo'],weibo['weibo_id'],\
            weibo['weibo'],datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S'),"SUCCESSFULLY")
        elif statusCode == "100001":#原微博已被删除
            self.record(Type[postType],weibo['weibo'],weibo['weibo_id'],\
            weibo['weibo'],datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S'),"FAILLY")
            self.clearDeletedWeibo(weibo['weibo_id'])
            raise "The weibo has been deleted"
        else:#未知错误
            self.record(Type[postType],weibo['weibo'],weibo['weibo_id'],\
            weibo['weibo'],datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S'),"FAILLY")
            raise "NOT KNOWN ERROR"

    def post(self):
        #从数据库中提取爬到的微博
        stmt = "SELECT weibo_id,content FROM weibo,target WHERE weibo.user_id=target.user_id and category = "  + "'" + self.interest + "'"
        try:
            cursor = self.conn.cursor()
            cursor.execute(stmt)
            weibos_temp = cursor.fetchall()
            weibos_temp = list(weibos_temp)
        except:
            print "Fetch weibos failly"

        weibos = []
        for i in weibos_temp:
            weibo = {}
            weibo['weibo_id'] = i[0].encode('utf-8')
            weibo['weibo'] = i[1][:10].encode('utf-8')
            weibos.append(weibo)

        numbers = min(self.liveness,len(weibos_temp))

        i=0
        while i<numbers:
            i=i+1
            weibo = random.choice(weibos)
            try:
                self.postWeibo(weibo)
            except Exception as e:
                i=i-1#若发送失败则再发一条
                print e


            weibos.remove(weibo)#删除已经转发的微博，避免重复
            time.sleep(180)

def main():
    conn = MySQLdb.connect('127.0.0.1','lhj','1234','weibo_srp')
    cur = conn.cursor()
    stmt = 'SELECT username,password,interest,liveness FROM control_account WHERE now() BETWEEN start_time AND end_time'
    try:
        cur.execute(stmt)
        accounts_temp = cur.fetchall()
    except:
        print "Fetch accounts failly"
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
