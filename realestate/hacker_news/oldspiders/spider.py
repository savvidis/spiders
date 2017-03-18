import re
import json
import urllib
import pdb
import datetime
import urlparse
import socket

from scrapy.selector import Selector
try:
    from scrapy.spiders import Spider
except:
    from scrapy.spiders import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader


from hacker_news.items import *
from misc.log import *
from misc.spider import CommonSpider
from scrapy.loader.processors import MapCompose, Join


from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists


class hacker_newsSpider(CommonSpider):
    name = "hacker_news"
    allowed_domains = ["capital.gr"]
    start_urls = [
        "http://realestate.capital.gr/properties/search-results.html",
        # "http://realestate.capital.gr/",
    ]

    # Rules for horizontal and vertical crawling
    rules = (
        Rule(LinkExtractor(
            restrict_xpaths='//*[@id="controller_area"]/ul/li[2]/a')),
        Rule(LinkExtractor(
            restrict_xpaths='//*[@class="title"]/a'), callback='parse_item'),
    )

    def parse_item(self, response):
        """ This function parses a property page.
        @url http://realestate.capital.gr/properties/homes/diamerisma-148-0tm.-168504.html
        @returns items 1
        @scrapes title price description area address 
        @scrapes url project spider server date
        """
        print("Looking", response.url)
        # Create the loader using the response
        l = ItemLoader(item=PropertiesItem(), response=response)

        # Load fields using XPath expressions
        l.add_xpath('title', '//*[@id="area_listing"]/h1/text()',
                    MapCompose(unicode.strip, unicode.title))
        l.add_xpath('price', '//*[@id="df_field_price"]/span/text()',
                    MapCompose(lambda i: i.replace(',', ''), float),
                    re='[,.0-9]+')
        l.add_xpath('area', '//*[@id="df_field_square_meters"]/div[2]/text()',
                    MapCompose(lambda i: i.replace(',', ''), float),
                    re='[,.0-9]+')
        l.add_xpath('description', '//*[@id="df_field_additional_information"]/div[2]/text()',
                    MapCompose(unicode.strip), Join())
        l.add_xpath('address',
                    '//*[@id="df_field_address"]/div[2]/text()',
                    MapCompose(unicode.strip))

        # Housekeeping fields
        l.add_value('url', response.url)
        l.add_value('project', self.settings.get('BOT_NAME'))
        l.add_value('spider', self.name)
        l.add_value('server', socket.gethostname())
        # l.add_value('date', datetime.datetime.now())
        print(l.load_item())
        return l.load_item()
