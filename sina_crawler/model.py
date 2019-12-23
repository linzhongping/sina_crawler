# -*- coding: utf-8 -*-
from mongoengine import *
from mongoengine.context_managers import switch_db
import datetime

class User(Document):
    _id = ObjectIdField(primary_key=True)
    uid = StringField(required=True, unique=True)
    container_id = StringField(default='')
    home_url = StringField(max_length=256,default='')
    username = StringField(max_length=128)
    userProfile = StringField(max_length=256)
    followerNum = IntField(default=0)
    fansNum = IntField(default=0)

    followsList = ListField(StringField(),default=[])  # 关注人列表
    fansList = ListField(StringField(),default=[])  # 粉丝列表


class Edge(Document):
    _id = ObjectIdField(primary_key=True)
    sourceUid = StringField(required=True)
    targetUid = StringField(required=True, unique_with='sourceUid')

class Post(Document):
    _id = ObjectIdField(primary_key=True)
    topic = StringField()  # 属于某个子话题
    uid = StringField() # 用户id
    mid = StringField(unique=True)  # 文章id
    purl = StringField()
    content = StringField()  # 帖子内容

class Comment(Document):
    _id = ObjectIdField(primary_key=True)
    cid = StringField(required=True,unique=True)
    mid = StringField(required=True)
    uid = StringField(required=True)
    content = StringField(max_length=256)