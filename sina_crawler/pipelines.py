# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sina_crawler.model import *
from bson.objectid import ObjectId
from sina_crawler.items import *
import traceback


class SinaCrawlerPipeline(object):

    def process_item(self, item, spider):

        if isinstance(item, UserItem):
            obj_id = ObjectId()
            u = User(
                _id=obj_id,
                uid=item['Uid'],
                container_id=item['ContainerId'],
                home_url=item['UserUrl'],
                username=item['UserName'],
                userProfile=item['ProfileImg'],
                followerNum=item['FollowerNum'],
                fansNum=item['FansNum']
            )
            try:
                u.save()
                print 'insert 1 user'
            except:
                traceback.print_exc()

        if isinstance(item, PostItem):
            obj_id = ObjectId()
            p = Post(
                _id=obj_id,
                topic=item['Topic'],
                uid=item['Uid'],
                mid=item['Mid'],
                purl=item['M_Url'],
                content=item['Content'],
            )
            try:
                p.save()
                print 'insert 1 post'
            except:
                traceback.print_exc()

        if isinstance(item, EdgeItem):
            obj_id = ObjectId()
            e = Edge(
                _id=obj_id,
                sourceUid=item['Source'],
                targetUid=item['Target']
            )
            try:
                e.save()
                print 'insert 1 edge'
            except:
                traceback.print_exc()

        if isinstance(item, CommentItem):

            obj_id = ObjectId()
            c = Comment(
                _id=obj_id,
                cid=item['Cid'],
                mid=item['Mid'],
                uid=item['Uid'],
                content=item['Content']
            )
            try:
                c.save()
                print 'insert 1 comment'
            except:
                traceback.print_exc()

        return item
