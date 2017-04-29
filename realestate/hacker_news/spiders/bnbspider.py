# -*- coding: utf-8 -*-
import scrapy
import json
from hacker_news.items import BnbtutorialItem
from MasterSpider import *
from scrapy.shell import inspect_response
from scrapy.spidermiddlewares.httperror import HttpError

from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
QUERY = 'Lucca--Italy'


class BnbspiderSpider(Master):
    name = "bnbspider"
    allowed_domains = ["airbnb.com"]
    # start_urls = (
    #     'https://www.airbnb.com/s/Lucca--Italy',
    # )

    # def __init__(self, **kwargs):
    #     changetor()
    #     print('Start')
    # My settings

    def start_requests(self):
        changetor()
        print('Start')
        request = Request(
            'https://www.airbnb.com/s/Lucca--Italy',
            callback=self.parse,
            errback=self.errback_httpbin,
            dont_filter=True
        )
        print request
        yield request
    # print(spitogatos)
    # self.source_xpaths = spitogatos

    # ------ Test -----
    # yield Request('file://127.0.0.1/users/sabbidis/Downloads/file.html',
    #               callback=self.parse_item)
    #  ----- End ------

    # for xtype in self.xtypes:
    #     for tran in self.transactions:
    #         for i in xrange(104, 105):                  # LIMIT CATEGORIES
    #             url = "http://www.homegreekhome.com/en/search/results/" + \
    #                 xtype + "/" + tran + "/r" + \
    #                 str(i) + "/m" + str(i) + "m/"
    #             yield Request(url, callback=self.get_searchpage_urls)

    def parse(self, response):
        # ge the last page number on the page
        last_page_number = 1  # self.last_pagenumer_in_search(response)
        print(response.url)
        if last_page_number < 1:
            # abort the search if there are no results
            print "no results "
            return
        else:
            # otherwise loop over all pages and scrape!
            page_urls = [response.url + "?page=" + str(pageNumber)
                         for pageNumber in range(1, last_page_number + 1)]
            for page_url in page_urls:
                print(page_url)
                request = Request(page_url,
                                  callback=self.parse_listing_results_page,
                                  errback=self.errback_httpbin,
                                  dont_filter=True
                                  )
                print(request)
                yield request

    def last_pagenumer_in_search(self, response):
        try:  # to get the last page number
            last_page_number = int(response
                                   .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                                   .extract()[0]
                                   .split('page=')[1]
                                   )
            return last_page_number

        except IndexError:  # if there is no page number
            # get the reason from the page
            reason = response.xpath('//p[@class="text-lead"]/text()').extract()
            # and if it contains the key words set last page equal to 0
            print "error", reason
            if reason and ('find any results that matched your criteria' in reason[0]):
                logging.log(logging.DEBUG, 'No results on page' + response.url)
                return 0
            else:
                # otherwise we can conclude that the page
                # has results but that there is only one page.
                return 1

    def parse_listing_results_page(self, response):
        print "parse_listing_results_page"
        all_urls = response.xpath('//a/@href').extract()
        room_urls = [url for url in all_urls if url[:5] == '/room']
        print(all_urls)
        print(room_urls)
        for href in room_urls:
            # get all href of the speficied kind and join them to be a valid
            # url
            url = response.urljoin(href)
            print(url)
            # request the url and pass the response to final listings parsing
            # function
            yield scrapy.Request(url, callback=self.parse_listing_contents)

    def parse_listing_contents(self, response):
        item = BnbtutorialItem()
        # inspect_response(response, self)

        json_array = response.xpath(
            '//meta[@id="_bootstrap-room_options"]/@content').extract()
        if json_array:
            airbnb_json_all = json.loads(json_array[0])
            airbnb_json = airbnb_json_all['airEventData']
            item['rev_count'] = airbnb_json['visible_review_count']
            item['amenities'] = airbnb_json['amenities']
            item['host_id'] = airbnb_json_all['hostId']
            item['hosting_id'] = airbnb_json['hosting_id']
            item['room_type'] = airbnb_json['room_type']
            item['price'] = airbnb_json['price']
            item['bed_type'] = airbnb_json['bed_type']
            item['person_capacity'] = airbnb_json['person_capacity']
            item['cancel_policy'] = airbnb_json['cancel_policy']
            item['rating_communication'] = airbnb_json['communication_rating']
            item['rating_cleanliness'] = airbnb_json['cleanliness_rating']
            item['rating_checkin'] = airbnb_json['checkin_rating']
            item['satisfaction_guest'] = airbnb_json[
                'guest_satisfaction_overall']
            item['instant_book'] = airbnb_json['instant_book_possible']
            item['accuracy_rating'] = airbnb_json['accuracy_rating']
            item['response_time'] = airbnb_json['response_time_shown']
            item['response_rate'] = airbnb_json['response_rate_shown']
            item['nightly_price'] = airbnb_json_all['nightly_price']
        item['url'] = response.url
        print(item)
        yield item

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        print(repr(failure))
        print"FAILUREEE"
        print failure.value.response
        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
