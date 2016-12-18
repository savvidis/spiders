import re
import json
import urllib
import pdb
import datetime
import urlparse
import socket
import csv
import socket
import sys
import httplib2
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
from misc.log import *
from misc.spider import CommonSpider
from scrapy.loader.processors import MapCompose, Join
# from scrapy.item import Item, Field
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import exists
from hacker_news.models import db_connect, Deals
from MasterSpider import *

from dateutil.parser import parse


class CsvSpider(Master):
    name = "spito"
    allowed_domains = ["homegreekhome.com"]

    xtypes = [
        "residential",
        # "land",
        # "new-residential",
        # "commercial"
    ]

    transactions = [
        "sale",
        # "rent"
    ]
    # My settings

    def start_requests(self):
        changetor()
        print('Start')
        with open('xpaths.json') as data_file:
            dict_source = json.load(data_file)[1]   # First
            self.source_xpaths = dict_source
            # print(self.source_xpaths)

        for xtype in self.xtypes:
            for tran in self.transactions:
                for i in range(100, 101):
                    url = "http://www.homegreekhome.com/en/search/results/" + \
                        xtype + "/" + tran + "/r" + \
                        str(i) + "/m" + str(i) + "m/"
                    print(url)
                    yield Request(url, callback=self.get_searchpage_urls)

    def get_searchpage_urls(self, response):
        if response.status != 200:
            print(response.status)
            return
        print(response.url)
        # get last page number
        last_page_number = response.xpath(
            '//*[@id="pagination"]/ul/li[9]/a/@href').re('/offset_([0-9]+)')
        print(last_page_number)
        offset_pages = 0
        if last_page_number:
            last_page_number = int(last_page_number[0])
            try:
                offset_pages = last_page_number / 10
            except Exception as e:
                print(e)

        print(offset_pages)

        for j in range(0, offset_pages + 1):
            if j == 0:
                yield Request(response.url, callback=self.parse_listing_results_page)
            else:
                last_part = "offset_" + str(int(j) * 10) + "/"
                new_url = response.url + last_part
                print(new_url)
                yield Request(new_url,
                              callback=self.parse_listing_results_page)

    def parse_listing_results_page(self, response):
        # Get item URLs and yield Requests
        print("here")
        page_urls = response.xpath(
            '//*[@id="searchDetailsListings"]/div/div/a/@href').extract()
        print(page_urls)
        for url in page_urls:
            print(url)
            if re.search('(.+)\?', url):
                nurl = re.search('(.+)\?', url).group(1)
            else:
                nurl = ""
            print(nurl)
            ret = self.entry_exists(Deals, nurl)
            if not ret:
                print("Starting -- > ", nurl)
                print(urlparse.urljoin(response.url, nurl))
                yield Request(urlparse.urljoin(response.url, nurl),
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
        l.add_value('transaction_type', 'commercial')
        return l.load_item()
