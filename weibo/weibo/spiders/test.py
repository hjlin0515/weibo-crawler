#!/usr/bin/env python
#-*- coding:utf-8 -*-

from weiboPost import weiboPostData
import MySQLdb

def main():
    weibo1 = weiboPostData('13092400382','yuezong253') //funny
    #weibo2 = weiboPostData('15664826416','cizhui111')//被冻
    #weibo3 = weiboPostData('18246146073','zhishi664')//American drama
    #weibo4 = weiboPostData('13790072934','laozhi818')//cartoon
    #weibo5 = weiboPostData('15686042984','yunren260')//scrapy
    #weibo = [weibo1,weibo2,weibo3,weibo4,weibo5]

    conn = MySQLdb.connect('127.0.0.1','root','root','weibo')
    stmt = 'SELECT weibo_id FROM weibo'
    cur = conn.cursor()
    cur.execute(stmt)
    weibo_ids = cur.fetchall()

    weibo_ids = list(weibo_ids)
    for i in range(len(weibo_ids)):
        weibo_ids[i] = weibo_ids[i][0].encode('utf-8')
        #eibo1.forwardWeibo(weibo_ids[i], 'TEST')
        print weibo1.username,weibo_ids[i]
    a = weibo1.username
    cur.execute("INSERT INTO record VALUES (%s,%s,%s,%s);" ,(weibo1.username,'forward','TEST',weibo_ids[i]) )
    conn.commit()


if __name__ == '__main__':
    main()
