from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from gudegnet.items import GudegnetItem

class GudegnetSpider(CrawlSpider):
	name = "gudegnetdir"
	allowed_domains = ["gudeg.net"]
	start_urls = ["https://gudeg.net/id/index.html"]
	rules = (Rule (SgmlLinkExtractor(allow=['^.*(directory|news).*$'],deny=['^.*PageNo.*$']),callback="parse_item", follow= True),
    )

	def parse_item(self, response):
		hxs = HtmlXPathSelector(response)
		item = GudegnetItem()
		item['url'] = response.url
		item['article_html'] = response.xpath("//div[@class='konten-data']/descendant::*/text()").extract()
		
		return item
	