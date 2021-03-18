import datetime
import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import MetzlerItem
from itemloaders.processors import TakeFirst


class MetzlerSpider(scrapy.Spider):
	name = 'metzler'
	start_urls = ['https://www.metzler.com/mwebrel/ajax/artikel/filter?limit=999999&offset=0&sprache=DE&artikelTyp=NEWS&suchText=&geschaeftsbereich=MAM&geschaeftsbereich=MCM&geschaeftsbereich=Bankhaus&geschaeftsbereich=MCF&geschaeftsbereich=Karriere&geschaeftsbereich=MPB']

	def parse(self, response):
		data = json.loads(response.text)

		for post in data['results']:
			title = post['text']
			date = post['startDatum']
			date = datetime.datetime.fromtimestamp(date/1000.0)
			url = 'https://www.metzler.com/de/metzler/bankhaus/presse-news/details/news'+post['path']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, title, date):
		description = response.xpath('//div[@class="module module--push2 richtext"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=MetzlerItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
