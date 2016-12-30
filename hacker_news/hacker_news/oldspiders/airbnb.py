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

from scrapy.http import Request
from hacker_news.items import *
from misc.log import *
from misc.spider import CommonSpider
from scrapy.loader.processors import MapCompose, Join


class Airbnb(CommonSpider):
    name = "airbnb"
    allowed_domains = ["capital.gr"]
    start_urls = [
        "http://realestate.capital.gr/properties/search-results.html",
    ]
    # To see my settings only once

    # def __init__(self, *args, **kwargs):
    #     super(CrawlSpider, self).__init__(*args, **kwargs)()
    #     print("Existing settings:")
    #     for k in self.settings.attributes.keys():
    #         print(k, self.settings.attributes[k])

    # My settings
    def parse(self, response):
        # Find total number of pages
        url_first_part = "http://realestate.capital.gr/properties/search-results/"
        last_page_number = int(response
                               .xpath('//*[@class="transit"]/span[2]/text()')
                               # .extract()[0] - > not need re does it
                               .re('[0-9]+')[0]
                               )
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
                yield Request(page_url, callback=self.parse_listing_results_page)

    def parse_listing_results_page(self, response):
        # Get item URLs and yield Requests
        page_urls = response.xpath('//*[@class="title"]/a/@href')
        for url in page_urls.extract():
            print("Starting -- > ", url)
            yield Request(urlparse.urljoin(response.url, url),
                          callback=self.parse_item)

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
