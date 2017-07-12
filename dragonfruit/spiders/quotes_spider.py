import scrapy
from time import sleep
import os
import datetime

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    # <li class="category-level-1">
    start_urls = [
        'https://www.costco.com/health-beauty.html',
    ]

    def start_requests(self):
        return [scrapy.FormRequest("https://www.costco.com/LogonForm?URL=%2f",
                                   formdata={'Email Address': 'xx@gmail.com', 'Password': 'secret'},
                                   callback=self.after_login)]


    def after_login(self, response):

        # logging response information
        log_dir = os.path.dirname(os.path.abspath(__file__)) + '\\response_log'
        currentTime = str(datetime.datetime.now())[:19]
        logfile = ''.join(c for c in currentTime if c.isalnum()) + '_res.txt'
        responseBodyString = response.body.decode()
        with open(os.path.join(log_dir, logfile), 'w') as f:
            f.write(responseBodyString)

        # check login succeed before going on
        if "authentication failed" in responseBodyString:
            self.logger.error("Login failed")
            return
        else:
            for url in self.start_urls:
                yield scrapy.Request(url, callback=self.parse_category)

    def parse_category(self, response):
        prices = response.css('div.price::text').extract()
        productnames = response.css('p.description::text').extract()

        if len(prices):
            self.parse_price(prices, productnames)

        for category_url in response.xpath('//div[@class="col-xs-6 col-md-3"]').css('a::attr(href)').extract():
            sleep(1)
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_price(self, prices, productnames):
        for i in range(len(prices)):
            # '.97':discount from store, '.00':clearance
            # '.49' or '.79' discount from brand
            if prices[i][-3:]=='.97' or prices[i][-3:]=='.00':
                print(productnames[i], ':', prices[i])
