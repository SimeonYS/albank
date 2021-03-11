import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AlbankItem
from itemloaders.processors import TakeFirst
import datetime

pattern = r'(\xa0)?'

class AlbankSpider(scrapy.Spider):
	now = datetime.datetime.now()
	name = 'albank'
	year = now.year
	start_urls = [f'https://www.al-bank.dk/om-banken/presse-og-nyheder/nyheder?year={year}']

	def parse(self, response):
		post_links = response.xpath('//h5/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.al-bank.dk/om-banken/presse-og-nyheder/nyheder?year={self.year}'
		if self.year >= 2014:
			self.year -=1
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//div[@class="date"]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//section//text()[not (ancestor::aside) and not (ancestor::h1) and not (ancestor::div[@class="news-details"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=AlbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
