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
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

# from torchange import *
from scrapy.http import Request
from hacker_news.items import *
from misc.log import *
from misc.spider import CommonSpider
from scrapy.loader.processors import MapCompose, Join
from scrapy.item import Item, Field
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
from hacker_news.models import db_connect, Deals
from torchange import changetor

from dateutil.parser import parse


class CsvSpider(CommonSpider):
    name = "csv"
    allowed_domains = ["realestate.capital.gr"]
    # changetor()
    tor_update_time = datetime.now()

    def start_requests(self):
        print('Start')

        start_urls = []
        with open("xpaths.csv", "rU") as f:
            reader = csv.DictReader(f)
            for line in reader:
                print(line)
                print(line['url'])
                self.meta_field = line
                yield Request(line.pop('url'))
                # yield request
        # return start_urls
    # My settings

    def parse(self, response):
        # Find total number of pages
        self.Session = sessionmaker(bind=db_connect())
        url_first_part = "http://realestate.capital.gr/properties/search-results/"
        last_page_number = response.xpath(
            '//*[@class="transit"]/span[2]/text()').re('[0-9]+')
        # .extract()[0] - > not need re does it

        if last_page_number:
            last_page_number = int(last_page_number[0])
        last_page_number = 2
        print(last_page_number)
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
        page_urls = response.xpath('//*[@class="title"]/a/@href')

        for url in page_urls.extract():
            ret = self.Session().query(exists().where(Deals.url == url)).scalar()
            self.Session().close()

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
        tdelta = datetime.now() - self.tor_update_time
        print(tdelta.total_seconds())
        if (tdelta.total_seconds()) > 30:
            changetor()
            self.tor_update_time = datetime.now()
        print("Looking", response.url)
        # Create the loader using the response
        l = ItemLoader(item=PropertiesItem(), response=response)
        l.default_output_processor = TakeFirst()
        for name, xpath in self.meta_field.iteritems():
            if xpath:
                if name[-3:] == "num":
                    l.add_xpath(name, xpath,
                                MapCompose(
                                    lambda i: i.replace(',', ''), float),
                                re='[,.0-9]+')
                elif name[-4:] == "date":
                    l.add_xpath(name, xpath,
                                MapCompose(
                                    lambda i: parse(i, fuzzy=True), unicode.strip),
                                )
                elif name == "description":
                    l.add_xpath(name, xpath,
                                MapCompose(unicode.strip), Join())
                else:
                    l.add_xpath(name, xpath,
                                MapCompose(unicode.strip, unicode.title))

        # Housekeeping fields
        l.add_value('url', response.url)
        # l.add_value('spider', self.name)
        l.add_value('source', self.allowed_domains[0])
        l.add_value('imported_date', datetime.now())
        l.add_value('asset_type', 'real estate')
        l.add_value('transaction_type', 'commercial')

        return l.load_item()
