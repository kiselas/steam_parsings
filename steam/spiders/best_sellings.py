# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from ..items import SteamItem
from scrapy_splash import SplashRequest


class BestSellingsSpider(scrapy.Spider):
    name = 'best_sellings'
    allowed_domains = ['store.steampowered.com']

    script = '''
        function main(splash, args)
            splash:on_request(function(request)
                if request.url:find('css') then
                    request.abort()
                end
            end)
          splash.images_enabled = false
          splash.js_enabled = false
          assert(splash:go(args.url))
          assert(splash:wait(0.5))
          return splash:html()
        end
        '''







    def start_requests(self):
        yield SplashRequest(url='https://store.steampowered.com/search/?filter=topsellers/', callback=self.parse_games,
                            endpoint='execute', args={'lua_source': self.script})

    def parse_games(self, response):
        games = response.xpath('//a[contains(@class, "search_result_row")]')
        # handle = open("output.html", "w")
        # handle.write(str(response.body))
        # handle.close()
        for game in games:
            loader = ItemLoader(item=SteamItem(), selector=game, response=response)
            loader.add_xpath('game_url', './/@href')
            loader.add_xpath('img_url', './/div[@class="col search_capsule"]/img/@src')
            loader.add_xpath('game_name', './/div[@class="responsive_search_name_combined"]/'
                                                 'div[@class="col search_name ellipsis"]/span/text()')
            loader.add_xpath('release_date', './/div[@class="responsive_search_name_combined"]/'
                                                    'div[@class="col search_released responsive_secondrow"]/text()')
            loader.add_xpath('rating', './/div[@class="col search_reviewscore responsive_secondrow"]/'
                                              'span/@data-tooltip-html')
            loader.add_xpath('platforms', './/span[contains(@class, "platform_img")]/@class')
            loader.add_xpath('discount_rate', ".//div[@class='col search_price_discount_combined "
                                                    "responsive_secondrow']/div[@class='col search_discount "
                                                    "responsive_secondrow']/span/text()")
            loader.add_xpath('original_price', './/div[contains(@class, "col search_price_discount_combined")]')
            loader.add_xpath('discount_price', './/div[contains(@class, "col search_price discounted")]/text()[2]')

            yield loader.load_item()
        next_page = response.xpath("//a[@class='pagebtn' and text()='>']/@href").get()
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_games
            )