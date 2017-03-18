import re
import json
import urllib
import pdb
from datetime import datetime
import urlparse
import socket
import csv

import socket
import sys

from scrapy.selector import Selector
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

# from torchange import *
from scrapy.http import Request
from hacker_news.items import *
from hacker_news.xpaths import tameio

#from misc.spider import CommonSpider
from scrapy.loader.processors import MapCompose, Join
# from scrapy.item import Item, Field
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import exists
from hacker_news.models import db_connect, Deals
from MasterSpider import *

from dateutil.parser import parse


class TameioSpider(Master):
    name = "nome"
    allowed_domains = ["deltio.tnomik.gr"]
    start_urls = [
        "https://deltio.tnomik.gr",
    ]

    # My settings
    # def start_requests(self):
    # pass
    # changetor()
    #     print('Start')
    # self.source_xpaths = tameio
    # self.tor_update_time = datetime.now()

    # My Starting point
    def parse(self, response):
        changetor()
        self.source_xpaths = tameio
        self.tor_update_time = datetime.now()
        # Find total number of pages
        print("1")
        # url_first_part = self.source_xpaths.pop('url')
        print("2")
        for i in xrange(100):
            url = response.urljoin("/details?id=" + str(i))
            print(url)
            yield Request(url, callback=self.checkdb)

    def checkdb(self, response):
        # Get item URLs and yield Requests
        url = response.url
        ret = self.entry_exists(Deals, url)
        if not ret:
            print("Starting -- > ", url)
            yield Request(urlparse.urljoin(response.url, url),
                          callback=self.parse_item)
        else:
            print("******* URL already in DB *******")

    def parse_item(self, response):
        """ This function parses a property page.
        @url http://realestate.capital.gr/properties/homes/diamerisma-148-0tm.-168504.html
        @returns items 1
        @scrapes title price description area address
        @scrapes url project spider server date
        """
        self.check_Tor_time()
        print("Looking", response.url)
        # Create the loader using the response
        l = ItemLoader(item=PropertiesItem(), response=response)
        l.default_output_processor = TakeFirst()
        self.fill_from_Json(l)

        # Housekeeping fields
        l.add_value('url', response.url)
        # l.add_value('spider', self.name)
        l.add_value('source', self.allowed_domains[0])
        l.add_value('imported_date', datetime.now())
        l.add_value('asset_type', 'real estate')
        l.add_value('transaction_type', 'auction')
        return l.load_item()
