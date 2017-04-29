import re
import json
import urllib
import pdb
from datetime import datetime
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

from scrapy.loader.processors import MapCompose, Join
from hacker_news.torchange import changetor

from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
from hacker_news.models import db_connect, Deals
from dateutil.parser import parse


class Master(CrawlSpider):

    tor_update_time = datetime.now()

    @classmethod
    def check_Tor_time(self):
        tdelta = datetime.now() - self.tor_update_time
        print(tdelta.total_seconds())
        if (tdelta.total_seconds()) > 30:
            changetor()
            self.tor_update_time = datetime.now()

    def fill_from_Json(self, l):
        xdic = self.source_xpaths
        for name in xdic.keys():
            if xdic[name] != '':
                if name[-4:] and name[-4:] == "html":
                    try:
                        l.add_xpath(name, xdic[name])
                    except Exception as e:
                        print "In Html", e

                if name[-3:] and name[-3:] == "num":
                    try:
                        l.add_xpath(name, xdic[name],
                                    MapCompose(
                                        lambda i: i.replace(',', ''), float),
                                    re='[,.0-9]+')
                    except Exception as e:
                        print e
                elif name[-4:] and name[-4] == "date":

                    l.add_xpath(name, xdic[name],
                                MapCompose(
                                    lambda i: parse(i, fuzzy=True)),
                                )
                elif xdic[name][-5:] and xdic[name][-5:] == "style":
                    l.add_xpath(name, xdic[name],
                                re="background-image.*'(.+)'"
                                )
                elif name == "description":
                    l.add_xpath(name, xdic[name],
                                MapCompose(unicode.strip), Join())
                else:
                    l.add_xpath(name, xdic[name],
                                MapCompose(unicode.strip, unicode.title))
            else:
                l.add_value(name, "")

    @classmethod
    def entry_exists(self, Deals, url):
        self.Session = sessionmaker(bind=db_connect())
        ret = self.Session().query(exists().where(Deals.url == url)).scalar()
        self.Session().close()
        return ret
