from __future__ import absolute_import
import scrapy
import json

from scrapy.http import Request
from crawling.spiders.lxmlhtml import CustomLxmlLinkExtractor as LinkExtractor
from scrapy.conf import settings

from scrapy_splash import SplashRequest

from crawling.items import RawResponseItem
from crawling.spiders.redis_spider import RedisSpider


class UbikeSpider(RedisSpider):
    '''
    A spider that walks all bikes from the requested URL. This is
    the entrypoint for generic crawling.
    '''
    name = "bike"

    def __init__(self, *args, **kwargs):
        super(UbikeSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        self._logger.debug("crawled url {}".format(response.request.url))
        cur_depth = 0
        if 'curdepth' in response.meta:
            cur_depth = response.meta['curdepth']

        # capture raw response
        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']

        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["status_msg"] = "OK"
        # item["response_headers"] = self.reconstruct_headers(response)
        item["response_headers"] = []
        item["request_headers"] = response.request.headers
        item["body"] = ""
        item["encoding"] = response.encoding
        item["links"] = []

        bikes = response.xpath("//div[@class = 'row seSearchProductWrapper']")
        i = 0
        for idx, bike in enumerate(bikes.xpath(".//descendant::div[@class = 'seProductTitle']")):
            link = bike.xpath(".//a/@href").get()
            if (idx < 1):
                self._logger.debug("Should craw next URL {}".format(link))
                yield response.follow(url = link, callback = self.parse_bike, meta = {"idx": idx})

        # next_page = response.xpath("//a[@class='sePaginationLink'][@tabindex='0']/@href").get()
        # print('next page to crawl is: ' + str(next_page))

        # if next_page:
        #     yield response.follow(next_page, callback=self.parse)


    def parse_bike(self, response):
        bike_meta =  {
            "type": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[4]/descendant::span/text())").get(),
            "suspension": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[5]/descendant::span/text())").get(),
            "brand": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[6]/descendant::span/text())").get(),
            "model": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[7]/descendant::span/text())").get(),
            "price": response.xpath("normalize-space(//div[@id='RegularPrice']/text())").get(),
            "url": response.request.url
        }

        data = response.json()
        print(data)

        item = RawResponseItem()
        # populated from response.meta
        item['appid'] = response.meta['appid']
        item['crawlid'] = response.meta['crawlid']
        item['attrs'] = response.meta['attrs']

        # populated from raw HTTP response
        item["url"] = response.request.url
        item["response_url"] = response.url
        item["status_code"] = response.status
        item["status_msg"] = "OK"
        item["response_headers"] = []
        # item["response_headers"] = self.reconstruct_headers(response)
        item["request_headers"] = []
        item["body"] = bike_meta
        item["encoding"] = response.encoding
        item["links"] = []
        yield item
        
