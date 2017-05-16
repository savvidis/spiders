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
from hacker_news.helper_lists import correct_codes


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
    transactions["v"] = 'sale'
    transactions["a"] = 'rent'
    ls = []
    hunt = 2
    # My settings

    def start_requests(self):
        changetor()
        print('Start')
        import pdb
        for t in self.transactions.keys():
            for k in self.xtypes.keys():
                for c in correct_codes:
                    url = "http://api.spitogatos.gr/en/spitogatos/mobile/v1/mobile.json/search?cat=" + str(k) + "&t=" + t + "&start=0&c=" + \
                        str(c) + "&searchType=search"
                    print url
                    yield Request(url, callback=self.get_searchpage_urls)

    def get_searchpage_urls(self, response):
        self.check_Tor_time()
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
        if start < n and n > 20:
            start = start + 20
            url = 'http://api.spitogatos.gr/en/spitogatos/mobile/v1/mobile.json/search?cat=' + \
                str(cat) + '&t=' + str(t) + '&start=' + \
                str(start) + '&c=' + str(c) + '&searchType=search'
            print url
            self.ls = self.ls + json_data['data']['ads']
            print(len(self.ls))
            yield Request(url, callback=self.get_searchpage_urls)
        else:
            if self.hunt == 1:
                # #1
                  #  ------------ if  we go into the each asset
                for l in self.ls:
                    url = "http://api.spitogatos.gr/en/spitogatos/mobile/v1/mobile.json/detail?skip_active_check=1&rty=ad&aid=" + \
                        l['id']
                    print url
                    self.ls.remove(l)
                    yield Request(url, callback=self.data_from_details)

            # 2
            # ------------ if  we go just to update
            elif self.hunt == 2:
                for l in self.ls:
                    obj = PropertiesItem()
                    obj['unique_id'] = l['id']
                    obj['price_num'] = l['p']
                    obj['description'] = l['desc']
                    obj['neighborhood'] = l['c']
                    obj['address'] = l['addr']
                    obj['longitude'] = l['ln']
                    obj['latitude'] = l['lt']
                    obj['property_area_num'] = l['mq']
                    obj['property_rooms_num'] = l['s']
                    obj['property_buy_or_rent'] = l['contr_nome'].lower()
                    try:
                        obj['img_url'] = l['imgs'][0]
                    except Exception as e:
                        obj['img_url'] = None

                    obj['imgs'] = l['imgs']
                    obj['category_major'] = self.xtypes[l['cat']]
                    obj['category_minor'] = l['t']
                    obj['geo'] = l['geoHash']
                    obj['url'] = l['url'].split("?")[0]
                    obj['updated_date'] = datetime.fromtimestamp(
                        float(l['last_mod']))
                    obj['source'] = self.allowed_domains[0]
                    obj['asset_type'] = 'realestate'
                    obj['transaction_type'] = 'commercial'
                    obj['source'] = self.allowed_domains[0]
                    obj['imported_date'] = datetime.now()
                    obj['title'] = obj['category_minor'] + " in " + \
                        obj['neighborhood'] + ", sqm " + \
                        str(obj['property_area_num']) + \
                        " , EUR " + str(obj['price_num'])
                    self.ls.remove(l)
                    yield obj

    def data_from_details(self, response):
        self.check_Tor_time()
        obj = PropertiesItem()
        json_data = json.loads(response.body_as_unicode())
        data = json_data['data']
        if not data:
            return
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
        obj['contact_phone'] = l['agencyDetail']['telefono1']
        obj['contact_mobile'] = l['agencyDetail']['cellulare']
        obj['contact_website'] = l['agencyDetail']['web']
        obj['unique_id'] = l['features']['5']['value']
        obj['price_num'] = l['p']
        obj['description'] = l['desc']
        obj['neighborhood'] = l['c']
        obj['address'] = l['addr']
        obj['longitude'] = l['ln']
        obj['latitude'] = l['lt']
        obj['property_area_num'] = l['mq']
        obj['property_rooms_num'] = l['s']
        obj['property_buy_or_rent'] = l['contr_nome'].lower()
        try:
            obj['img_url'] = l['imgs'][0]
        except Exception as e:
            obj['img_url'] = None
        obj['imgs'] = l['imgs']
        obj['construction_year'] = l['features']['70']['value']
        obj['category_major'] = self.xtypes[l['cat']]
        obj['category_minor'] = l['t']
        obj['fulltext'] = json.dumps(l)
        obj['updated_date'] = datetime.fromtimestamp(float(l['last_mod']))
        obj['geo'] = l['geoHash']
        obj['url'] = l['url'].split("?")[0]
        obj['source'] = self.allowed_domains[0]
        obj['imported_date'] = datetime.now()
        obj['asset_type'] = 'realestate'
        obj['transaction_type'] = 'commercial'
        obj['title'] = obj['category_minor'] + " in " + \
            obj['neighborhood'] + ", sqm " + \
            str(obj['property_area_num']) + " , EUR " + str(obj['price_num'])

        yield obj

    def closed(self, reason):
        print self.correct_codes
        thefile = open('correct_codes.txt', 'w')
        thefile.write("%s\n" % self.correct_codes)
