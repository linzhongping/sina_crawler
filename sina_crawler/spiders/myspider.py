# -*- coding:utf-8 -*-
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
import urllib
from lxml import etree
from mongoengine.queryset.visitor import Q
from mongoengine import *
from sina_crawler.items import UserItem, EdgeItem, PostItem, CommentItem
from sina_crawler.model import *
import json

conn = connect('weibo_user_post', alias='default', host='127.0.0.1', port=27017, username='', password='')

class SinaSpider(scrapy.Spider):

    name = 'crawlsina'

    # follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid={conid}_-_followers_-_{uid}&page={page}'
    # fans_url = 'https://m.weibo.cn/api/container/getIndex?containerid={conid}_-_fans_-_{uid}&since_id={since_id}'

    fans_url = 'https://m.weibo.cn/api/container/getSecond?containerid={0}_-_FANS&page={1}'
    follow_url = 'https://m.weibo.cn/api/container/getSecond?containerid={0}_-_FOLLOWERS&page={1}'


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
    # yield scrapy.http.FormRequest(login_url, callback=self.after_login,
    # dont_filter=True)

    def start_requests(self):
        topics = ['莫雷NBA']
        for topic in topics:
            t = topic
            encode_url = urllib.quote(t)
            for i in range(1, 10):
                url = 'https://weibo.cn/search/mblog?hideSearchFrame=&keyword=' + \
                    encode_url + '&sort=time&page=' + str(i)
                yield scrapy.http.Request(url, meta={'topic': t}, callback=self.parse)


    def parse(self, response):  # 解析网页
        html = response.body
        topic = response.meta['topic']
        selector = etree.HTML(html)

        for sel in selector.xpath('//div[@class="c"][@id]'):
            post = PostItem()  # 一个post容器
            user = UserItem()  # 一个user容器

            mid = sel.xpath('@id')[0][2:]
            # print(mid)
            murl = 'https://weibo.cn/comment/' + mid
            # print(murl)

            div_len = len(sel.xpath('div'))
            print('此处的div数量', div_len)

            poster_name = sel.xpath('div[1]/a/text()')[0]
            poster_url = sel.xpath('div[1]/a/@href')[0]

            # print(poster_name,poster_url)

            if '/u/' in poster_url:
                uid = poster_url[poster_url.index('/u/') + 3:]
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
            for page in range(1,6):
                # https: // weibo.cn / comment / IljMAy9M2?uid = 1647486362 & rl = 1 & page = 1
                comment_url = murl + '?uid=' + uid + '&page=' + str(page)
                yield scrapy.http.Request(comment_url, meta = {'message_id': mid, 'poster_id':uid}, callback= self.edge_parse)    #爬取评论关系

            user['Uid'] = uid
            user['UserName'] = poster_name
            user['UserUrl'] = 'https://m.weibo.cn/profile/info?uid=' + uid
            yield scrapy.http.Request('https://m.weibo.cn/profile/info?uid=' + uid, meta={'user_objective': user}, callback=self.user_parse)




    def edge_parse(self, response):
        print 'edge_parse'
        html = response.body
        selector = etree.HTML(html)

        mid = response.meta['message_id']  # 主贴id
        uid = response.meta['poster_id']  # 主用户id
        print len(selector.xpath('//div[@class="c"][contains(@id,"C_")]'))
        for sel in selector.xpath('//div[@class="c"][contains(@id,"C_")]'):
            edge = EdgeItem()
            comment = CommentItem()
            user = UserItem()

            cid = sel.xpath('@id')[0][2:]

            cer_url = sel.xpath('a[1]/@href')[0]
            cer_name = sel.xpath('a[1]/text()')[0]
            # print(cer_url,cer_name)
            if '/u/' in cer_url:
                cerid = cer_url[cer_url.index('/u/') + 3:]  # 评论者id
            else:
                continue
            content_list = sel.xpath('span[@class="ctt"]//text()')
            content = ''.join(content_list)
            if len(content) < 30:
                continue

            comment['Cid'] = cid
            comment['Uid'] = cerid
            comment['Content'] = content
            comment['Mid'] = mid

            yield comment
            edge['Source'] = uid
            edge['Target'] = cerid
            yield edge
            user['Uid'] = cerid
            user['UserUrl'] = 'https://m.weibo.cn/profile/info?uid=' + cerid
            user['UserName'] = cer_name

            yield scrapy.http.Request('https://m.weibo.cn/profile/info?uid=' + cerid, meta={'user_objective': user}, callback=self.user_parse)


    def user_parse(self, response):

        user = response.meta['user_objective']
        d = json.loads(response.body)['data']
        user_info = d['user']

        user['ProfileImg'] = user_info['profile_image_url']
        user['FollowerNum'] = user_info['follow_count']
        user['FansNum'] = user_info['followers_count']

        # 获取container_id
        fans_url = d['fans']
        follow_url = d['follow']

        def get_container_id(s):
            import re
            return re.findall(r'[0-9]\d*', s)[0]

        container_id = get_container_id(fans_url)

        user['ContainerId'] = container_id

        yield user # 先生成一个user数据库对象


        # fans_url = 'https://m.weibo.cn/api/container/getSecond?containerid={conid}_-_FANS&page={page}'
        # follow_url = 'https://m.weibo.cn/api/container/getSecond?containerid={conid}_-_FOLLOWERS&page={page}'
        for i in range(1, 5):
            yield scrapy.http.Request(self.fans_url.format(container_id,str(i)), meta={'user_objective': user}, callback=self.parse_fans)

        for j in range(1, 5):
            yield scrapy.http.Request(self.follow_url.format(container_id,str(j)), meta={'user_objective': user}, callback=self.parse_follow)


    def parse_fans(self, response):
        '''
        获取粉丝列表,动态更新User Table的fans list
        :param response:
        :return:
        '''
        user = response.meta['user_objective']
        d = json.loads(response.body)['data']
        fans_dict_list = d['cards']
        l = []
        for _ in fans_dict_list:
            l.append(str(_['user']['id']))
        print '粉丝列表:', l
        # 动态更新
        u = User.objects(uid = user['Uid'])[0]
        tmp = u.fansList
        tmp += l
        tmp = list(set(tmp))
        u.update(fansList=tmp)


    def parse_follow(self, response):
        '''
        获取关注列表,动态更新User Table的followlist
        :param response:
        :return:
        '''
        user = response.meta['user_objective']
        d = json.loads(response.body)['data']
        follows_dict_list = d['cards']
        l = []
        for _ in follows_dict_list:
            l.append(str(_['user']['id']))
        print '关注列表:',l
        # 动态更新
        u = User.objects(uid=user['Uid'])[0]
        tmp = u.followsList
        tmp += l
        tmp = list(set(tmp))
        u.update(followsList=tmp)
