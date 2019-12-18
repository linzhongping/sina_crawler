# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    Topic = scrapy.Field() # 属于某个子话题
    Uid = scrapy.Field()   # 用户id
    Mid = scrapy.Field()   # 文章id
    M_Url = scrapy.Field()

    Content = scrapy.Field() # 帖子内容

class EdgeItem(scrapy.Item):
    # non direct edges
    Source = scrapy.Field() # user_id 1
    Target = scrapy.Field() # user_id 2


class UserItem(scrapy.Item):

    Uid = scrapy.Field()
    UserUrl = scrapy.Field()
    UserName = scrapy.Field()

    # 需要人来确定
    ProfileImg = scrapy.Field()
    FollowerNum = scrapy.Field()
    FansNum = scrapy.Field()
    FollowerList = scrapy.Field() # 关注列表 按照排序
    FansList = scrapy.Field() # 粉丝列表


class CommentItem(scrapy.Item):

    Cid = scrapy.Field()
    Mid = scrapy.Field() # 指向某条帖子
    Uid = scrapy.Field() # 评论人信息
    Content = scrapy.Field() # 评论内容




