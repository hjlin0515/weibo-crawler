#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
import urllib2
import re
import json
from weiboLogin import Weibo
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class weiboPostData():
    username = ''
    password = ''
    weibo = Weibo()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    userid = ''


    def __init__(self,username,password):
        self.username = username
        self.password = password
        login_url = self.weibo.login(self.username,self.password)
        result = self.weibo.opener.open(login_url).read()
        id_pattern = re.compile(r'uniqueid":"(\d+)"')
        self.userid = id_pattern.search(result).group(1)
        self.headers['Referer'] = 'http://weibo.com/u/%s/home?topnav=1&wvr=6' % self.userid

    #发送微博
    def sendWeibo(self,text):
        url = 'http://weibo.com/aj/mblog/add?ajwvr=6'
        postdata = {
        'loaction':'v6_content_home',
        'appkey':'',
        'style_type':'1',
        'pic_id':'',
        'text':text,
        'pdetail':'',
        'rank':'0',
        'rankid':'',
        'module':'stissue',
        'pub_source':'main_',
        'pub_type':'dialog',
        '_t':'0'
        }
        postdata = urllib.urlencode(postdata)
        return self.post(url,postdata)



    #转发微博
    def forwardWeibo(self,weibo_id,text):
        url = 'http://weibo.com/aj/v6/mblog/forward?ajwvr=6&domain=%s' % self.userid
        postdata = {
        'pic_src':'',
        'pic_id':'',
        'appkey':'',
        'mid':weibo_id,
        'style_type':'1',
        'mark':'',
        'reason':text,
        'location':'v6_content_home',
        'pdetail':'',
        'module':'',
        'page_module_id':'',
        'refer_sort':'',
        'rank':'0',
        'rankid':'',
        'group_source':'group_all',

        '_t':'0'}
        postdata = urllib.urlencode(postdata)
        return self.post(url,postdata)



    def commentWeibo(self,weibo_id,text):
        url = 'http://weibo.com/aj/v6/comment/add?ajwvr=6'
        postdata = {
        'act':'post',
        'mid':weibo_id,
        'uid':self.userid,
        'forward':'0',
        'isroot':'0',
        'content':text,
        'location':'v6_content_home',
        'module':'scommlist',
        'group_source':'group_all',
        'pdetail':'',
        '_t':'0'}
        postdata = urllib.urlencode(postdata)
        return self.post(url,postdata)




    def post(self, url, postdata):
        req = urllib2.Request(url=url,data=postdata,headers=self.headers)
        result = self.weibo.opener.open(req).read()

        resultdata = json.loads(result)
        msg = resultdata['msg']

        code_pattern = re.compile(r'code":"(\d+)"')
        code = code_pattern.search(result).group(1)
        if msg:
            print msg
        return code#发送微博后返回的状态码
