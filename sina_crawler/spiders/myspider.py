# -*- coding:utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
import urllib
from lxml import etree
from mongoengine.queryset.visitor import Q
from sina_crawler.items import UserItem,EdgeItem,PostItem,CommentItem
import json
class SinaSpider(scrapy.Spider):

    name = 'crawlsina'
    # 获取微博主贴和uid
    # def start_requests(self):
    #     start_url = 'http://weibo.cn/pub/'
    #     yield scrapy.http.Request(start_url,callback=self.pre_login)
    #
    # def pre_login(self,response):
    #     pre_url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt='
    #     yield scrapy.http.Request(pre_url, callback=self.login)
    #
    # def login(self,response):
    #
    #     login_url = 'https://passport.weibo.cn/sso/login'
    #     yield scrapy.http.FormRequest(login_url, callback=self.after_login, dont_filter=True)

    def start_requests(self):
        topics = ['莫雷','休斯顿火箭','亚当萧华']
        for topic in topics:
            t = topic
            encode_url = urllib.quote(t)
            for i in range(1,2):
                url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword='+encode_url+'&sort=time&page=' + str(i)
                yield scrapy.http.Request(url, meta={'topic':t},callback = self.parse)
            break

    def parse(self, response): # 解析网页
        html = response.body
        topic = response.meta['topic']
        selector = etree.HTML(html)

        for sel in selector.xpath('//div[@class="c"][@id]'):
            post = PostItem() # 一个post容器
            user = UserItem() # 一个user容器

            mid = sel.xpath('@id')[0][2:]
            # print(mid)
            murl = 'https://weibo.cn/comment/' + mid
            # print(murl)




            div_len = len(sel.xpath('div'))
            print('此处的div数量',div_len)

            poster_name = sel.xpath('div[1]/a/text()')[0]
            poster_url = sel.xpath('div[1]/a/@href')[0]

            # print(poster_name,poster_url)

            if '/u/' in poster_url:
                uid = poster_url[poster_url.index('/u/') + 3 : ]
            else:
                continue

            content_list = sel.xpath('div[1]/span[@class="ctt"]//text()')
            content = ''.join(content_list)
            # print(content[1:])

            post['Topic'] = topic
            post['Uid'] = uid
            post['Content'] = content[1:]
            post['Mid'] = mid
            post['M_Url'] = murl
            yield post
            # yield scrapy.http.Request(murl, meta = {'message_id': mid, 'poster_id':uid}, callback= self.edge_parse)   #爬取评论关系

            user['Uid'] = uid
            user['UserName'] = poster_name
            user['UserUrl'] = poster_url
            yield scrapy.http.Request('https://m.weibo.cn/profile/info?uid=' + uid, meta={'user_objective':user}, callback = self.user_parse)

            break

    def edge_parse(self,response):

        html = response.body
        selector = etree.HTML(html)

        mid = response.meta['message_id'] # 主贴id
        uid = response.meta['poster_id'] # 主用户id

        for sel in selector.xpath('//div[@class="c"][contains(@id,"C_")]'):
            edge = EdgeItem()
            comment = CommentItem()
            user = UserItem()

            cid = sel.xpath('@id')[0][2:]


            cer_url = sel.xpath('a[1]/@href')[0]
            cer_name = sel.xpath('a[1]/text()')[0]
            # print(cer_url,cer_name)
            if '/u/' in cer_url:
                cerid = cer_url[cer_url.index('/u/') + 3 : ]  # 评论者id
            else:
                continue
            content_list = sel.xpath('span[@class="ctt"]//text()')
            content = ''.join(content_list)
            # if len(comment) < 30:
            #     continue

            comment['Cid'] = cid
            comment['Uid'] = cerid
            comment['Content'] = content
            comment['Mid'] = mid
            # print(cid,cerid,content,mid)

            edge['Source'] = uid
            edge['Target'] = cerid


            user['Uid'] = cerid
            user['UserUrl'] = 'https://weibo.cn' + cer_url
            user['UserName'] = cer_name

            yield edge, comment
            yield scrapy.http.Request('https://m.weibo.cn/profile/info?uid=' + cer_url, meta={'user_objective':user}, callback = self.user_parse)
            break


    def user_parse(self,response):
        print response.body
        user = response.meta['user_objective']
        d = json.loads(response.body)['data']
        user_info = d['user']

        user['ProfileImg'] = user_info['profile_image_url']
        user['FollowerNum'] = user_info['follow_count']
        user['FansNum'] =  user_info['followers_count']

        fans_url = d['fans']
        follow_url = d['follow']

        fans_url = 'https://m.weibo.cn/' + fans_url + '&page='
        follow_url = 'https://m.weibo.cn/' + follow_url + '&page='

        for i in range(1,5):
            yield scrapy.http.Request(fans_url, meta = {'user_objective': user}, callback = self.parse_fans)

        for j in range(1,5):
            yield  scrapy.http.Request(follow_url, meta = {'user_objective':user},callback=self.parse_follows)









