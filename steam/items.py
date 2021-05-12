# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from scrapy.selector import Selector


def clean_discount_rate(discount_rate):
    if discount_rate:
        discount_rate = discount_rate.lstrip('-').rstrip('%')
    return discount_rate


def remove_html(str_with_html):
    cleaned_str = ''
    try:
        cleaned_str = str_with_html.replace('<br>', ' ')
    except TypeError:
        cleaned_str = 'No reviews'
    except AttributeError:
        cleaned_str = 'No reviews'
    return cleaned_str


def get_platforms(one_class):
    platforms = [one_class.split(' ')[-1]]
    return platforms


def get_original_price(html_markup):
    selector_obj = Selector(text=html_markup)
    original_price = ''
    div_with_discount = selector_obj.xpath(".//div[contains(@class, 'search_price discounted')]")
    if len(div_with_discount) > 0:
        original_price = div_with_discount.xpath(".//span/strike/text()").getall()
    else:
        original_price = selector_obj.xpath(".//div[contains(@class, 'search_price')]/text()").getall()

    return original_price


class SteamItem(scrapy.Item):
    game_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    img_url = scrapy.Field(
        output_processor=TakeFirst()
    )
    game_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    release_date = scrapy.Field(
        output_processor=TakeFirst()
    )
    rating = scrapy.Field(
        input_processor=MapCompose(remove_html),
        output_processor=TakeFirst()
    )
    platforms = scrapy.Field(
        input_processor=MapCompose(get_platforms))
    original_price = scrapy.Field(
        input_processor=MapCompose(get_original_price, str.strip),
        output_processor=Join('')
    )
    discount_rate = scrapy.Field(
        input_processor=MapCompose(clean_discount_rate),
        output_processor=TakeFirst()
    )
    discount_price = scrapy.Field(
        output_processor=TakeFirst()
    )

