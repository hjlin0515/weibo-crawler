#!/usr/bin/env python
#-*- coding:utf-8 -*-

import urllib
import urllib2
import cookielib
import base64
import re, sys, json
import binascii
import rsa
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Weibo():
  def __init__(self):
    #保存cookie
    self.cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(self.cj)
    self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)


  def _get_servertime(self, username):
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)' %username

    data = self.opener.open(url).read()
    p = re.compile('\((.*)\)')
    json_data = p.search(data).group(1)
    data = json.loads(json_data)
    servertime = str(data['servertime'])
    nonce = data['nonce']
    pubkey = data['pubkey']
    rsakv = data['rsakv']
    return servertime, nonce, pubkey, rsakv

  def _get_pwd(self, pwd, servertime, nonce, pubkey):
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537)
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(pwd)
    pwd = rsa.encrypt(message, key)
    return binascii.b2a_hex(pwd)

  def _get_user(self, username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username

  def login(self, username, pwd):
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)'
    try:
      servertime, nonce, pubkey, rsakv = self._get_servertime(username)
    except:
      print  'Get severtime error!'
      return None
    postdata = {
            'entry':'weibo',
            'gateway':'1',
            'from':'',
            'savestate': '7',
            'userticket': '1',
            'ssosimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': self._get_user(username),
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': self._get_pwd(pwd,servertime,nonce,pubkey),
            'encoding': 'UTF-8',
            'prelt': '115',
            'rsakv': rsakv,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
    }

    postdata = urllib.urlencode(postdata)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}

    req = urllib2.Request(
      url=url,
      data=postdata,
      headers=headers
    )

    result = self.opener.open(req)

    text = result.read()
    p = re.compile('location\.replace\([\'|"](.*?)[\'|"]\)')
    try:
      return p.search(text).group(1)
    except:
      return None
