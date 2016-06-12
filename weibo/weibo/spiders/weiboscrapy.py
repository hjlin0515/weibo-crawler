#!/usr/bin/env python
#-*- encoding=utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider,Rule
#from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from datetime import datetime,timedelta
from weibo.items import fanItem,weiboItem,commentItem
from weibo import settings
import json
import re
from weiboLogin import Weibo
from scrapy import log
from scrapy import optional_features
#optional_features.remove('boto')



class wbSpider(CrawlSpider):
    username = settings.USERNAME
    password = settings.PASSWORD
    allowed_domains = ['weibo.com','sina.com.cn','weibo.cn']
    start_urls = []
    name = 'wb'
    weibo = Weibo()
    user_id = []#数据库中存放的要爬的用户ID
    #(pagebar,id,id,page,prepage)
    weibo_url = 'http://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&from=myfollow_all&is_all=1&pagebar=%s&pl_name=Pl_Official_MyProfileFeed__24&id=100505%s&script_uri=/u/%s&feed_type=0&page=%s&pre_page=%s&domain_op=100505'
    #(weibo_id,page)
    weibo_comment_url = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=%s&page=%s'
    #(id,page)
    fan_url = 'http://weibo.com/p/100505%s/follow?relate=fans&page=%s'
    old_weibos = []
    DOWNLOAD_DELAY=100


    def __init__(self,*args,**kw):
        super(wbSpider,self).__init__(*args,**kw)
        login_url = self.weibo.login(self.username,self.password)
        if login_url:
            self.start_urls.append(login_url)

    def parse(self, response):
        if response.body.find('feedBackUrlCallBack') != -1:
            print response.body
            data = json.loads(re.search(r'feedBackUrlCallBack\((.*?)\)', response.body, re.I).group(1))
            userinfo = data.get('userinfo', '')
            if len(userinfo):
                log.msg('user id %s' % userinfo['userid'], level=log.INFO)
                url='http://weibo.com/'
                yield Request(url=url,callback=self.parse_page)
            else:
                log.msg('login failed: errno=%s, reason=%s' % (data.get('errno', ''), data.get('reason', '')))



    def parse_page(self,response):
        for weibo in self.old_weibos:
            #print weibo
            comment_url = self.weibo_comment_url % (weibo['weibo_id'],'1')
            yield Request(url=comment_url,callback=self.parse_comments,meta={'weibo_id':weibo['weibo_id'],'user_id':weibo['user_id'],'page':'1'})

        #crawl fans
        #for i in self.user_id:
            #fans_url = self.fan_url % (i,'1')
            #yield Request(url=fans_url,callback=self.parse_fans,meta={'user_id':i,'page':'1'})
        for i in self.user_id:
            weibos_url = self.weibo_url % ('0',i,i,'1','0')
            yield Request(url=weibos_url,callback=self.parse_json_weibo, meta={'page':'1','user_id':i,'part':'1'})

    def parse_fans(self,response):
        response = self.extract_weibo_response(response,'列表')
        sel = HtmlXpathSelector(response)
        fans = sel.select("//div[@class='info_name W_fb W_f14']/a/text()").extract()
        fans_id = sel.select("//div[@class='info_name W_fb W_f14']/a/@usercard").extract()
        id_pattern = re.compile(r'id=(\d+)')
        for i in fans_id:
            fans_id[fans_id.index(i)] = id_pattern.search(i).group(1)
        for f,i in zip(fans,fans_id):
            fan = fanItem()
            fan['user_id'] = response.meta['user_id']
            fan['fan_id'] = i
            fan['fan_name'] = f
            yield fan
        if fans:
            page = str(int(response.meta['page'])+1)
            url = self.fan_url % (response.meta['user_id'],page)
            yield Request(url = url, callback=self.parse_fans,meta={'user_id':response.meta['user_id'],'page':page})



    def parse_json_weibo(self,response):
        response = self.extract_weibo_json_response(response,'weibo')
        sel = HtmlXPathSelector(response)

        weibos_time = sel.select('//div[@class="WB_feed_detail clearfix"]/div[@class="WB_detail"]/div[@class="WB_from S_txt2"]/a[1]/text()').extract()
        weibos = sel.select('//div[@class="WB_feed_detail clearfix"]/div[@class="WB_detail"]/div[@class="WB_text W_f14"]').xpath('string(.)').extract()
        weibo_id = sel.select('//div[@class="WB_cardwrap WB_feed_type S_bg2 "]/@mid|//div[@class="WB_cardwrap WB_feed_type S_bg2 WB_feed_vipcover "]/@mid').extract()
        if response.meta['page'] == '1' and response.meta['part'] == '1':
            First_weibo = True #用来排除置顶微博的干扰
        else:
            First_weibo = False

        for w,t,i in zip(weibos,weibos_time,weibo_id):

            t = self.extract_time(t.strip())

            if First_weibo:
                First_weibo = False
                if not self.is_today(t):
                    continue

            #已爬完当天
            if not self.is_today(t):
                return


            weibo = weiboItem()
            weibo['user_id'] = response.meta['user_id']
            weibo['content'] = w.strip()
            weibo['time'] = t
            weibo['weibo_id'] = i
            yield weibo
            # crawl comment
            comment_url = self.weibo_comment_url % (i,'1')
            yield Request(url=comment_url,callback=self.parse_comments,meta={'weibo_id':i,'user_id':response.meta['user_id'],'page':'1'})
        if weibos:
            if response.meta['part'] == '3':
                page = str(int(response.meta['page'])+1)
                prepage = response.meta['page']
                url = self.weibo_url % ('0',response.meta['user_id'], response.meta['user_id'], page,prepage)
                yield Request(url=url,callback=self.parse_json_weibo,meta={'page':page,'user_id':response.meta['user_id'],'part':'1'})
            elif response.meta['part'] == '2':
                page = response.meta['page']
                prepage = page
                url = self.weibo_url % ('1',response.meta['user_id'],response.meta['user_id'],page,prepage)
                yield Request(url=url,callback=self.parse_json_weibo,meta={'page':page,'user_id':response.meta['user_id'],'part':'3'})
            else:
                page = response.meta['page']
                prepage = page
                url = self.weibo_url % ('0',response.meta['user_id'],response.meta['user_id'],page,prepage)
                yield Request(url=url,callback=self.parse_json_weibo,meta={'page':page,'user_id':response.meta['user_id'],'part':'2'})

    def parse_comments(self,response):
        response = self.extract_weibo_json_response(response,'comment')
        sel = HtmlXPathSelector(response)
        comments = sel.select('//div[@class="list_li S_line1 clearfix"]/div[@class="list_con"]/div[@class="WB_text"]').select('string(.)').extract()
        time = sel.select('//div[@class="list_li S_line1 clearfix"]/div[@class="list_con"]/div[@class="WB_func clearfix"]/div[@class="WB_from S_txt2"]/text()').extract()
        comment_id = sel.select('//div[@class="list_li S_line1 clearfix"]/@comment_id').extract()
        for c,t,i in zip(comments,time,comment_id):
            #格式化时间
            t = self.extract_time(t.strip())
            if not self.is_today(t):
                return

            comment = commentItem()
            comment['user_id'] = response.meta['user_id']
            comment['weibo_id'] = response.meta['weibo_id']
            comment['comment_id'] = i
            comment['content'] = c.strip()
            comment['time'] = t
            yield comment
        if comments:
            page = str(int(response.meta['page'])+1)
            comment_url=self.weibo_comment_url % (response.meta['weibo_id'],page)
            yield Request(url=comment_url,callback=self.parse_comments,meta={'weibo_id':response.meta['weibo_id'], 'user_id':response.meta['user_id'],'page':page})

    #将script中的内容替换response中的body
    def extract_weibo_response(self,response,keyword):

        script_set = response.select('//script')
        script = ''
        for s in script_set:
            try:
                s_text = s.select('text()').extract()[0].encode('utf8').replace(r'\"',r'"').replace(r'\/',r'/')
            except:
                return response
            if s_text.find(keyword) > 0:
                script = s_text
                break
        kw = {'body':script}
        response = response.replace(**kw)

        return response


    def extract_weibo_json_response(self,response,type):
        jsondata = response.body
        data = json.loads(jsondata)
        if type == 'weibo':
            kw={'body':data['data']}
        elif type == 'comment':
            kw={'body':data['data']['html']}
        else:
            kw={'body':response.body}
            print "ERROR"
        response=response.replace(**kw)
        return response

    def extract_time(self,time):
        pattern = re.compile('\d+')
        time = pattern.findall(time)
        if len(time) == 5:
            time = datetime(int(time[0]),int(time[1]),int(time[2]),int(time[3]),int(time[4])).strftime("%Y-%m-%d %H:%M:%S")
            return time
        elif len(time) == 4:
            time = datetime(int(datetime.now().strftime("%Y")),int(time[0]),int(time[1]),int(time[2]),int(time[3])).strftime("%Y-%m-%d %H:%M:%S")
            return time
        elif len(time) == 2:
            time = datetime(int(datetime.now().strftime("%Y")),int(datetime.now().strftime("%m")), int(datetime.now().strftime("%d")),int(time[0]),int(time[1])).strftime("%Y-%m-%d %H:%M:%S")
            return time
        elif len(time) == 1:
            time = (datetime.now()-timedelta(minutes=int(time[0]))).strftime("%Y-%m-%d %H:%M:%S")
            return time
        else:
            print "TIME ERROR"

    def is_today(self,time):
        pattern = re.compile('\d+')
        day = pattern.findall(time)[2]
        if day == datetime.now().strftime('%d'):
            return True
        else:
            return False
