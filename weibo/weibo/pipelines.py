# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
reload(sys)
sys.setdefaultencoding("utf8")
from twisted.enterprise import adbapi
from weibo.items import fanItem,weiboItem,commentItem
from weibo.db import fanTable,weiboTable,commentTable,targetTable
import datetime
import MySQLdb




class EncodePipeline(object):
    def process_item(self,item,spider):
        if isinstance(item,fanItem):
            item['user_id'] = item['user_id'].encode('utf-8')
            item['fan_id'] = item['fan_id'].encode('utf-8')
            item['fan_name'] = item['fan_name'].encode('utf-8')
        elif isinstance(item,weiboItem):
            item['user_id'] = item['user_id'].encode('utf-8')
            item['content'] = item['content'].encode('utf-8')
            item['time'] = item['time'].encode('utf-8')
            item['weibo_id'] = item['weibo_id'].encode('utf-8')
        elif isinstance(item,commentItem):
            item['user_id'] = item['user_id'].encode('utf-8')
            item['weibo_id'] = item['weibo_id'].encode('utf-8')
            item['content'] = item['content'].encode('utf-8')
            item['time'] = item['time'].encode('utf-8')
            item['comment_id'] = item['comment_id'].encode('utf-8')
        return item

class WeiboPipeline(object):
    def __init__(self,host,username,password,db):
        self.host = host
        self.username = username
        self.password = password
        self.db = db


    @classmethod
    def from_crawler(cls,crawler):
        host = crawler.settings.get('MYSQL_HOST')
        username = crawler.settings.get('MYSQL_USERNAME')
        password = crawler.settings.get('MYSQL_PASSWORD')
        db = crawler.settings.get('MYSQL_DB')
        return cls(host,username,password,db)

    def open_spider(self,spider):
        self.conn = MySQLdb.connect(self.host,self.username,self.password,self.db,charset='utf8')
        self.weibo_table = weiboTable(self.conn)
        self.fan_table = fanTable(self.conn)
        self.comment_table = commentTable(self.conn)
        self.target_table = targetTable(self.conn)
        old_weibos = self.weibo_table.select_all_old_weibo()
        for weibo in old_weibos:
            weibo_dict = {}
            weibo_dict['user_id'] = weibo[0].encode('utf-8')
            weibo_dict['weibo_id'] = weibo[1].encode('utf-8')
            spider.old_weibos.append(weibo)
        user_ids = self.target_table.select_all_target()
        for user_id in user_ids:
            user_id = user_id[0].encode('utf-8')
            spider.user_id.append(user_id)

    def close_spider(self,spider):
        self.conn.close()

    def process_item(self, item, spider):
        if isinstance(item,fanItem):
            self.fan_table.insert(item['user_id'],item['fan_id'],item['fan_name'])
        elif isinstance(item,weiboItem):
            self.weibo_table.insert(item['user_id'], item['content'],item['time'],item['weibo_id'])
        elif isinstance(item,commentItem):
            self.comment_table.insert(item['user_id'], item['weibo_id'],item['comment_id'], item['content'], item['time'])
        return item
