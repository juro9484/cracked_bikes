from __future__ import absolute_import
import scrapy

from scrapy.http import Request
from crawling.spiders.lxmlhtml import CustomLxmlLinkExtractor as LinkExtractor
from scrapy.conf import settings

from scrapy_splash import SplashRequest

from crawling.items import RawResponseItem
from crawling.spiders.redis_spider import RedisSpider


class ubikesSpider(RedisSpider):
    '''
    A spider that walks all links from the requested URL. This is
    the entrypoint for generic crawling.
    '''
    name = "ubikes"

    def __init__(self, *args, **kwargs):
        super(ubikesSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        self._logger.debug("crawled url {}".format(response.request.url))
        bikes = response.xpath("//div[@class = 'row seSearchProductWrapper']")
        i = 0
        for idx, bike in enumerate(bikes.xpath(".//descendant::div[@class = 'seProductTitle']")):
            link = bike.xpath(".//a/@href").get()
            if (idx < 2):
                self._logger.debug("Should craw next URL {}".format(link))
                yield response.follow(url = link, callback = self.parse_bike, meta = {"idx": idx})

    def parse_bike(self, response):
        
        bike_meta =  {
            "type": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[4]/descendant::span/text())").get(),
            "suspension": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[5]/descendant::span/text())").get(),
            "brand": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[6]/descendant::span/text())").get(),
            "model": response.xpath("normalize-space(//div[@id='ProductDetails']/ol/li[7]/descendant::span/text())").get(),
            "price": response.xpath("normalize-space(//div[@id='RegularPrice']/text())").get(),
            "url": response.request.url
        }
        
        select1 = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation1']")
        select2 = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation3']")

        # IF BOTH SELECT OPTIONS ARE PRESENT
        if (len(select1) > 0 and len(select2) > 0):
            colors = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation3']/option[position()>1]")
            for variation in colors:
                tmp_script = '''
                    function main(splash, args)
                        splash.private_mode_enabled = false
                        assert(splash:go("''' + response.request.url + '''"))
                        assert(splash:wait(1))
                        splash:runjs('document.getElementById("Variation3").value = "''' + variation.xpath('.//@value').get() + '''"')
                        splash:runjs('document.getElementById("Variation3").dispatchEvent(new Event("change"))');
                        assert(splash:wait(1))
                        return splash:html()
                    end 
                '''
                select1_label = response.xpath("//div[@id='SkuSelection']/div/label[@class='seItemVariationLabel'][@for='Variation3']/text()").get()
                select1_value = variation.xpath('.//text()').get()
                tmp_dict = bike_meta.copy()
                tmp_dict[select1_label] = select1_value
                yield SplashRequest(url = response.request.url, callback = self.parse_bike_options,
                endpoint='execute', args = {'lua_source': tmp_script}, meta = {"bike_meta": tmp_dict})

        # IF ONLY THE SIZE SELECT OPTION IS PRESENT
        elif (len(select1) > 0):
            sizes = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation1']/option[position()>1]")
            for variation in sizes:
                tmp_dict = bike_meta.copy()
                tmp_dict[response.xpath("//div[@id='SkuSelection']/div/label[@class='seItemVariationLabel'][@for='Variation1']/text()").get()] = variation.xpath('.//text()').get()
                tmp_dict[response.xpath("//dl[@class='col-xs-12 seItemVariationsTextContainer']/div/dt[@class='seItemVariationLabel']/text()").get()] = response.xpath("//dl[@class='col-xs-12 seItemVariationsTextContainer']/div/dd[@class='seItemData']/text()").get()
                yield tmp_dict

                # THIS RUNS SPLASH FOR EVERY COLOR SIZE IF THERE ARE ONLY SIZE OPTIONS AVAILABLE. REMOVED FOR NOW BECAUSE COULD BE EXCESS OF SCRAPING (THERE IS ONLY ONE POSSIBLE COLOR).

                # tmp_script = '''
                #     function main(splash, args)
                #         splash.private_mode_enabled = false
                #         assert(splash:go("''' + response.request.url + '''"))
                #         assert(splash:wait(1))
                #         splash:runjs('document.getElementById("Variation1").value = "''' + variation.xpath('.//@value').get() + '''"')
                #         splash:runjs('document.getElementById("Variation1").dispatchEvent(new Event("change"))');
                #         assert(splash:wait(1))
                #         return splash:html()
                #     end 
                # '''
                # select1_label = response.xpath("//div[@id='SkuSelection']/div/label[@class='seItemVariationLabel'][@for='Variation1']/text()").get()
                # select1_value = variation.xpath('.//text()').get()
                # tmp_dict = bike_meta.copy()
                # tmp_dict[select1_label] = select1_value
                # yield SplashRequest(url = response.request.url, callback = self.parse_bike_options_2,
                # endpoint='execute', args = {'lua_source': tmp_script}, meta = {"bike_meta": tmp_dict})

        # IF ONLY THE COLOR SELECT OPTION IS PRESENT
        elif (len(select2) > 0):
            sizes = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation3']/option[position()>1]")
            for variation in sizes:
                tmp_dict = bike_meta.copy()
                tmp_dict[response.xpath("//div[@id='SkuSelection']/div/label[@class='seItemVariationLabel'][@for='Variation3']/text()").get()] = variation.xpath('.//text()').get()
                tmp_dict[response.xpath("//dl[@class='col-xs-12 seItemVariationsTextContainer']/div/dt[@class='seItemVariationLabel']/text()").get()] = response.xpath("//dl[@class='col-xs-12 seItemVariationsTextContainer']/div/dd[@class='seItemData']/text()").get()
                yield tmp_dict

            # THIS RUNS SPLASH FOR EVERY COLOR OPTION IF THERE ARE ONLY COLOR OPTIONS AVAILABLE. REMOVED FOR NOW BECAUSE COULD BE EXCESS OF SCRAPING (THERE IS ONLY ONE POSSIBLE SIZE).

            # colors = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation3']/option[position()>1]")
            # for variation in colors:
            #     tmp_script = '''
            #         function main(splash, args)
            #             splash.private_mode_enabled = false
            #             assert(splash:go("''' + response.request.url + '''"))
            #             assert(splash:wait(1))
            #             splash:runjs('document.getElementById("Variation3").value = "''' + variation.xpath('.//@value').get() + '''"')
            #             splash:runjs('document.getElementById("Variation3").dispatchEvent(new Event("change"))');
            #             assert(splash:wait(1))
            #             return splash:html()
            #         end 
            #     '''
            #     select1_label = response.xpath("//div[@id='SkuSelection']/div/label[@class='seItemVariationLabel'][@for='Variation3']/text()").get()
            #     select1_value = variation.xpath('.//text()').get()
            #     tmp_dict = bike_meta.copy()
            #     tmp_dict[select1_label] = select1_value
            #     yield SplashRequest(url = response.request.url, callback = self.parse_bike_options_2,
            #     endpoint='execute', args = {'lua_source': tmp_script}, meta = {"bike_meta": tmp_dict})

        # IF NO SELECT OPTIONS ARE PRESENT
        else:
            variations = response.xpath("//dl[@class='col-xs-12 seItemVariationsTextContainer']/div")
            tmp_dict = bike_meta.copy()
            for variation in variations:
                tmp_dict[variation.xpath(".//dt[@class='seItemVariationLabel']/text()").get()] = variation.xpath(".//dd[@class='seItemData']/text()").get()
            yield tmp_dict

    def parse_bike_options(self, response):
        select1_label = response.xpath("//div[@id='SkuSelection']/div/label[@class='seItemVariationLabel'][@for='Variation1']/text()").get()
        select1_options = response.xpath("//div[@id='SkuSelection']/div/select[@id='Variation1']/optgroup[@class='availableGroup']/option")
        for idx, variation in enumerate(select1_options):
            tmp_size = variation.xpath('.//text()').get()
            tmp_dict = response.meta['bike_meta'].copy()
            tmp_dict[select1_label] = tmp_size
            yield tmp_dict

    def parse_bike_options_2(self, response):
        variations = response.xpath("//dl[@class='col-xs-12 seItemVariationsTextContainer']/div")
        tmp_dict = response.meta['bike_meta'].copy()
        for variation in variations:
                tmp_dict[variation.xpath(".//dt[@class='seItemVariationLabel']/text()").get()] = variation.xpath(".//dd[@class='seItemData']/text()").get()
        yield tmp_dict
        