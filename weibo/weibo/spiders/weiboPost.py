#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
import urllib2
import re
import json
from weiboLogin import Weibo

class weiboPostData():
    username = ''
    password = ''
    weibo = Weibo()
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
    user_id = ''

    def __init__(self,username,password):
        self.username = username
        self.password = password
        login_url = self.weibo.login(self.username,self.password)
        result = urllib2.urlopen(login_url).read()
        id_pattern = re.compile(r'uniqueid":"(\d+)"')
        self.user_id = id_pattern.search(result).group(1)
        self.headers['Referer'] = 'http://weibo.com/u/%s/home?topnav=1&wvr=6' % self.user_id

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
        if self.post(url,postdata):
            print "SEND SUCCESSFULLY"
        else:
            print "SEND FAILLY"
        #send_headers = self.headers.copy()

    #转发微博
    def forwardWeibo(self,weibo_id,text):
        url = 'http://weibo.com/aj/v6/mblog/forward?ajwvr=6&domain=%s' % self.user_id
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
        #'rid':'0_0_1_2669597129785822517'
        '_t':'0'}
        postdata = urllib.urlencode(postdata)
        if self.post(url,postdata):
            print "FORWARE SUCCESSFULLY"
        else:
            print "FORWARD FAILLY"

    def commentWeibo(self,weibo_id,text):
        url = 'http://weibo.com/aj/v6/comment/add?ajwvr=6'
        postdata = {
        'act':'post',
        'mid':weibo_id,
        'uid':self.user_id,
        'forward':'0',
        'isroot':'0',
        'content':text,
        'location':'v6_content_home',
        'module':'scommlist',
        'group_source':'group_all',
        'pdetail':'',
        '_t':'0'}
        postdata = urllib.urlencode(postdata)
        if self.post(url,postdata):
            print "COMMENT SUCCESSFULLY"
        else:
            print "COMMENT FAILLY"


    def post(self, url, postdata):
        req = urllib2.Request(url=url,data=postdata,headers=self.headers)
        result = urllib2.urlopen(req).read()

        resultdata = json.loads(result)
        msg = resultdata['msg']

        code_pattern = re.compile(r'code":"(\d+)"')
        code = code_pattern.search(result).group(1)
        if code == '100000':
            return True
        else:
            print msg
            return False



if __name__ == '__main__':
    weiboPost = weiboPostData('13092400382','yuezong253')
    #weiboPost.sendWeibo('TEST')
    weiboPost.forwardWeibo('3953790413593286','TEST')
    #weiboPost.commentWeibo('3954115669899209','回复@Ivan_Lam___:T2E2ST')
