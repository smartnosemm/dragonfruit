# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import boto3
from time import sleep
from boto3.dynamodb.conditions import Key, Attr

class ProductPipeline(object):

    def __init__(self):
        pass

    def open_spider(self, spider):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        self.productTable = self.dynamodb.Table('Costco_Products_Clearance')

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.productTable.put_item(Item=dict(item))
        return item
