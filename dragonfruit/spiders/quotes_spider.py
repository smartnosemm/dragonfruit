import scrapy
from time import sleep
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from dragonfruit.items import Product
import os
import datetime
import time

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ['costco.com']

    # <li class="category-level-1">
    start_urls = [
        'https://www.costco.com/skin-care.html'
    ]

    rules = (
        Rule(LinkExtractor(allow=()), callback="parse_category", follow=True),
    )

    # Connect to Amazon Dynamodb
    #dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    #productTable = dynamodb.Table('Costco_Products_Clearance')

    def start_requests(self):
        return [scrapy.FormRequest("https://www.costco.com/LogonForm?URL=%2f",
                                   formdata={'Email Address': 'xx@gmail.com', 'Password': 'secret'},
                                   callback=self.after_login)]

    def after_login(self, response):

        # logging response information
        #log_dir = os.path.dirname(os.path.abspath(__file__)) + '\\response_log'
        #current_time = str(datetime.datetime.now())[:19]
        #logfile = ''.join(c for c in current_time if c.isalnum()) + '_res.txt'
        response_body_string = response.body.decode()
        #with open(os.path.join(log_dir, logfile), 'w') as f:
        #    f.write(response_body_string)

        # check login succeed before going on
        if "authentication failed" in response_body_string:
            self.logger.error("Login failed")
            return
        else:
            for url in self.start_urls:
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        prices = response.css('div.price::text').extract()
        category = response.css('h1::text').extract_first()
        products = response.xpath('//div[@class="col-xs-6 col-md-4 col-xl-3 product"]')

        if len(prices):
            for i in range(len(prices)):
                # '.97':discount from store, '.00':clearance
                # '.49' or '.79' discount from brand
                if prices[i][-3:] == '.97' or prices[i][-3:] == '.00':
                    product_name = products[i].css('p.description::text').extract_first()
                    product_link = products[i].css('a').xpath('@href').extract_first()
                    product_id = products[i].css('a').xpath('@itemid').extract_first()
                    img_link = products[i].css('img').xpath('@data-src').extract_first()
                    if img_link is None:
                        img_link = products[i].css('img').xpath('@src').extract_first()
                    # epoch time
                    current_time = str(datetime.datetime.now())[:19]
                    expired_time = str(datetime.datetime.now() + datetime.timedelta(days=1))[:19]
                    creation_time = int(time.mktime(time.strptime(current_time, '%Y-%m-%d %H:%M:%S')))
                    expiration_time = int(time.mktime(time.strptime(expired_time, '%Y-%m-%d %H:%M:%S')))

                    item=Product()
                    item['ProductID'] = product_id
                    item['ProductName'] = product_name
                    item['ProductPrice'] = prices[i]
                    item['ProductLink'] = product_link
                    item['ImgLink'] = img_link
                    item['Category'] = category
                    item['CreationTime'] = creation_time
                    item['ExpirationTime'] = expiration_time
                    yield item

        #urls = response.xpath('//div[@class="col-xs-6 col-md-3"]').css('a::attr(href)').extract()
        #page_urls = response.xpath('//li[@class="page "]').css('a').xpath('@href').extract()
        '''
        if not urls:
            urls = response.xpath('//div[@class="col-xs-6 col-md-3 feature-tile"]').css('a::attr(href)').extract()
        if not urls:
            urls = response.xpath('//div[@class="col-xs-6 col-md-3 col-xl-3"]').css('a::attr(href)').extract()
        
        urls = urls + page_urls
        for category_url in urls:
            sleep(1)
            # If url is relative url, add 'https://www.costco.com'
            if category_url[:5] != 'https':
                if category_url[:1] != '/':
                    category_url = '/' + category_url
                category_url = 'https://www.costco.com' + category_url
            yield scrapy.Request(category_url, callback=self.parse_category)
        '''

