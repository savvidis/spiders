#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding=UTF-8
import scrapy
import urlparse
from scrapy.http import Request
from scrapy.utils.response import get_base_url
from urlparse import urlparse, urljoin
from vacancies.items import JobItem

# We need that in order to force Slovenian pages instead of English pages. It happened at "http://www.g-gmi.si/gmiweb/" that only English pages were found and no Slovenian.
#from scrapy.conf import settings
#settings.overrides['DEFAULT_REQUEST_HEADERS'] = {'Accept':'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8','Accept-Language':'sl',}
# settings.overrides['DEFAULT_REQUEST_HEADERS'] =
# {'Accept':'text/html,application/xhtml+xml;q=0.9,*/*;q=0.8','Accept-Language':'sl','en':q=0.8,}


class JobSpider(scrapy.Spider):

    name = "jobs"

    # Test sample of SLO companies
    start_urls = [

        "http://www.g-gmi.si/gmiweb/",
    ]
    # Result of the programme is this list of job vacancies webpages.
    jobs_urls = []

    def parse(self, response):

        response.selector.remove_namespaces()

        # We take all urls, they are marked by "href". These are either
        # webpages on our website either new websites.
        urls = response.xpath('//@href').extract()

        # Base url.
        base_url = get_base_url(response)

        # Loop through all urls on the webpage.
        for url in urls:

            # If url represents a picture, a document, a compression ... we
            # ignore it. We might have to change that because some companies
            # provide job vacancies information in PDF.
            if url.endswith((
                # images
                '.jpg', '.jpeg', '.png', '.gif', '.eps', '.ico', '.svg', '.tif', '.tiff',
                '.JPG', '.JPEG', '.PNG', '.GIF', '.EPS', '.ICO', '.SVG', '.TIF', '.TIFF',

                # documents
                '.xls', '.ppt', '.doc', '.xlsx', '.pptx', '.docx', '.txt', '.csv', '.pdf', '.pd',
                '.XLS', '.PPT', '.DOC', '.XLSX', '.PPTX', '.DOCX', '.TXT', '.CSV', '.PDF', '.PD',

                #music and video
                '.mp3', '.mp4', '.mpg', '.ai', '.avi', '.swf',
                '.MP3', '.MP4', '.MPG', '.AI', '.AVI', '.SWF',

                #compressions and other
                '.zip', '.rar', '.css', '.flv', '.php',
                '.ZIP', '.RAR', '.CSS', '.FLV', '.PHP',


            )):
                continue

            # If url includes characters like ?, %, &, # ... it is LIKELY NOT to be the one we are looking for and we ignore it.
            # However in this case we exclude good urls like
            # http://www.mdm.si/company#employment
            if any(x in url for x in ['?', '%', '&', '#']):
                continue

            # Ignore ftp.
            if url.startswith("ftp"):
                continue

            # We need to save original url for xpath, in case we change it
            # later (join it with base_url)
            url_xpath = url

            # If url doesn't start with "http", it is relative url, and we add base url to get absolute url.
            # -- It is true, that we may get some strange urls, but it is fine for now.
            if not (url.startswith("http")):

                url = urljoin(base_url, url)

            # We don't want to go to other websites. We want to stay on our
            # website, so we keep only urls with domain (netloc) of the company
            # we are investigating.
            if (urlparse(url).netloc == urlparse(base_url).netloc):

                # The main part. We look for webpages, whose urls include one
                # of the employment words as strings.

                # -- Instruction.
                # -- Users in other languages, please insert employment words in your own language, like jobs, vacancies, career, employment ... --
                if any(x in url for x in [

                    'zaposlovanje',
                    'Zaposlovanje',

                    'zaposlitev',
                    'Zaposlitev',

                    'zaposlitve',
                    'Zaposlitve',

                    'zaposlimo',
                    'Zaposlimo',

                    'kariera',
                    'Kariera',

                    'delovna-mesta',

                    'delovna_mesta',

                    'pridruzi-se',
                    'pridruzi_se',

                    'prijava-za-delo',
                    'prijava_za_delo',

                    'oglas',
                    'Oglas',

                    'iscemo',
                    'Iscemo',

                    'careers',
                    'Careers',

                    'jobs',
                    'Jobs',

                    'employment',
                    'Employment',


                ]):
                    # This is additional filter, suggested by Dan Wu, to
                    # improve accuracy. We will check the text of the url as
                    # well.
                    texts = response.xpath(
                        '//a[@href="%s"]/text()' % url_xpath).extract()

                    # 1. Texts are empty.
                    if texts == []:

                        print "Ni teksta za url: " + str(url)

                        # We found url that includes one of the magic words and also the text includes a magic word.
                        # We check url, if we have found it before. If it is
                        # new, we add it to the list "jobs_urls".
                        if url not in self.jobs_urls:

                            self.jobs_urls.append(url)
                            item = JobItem()
                            #item["text"] = text
                            item["url"] = url

                            # We return the item.
                            yield item

                    # 2. There are texts, one or more.
                    else:

                        # For the same partial url several texts are possible.
                        for text in texts:

                            if any(x in text for x in [

                                'zaposlovanje',
                                'Zaposlovanje',

                                'zaposlitev',
                                'Zaposlitev',

                                'zaposlitve',
                                'Zaposlitve',

                                'zaposlimo',
                                'Zaposlimo',
                                'ZAPOSLIMO',

                                'kariera',
                                'Kariera',

                                'delovna-mesta',

                                'delovna_mesta',

                                'pridruzi-se',
                                'pridruzi_se',

                                'oglas',
                                'Oglas',

                                'iscemo',
                                'Iscemo',
                                'ISCEMO',


                                'careers',
                                'Careers',

                                'jobs',
                                'Jobs',

                                'employment',
                                'Employment',



                            ]):

                                # We found url that includes one of the magic words and also the text includes a magic word.
                                # We check url, if we have found it before. If
                                # it is new, we add it to the list "jobs_urls".
                                if url not in self.jobs_urls:

                                    self.jobs_urls.append(url)
                                    item = JobItem()
                                    item["text"] = text
                                    item["url"] = url

                                    # We return the item.
                                    yield item

                # We don't put "else" sentence because we want to further explore the employment webpage to find possible new employment webpages.
                # We keep looking for employment webpages, until we reach the
                # DEPTH, that we have set in settings.py.
                yield Request(url, callback=self.parse)

      # We run the programme in the command line with this command:

      #      scrapy crawl jobs -o jobs.csv -t csv --logfile log.txt

      # We get two output files
      #  1) jobs.csv
      #  2) log.txt

      # Then we manually put one of employment urls from jobs.csv into read.py
