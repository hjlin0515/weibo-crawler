#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf8")


class Table:
    def __init__(self,conn):
        self.conn = conn

    def insert(self,*args):
        cur = self.conn.cursor()
        cur.execute(self.insert_stmt,args)
        self.conn.commit()

class weiboTable(Table):
    def __init__(self,conn):
        self.table_name = 'weibo'
        self.insert_stmt = 'INSERT INTO '+ self.table_name + ' VALUES(%s, %s, %s, %s)'
        Table.__init__(self,conn)

    def select_all_old_weibo(self):
        select_stmt = 'SELECT user_id, weibo_id FROM weibo ORDER BY time'
        cur = self.conn.cursor()
        cur.execute(select_stmt)
        weibo_ids = cur.fetchall()
        return weibo_ids
    def is_exist_by_weibo_id(self,weibo_id):
        select_stmt = 'SELECT 1 FROM '+ self.table_name +' WHERE weibo_id=%s'
        cur = self.conn.cursor()
        cur.execute(select_stmt,weibo_id)
        if cur.fetchall():
            return True
        else:
            return False

class commentTable(Table):
    def __init__(self,conn):
        self.table_name = 'comment'
        self.insert_stmt = 'INSERT INTO ' + self.table_name + ' VALUES(%s,%s,%s,%s,%s)'
        Table.__init__(self,conn)

class fanTable(Table):
    def __init__(self,conn):
        self.table_name = 'fan'
        self.insert_stmt = 'INSERT INTO ' + self.table_name + ' VALUES(%s, %s, %s)'
        Table.__init__(self,conn)

class targetTable():
    def __init__(self,conn):
        self.table_name = 'target'
        self.conn = conn
    def select_all_target(self):
        select_stmt = 'SELECT user_id FROM ' + self.table_name
        cur = self.conn.cursor()
        cur.execute(select_stmt)
        user_ids = cur.fetchall()
        return user_ids
    def select_target_by_category(self,category):
        select_stmt = 'SELECT user_id FROM ' + self.table_name + ' WHERE category = ' + category
        cur = self.conn.cursor()
        cur.execute(select_stmt)
        user_ids = cur.fetchall()
        return user_ids
