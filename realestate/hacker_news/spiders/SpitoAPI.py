import re
import json
import datetime
import socket
import socket
import sys
import os
import pickle

from scrapy.selector import Selector

from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from scrapy.http import Request
from hacker_news.items import *
from hacker_news.xpaths import spitogatos
from scrapy.loader.processors import MapCompose, Join

from hacker_news.models import db_connect, Deals
from MasterSpider import *

from dateutil.parser import parse
from urlparse import urlparse, parse_qs


# a = rent
# v = sell
# othertp1  = New dev
# othertp2 = Student house
# onlypropwith2
# onlypropwith1


# geohash
#"geoHash": "swbbjt00",
#"geoHash": "sx0r4st0",

class SpitoSpider(Master):
    name = "spitoapi"
    allowed_domains = ["spitogatos.gr", "homegreekhome.com"]
    correct_codes = []
    xtypes = {}
    transactions = {}
    xtypes["1"] = 'residential'
    xtypes["2"] = 'commercial'
    xtypes["3"] = 'land'
    xtypes["4"] = 'other'
    transactions["1"] = 'sale'
    transactions["2"] = 'rent'

    # My settings
    def start_requests(self):
        changetor()
        print('Start')

        for k in xrange(2200, 2300, 1):
            url = "http://api.spitogatos.gr/en/spitogatos/mobile/v1/mobile.json/search?cat=1&t=v&start=0&c=" + \
                str(k) + "&searchType=search"
            print url
            yield Request(url, callback=self.get_searchpage_urls)

    def get_searchpage_urls(self, response):
        json_data = json.loads(response.body_as_unicode())
        query = parse_qs(urlparse(response.url).query)
        c = int(query['c'][0])
        cat = int(query['cat'][0])
        start = int(query['start'][0])
        t = query['t'][0]
        n = int(json_data['data']['n'])
        if n > 1:
            if c not in self.correct_codes:
                self.correct_codes.append(c)
        if 1 < start:
            print 3
            return

        start = start + 20
        url = 'http://api.spitogatos.gr/en/spitogatos/mobile/v1/mobile.json/search?cat=' + \
            str(cat) + '&t=' + str(t) + '&start=' + \
            str(start) + '&c=' + str(c) + '&searchType=search'
        print url
        # yield Request(url, callback=self.get_searchpage_urls)
        ls = json_data['data']['ads']
        # if  we go into the each asset
        ids = [l['id'] for l in ls]
        urls = [
            "http://api.spitogatos.gr/en/spitogatos/mobile/v1/mobile.json/detail?skip_active_check=1&rty=ad&aid=" + id for id in ids]

        for url in urls:
            print url
            yield Request(url, callback=self.data_from_details)

        # objs = self.update_data_from_list(ls)
        # for obj in objs:
        #     yield obj

    def update_data_from_list(self, ls):
        objs = []
        self.check_Tor_time()
        for l in ls:
            obj = PropertiesItem()
            # obj['stitogatos_id'] = l['id']
            #+ unique_id = l['features']['5']['value']
            #+ title = Column('title', String)
            obj['price_num'] = l['p']
            obj['description'] = l['desc']

            #+ region = Column('region', String, nullable=True)
            #+ city = Column('city', String, nullable=True)
            obj['neighborhood'] = l['c']
            obj['address'] = l['addr']
            obj['longitude'] = l['ln']
            obj['latitude'] = l['lt']
            obj['property_area_num'] = l['mq']
            obj['property_rooms_num'] = l['s']
            obj['property_buy_or_rent'] = l['contr_nome']

            obj['img_url'] = l['imgs'][0]
            obj['imgs'] = l['imgs']
            # on_site_date = Column('on_site_date', DateTime, nullable=True)
            # views_num = Column('views_num', Integer, nullable=True)

            obj['category_major'] = l['cat']
            obj['category_minor'] = l['t']
            obj['fulltext'] = json.dumps(l)
            # last_update_num = Column('last_update_num', Integer, nullable=True)
            #+ updated_date = Column('updated_date', DateTime, nullable=True)
            obj['geo'] = l['geoHash']
            obj['url'] = l['url']
            # obj['spider', self.name)
            obj['source'] = self.allowed_domains[0]
            # obj['imported_date'] = datetime.now()
            obj['asset_type'] = 'realestate'
            obj['transaction_type'] = 'commercial'
            objs.append(obj)
        return objs

    def data_from_details(self, response):
        self.check_Tor_time()
        obj = PropertiesItem()
        json_data = json.loads(response.body_as_unicode())
        data = json_data['data']
        if not data:
            print "exit"  # return
        l = data['list'][0]
        features = []
        for f in l['features'].values():
            if f['value'] != 'No' and f['value'] != '0':
                features.append(f['key'] + "=" + f['value'])
        obj['features'] = features
        obj['imgs'] = l['imgs']

        obj['contact_legal_name'] = l['agencyDetail']['nome']
        obj['contact_ln'] = l['agencyDetail']['ln']
        obj['contact_lt'] = l['agencyDetail']['lt']
        # contact_name = Column('contact_name', String, nullable=True)
        obj['contact_phone'] = l['agencyDetail']['telefono1']
        obj['contact_mobile'] = l['agencyDetail']['cellulare']
        # contact_email = Column('contact_email', String, nullable=True)
        obj['contact_website'] = l['agencyDetail']['web']
        obj['unique_id'] = l['features']['5']['value']

        obj['price_num'] = l['p']
        obj['description'] = l['desc']

        #+ region = Column('region', String, nullable=True)
        #+ city = Column('city', String, nullable=True)
        obj['neighborhood'] = l['c']
        obj['address'] = l['addr']
        obj['longitude'] = l['ln']
        obj['latitude'] = l['lt']
        obj['property_area_num'] = l['mq']
        obj['property_rooms_num'] = l['s']
        obj['property_buy_or_rent'] = l['contr_nome'].lower()
        obj['img_url'] = l['imgs'][0]
        obj['imgs'] = l['imgs']
        # on_site_date = Column('on_site_date', DateTime, nullable=True)
        # views_num = Column('views_num', Integer, nullable=True)
        obj['construction_year'] = l['features']['70']['value']
        obj['category_major'] = self.xtypes[l['cat']]
        obj['category_minor'] = l['t']
        obj['fulltext'] = json.dumps(l)
        # last_update_num = Column('last_update_num', Integer, nullable=True)
        updated_date = l['features']['80']['value']
        obj['geo'] = l['geoHash']
        obj['url'] = l['url'].split("?")[0]
        # obj['spider', self.name)
        obj['source'] = self.allowed_domains[0]
        obj['imported_date'] = datetime.now()
        obj['asset_type'] = 'realestate'
        obj['transaction_type'] = 'commercial'
        obj['title'] = obj['category_minor'] + " in " + \
            obj['neighborhood'] + " , " + str(obj['price_num'])
        yield obj

    def closed(self, reason):
        print self.correct_codes
        thefile = open('correct_codes.txt', 'w')
        thefile.write("%s\n" % self.correct_codes)
