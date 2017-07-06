import scrapy

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
        # check login succeed before going on
        if "authentication failed" in response.body.decode():
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
            yield scrapy.Request(category_url, callback=self.parse_category)

    def parse_price(self, prices, productnames):
        for i in range(len(prices)):
            if prices[i][-2:] == '97':
                print(productnames[i], ':', prices[i])
