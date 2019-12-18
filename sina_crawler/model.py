# -*- coding: utf-8 -*-
from mongoengine import *
import datetime

class User(Document):
    _id = ObjectIdField(primary_key=True)
    uid = StringField(required=True, unique=True)
    home_url = StringField(max_length=256,default='')
    username = StringField(max_length=128)
    followers_num = IntField(default=0)
    userProfile = StringField(max_length=256)
    fans_num = IntField(default=0)
    followerList = ListField(StringField(),default=[])  # 关注人列表
    fansList = ListField(StringField(),default=[])  # 粉丝列表


class Edge(Document):
    _id = ObjectIdField(primary_key=True)
    sourceUid = StringField(required=True)
    targetUid = StringField(required=True)

class Post(Document):
    _id = ObjectIdField(primary_key=True)
    topic = StringField()  # 属于某个子话题
    uid = StringField() # 用户id
    mid = StringField()  # 文章id
    pUrl = StringField()
    Content = StringField()  # 帖子内容