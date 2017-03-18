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
from hacker_news.xpaths import capital

# from torchange import *
from scrapy.http import Request
from hacker_news.items import *

# from misc.spider import CommonSpider
from scrapy.loader.processors import MapCompose, Join
# from scrapy.item import Item, Field
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import exists
from hacker_news.models import db_connect, Deals
from MasterSpider import *

from dateutil.parser import parse


class CsvSpider(Master):

    cat_major_list = [
        "homes",
        "land",
        "commercial",
    ]

    transactions_list = [
        "sale",
        "rent"
    ]

    minor_homes = [
        "apartments",
        "houses",
        "splitlevels",
        "villas"
    ]

    minor_land = [
        "parcel",
        "field"
    ]
    minor_commercial = [
        "offices",
        "businness-buildings",
        "hotels",
        "industrial-spaces"
    ]

    name = "clean"
    allowed_domains = ["realestate.capital.gr"]
    start_urls = [
        'http://realestate.capital.gr/properties/']
    # My settings

    def __init__(self):
        # changetor()
        print('Start')
        self.source_xpaths = capital

     # ------ Test -----
    def start_requests(self):
        changetor()
        print('Start')
        yield Request('file://127.0.0.1/users/sabbidis/Downloads/capital_demo.html',
                      callback=self.parse_item)
     # ----- End ------

    # def start_requests(self):
    #     for cat_major in self.cat_major_list:
    #         if cat_major == "homes":
    #             for cat_minor in self.minor_homes:
    #                 self.xcategories = (cat_major, cat_minor)
    #                 print(self.xcategories)
    #                 url = "http://realestate.capital.gr/properties/" + cat_major + "/" + cat_minor
    #                 yield Request(url, callback=self.parse)
    #         elif cat_major == "land":
    #             for cat_minor in self.minor_land:
    #                 self.xcategories = (cat_major, cat_minor)
    #                 print(self.xcategories)
    #                 url = "http://realestate.capital.gr/properties/" + cat_major + "/" + cat_minor
    #                 yield Request(url, callback=self.parse)
    #         else:
    #             for cat_minor in self.minor_commercial:
    #                 self.xcategories = (cat_major, cat_minor)
    #                 url = "http://realestate.capital.gr/properties/" + cat_major + "/" + cat_minor
    #                 yield Request(url, callback=self.parse)

    # My Starting point
    def parse(self, response):
        # Find total number of pages
        url_first_part = response.url
        print(response.url)
        print('2.5')
        last_page_number = response.xpath(
            '//*[@class="transit"]/span[2]/text()').re('[0-9]+')
        print('2')

        if last_page_number:
            last_page_number = int(last_page_number[0])
        last_page_number = 1
        if last_page_number < 1:
            print("last < 1")
            # abort the search if there are no results
            return
        else:
            # otherwise loop over all pages and scrape!
            page_urls = [url_first_part + "index" +
                         str(pageNumber) + ".html" for pageNumber in range(1, last_page_number + 1)]
            for page_url in page_urls:
                print(page_url)
                yield Request(
                    page_url, callback=self.parse_listing_results_page)

    def parse_listing_results_page(self, response):
        # Get item URLs and yield Requests
        print('3')

        page_urls = response.xpath('//*[@class="title"]/a/@href')

        for url in page_urls.extract():
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
        try:
            self.fill_from_Json(l)
        except Exception as e:
            print(e)
        try:
            on_site_date = re.search(
                r'(\d\d-\d\d\d\d)', l.get_collected_values('img_url')[0]).group(0)
            ddate = datetime.strptime(on_site_date, '%m-%Y')
            l.add_value('on_site_date', ddate)
        except Exception as e:
            print(e)

        # l.replace_value('category_major', self.xcategories[0])
        # l.replace_value('category_minor', self.xcategories[1])

        # Housekeeping fields
        l.add_value('url', response.url)
        # l.add_value('spider', self.name)
        l.add_value('source', self.allowed_domains[0])
        l.add_value('imported_date', datetime.now())
        l.add_value('asset_type', 'real estate')
        l.add_value('transaction_type', 'commercial')
        print(l)
        return l.load_item()
