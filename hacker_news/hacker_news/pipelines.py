#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import redis


from scrapy import signals

from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
from models import Deals, db_connect, create_auctions_table

import json
import codecs
from collections import OrderedDict
from geopy.geocoders import Nominatim, GoogleV3


class JsonWithEncodingPipeline(object):

    def __init__(self):
        self.file = codecs.open('data_utf8.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(
            item), ensure_ascii=False, sort_keys=False) + "\n"
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class AuctionsPipeline(object):
    """Livingsocial pipeline for storing scraped items in the database"""

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates deals table.
        """
        engine = db_connect()
        create_auctions_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Save deals in the database.

        This method is called for every item pipeline component.

        """
        session = self.Session()
        print("itemitemitemitemitemitem")
        print(item)
        deal = Deals(**item)

        try:
            ret = session.query(exists().where(
                Deals.url == item['url'])).scalar()
            print(ret)
            if not ret:
                session.add(deal)
                print("added to DB")
                session.commit()
            else:
                print("exists !!")
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item


class LocationPipeline(object):

    def process_item(self, item, spider):
        try:
            #geolocator = Nominatim()
            geolocator = GoogleV3()
            item.setdefault('address', '')
            item.setdefault('neighborhood', '')
            item.setdefault('city', '')
            item.setdefault('region', '')

            locs = [item['address'], item['neighborhood'],
                    item['city'], item['region']]
            for loc in locs:
                if loc:
                    print(loc)
                    location = geolocator.geocode(loc, timeout=5)
                    if location:
                        break

            item['latitude'] = location.latitude
            item['longitude'] = location.longitude
            return item
        except:
            print('Location Problem with ', item['url'])
            raise

            # class RedisPipeline(object):

            #     def __init__(self):
            #         self.r = redis.StrictRedis(host='localhost', port=6379)

            #     def process_item(self, item, spider):
            #         if not item['id']:
            #             print 'no id item!!'

            #         str_recorded_item = self.r.get(item['id'])
            #         final_item = None
            #         if str_recorded_item is None:
            #             final_item = item
            #         else:
            #             ritem = eval(self.r.get(item['id']))
            #             final_item = dict(item.items() + ritem.items())
            #         self.r.set(item['id'], final_item)

            #     def close_spider(self, spider):
            #         return
