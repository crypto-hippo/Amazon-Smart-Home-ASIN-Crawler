from data.categories import categories 
from urllib.parse import urlencode  
from pyppeteer import launch
import asyncio
import time 

class BaseCrawler(object):
    pass

class AmazonCrawler(BaseCrawler):

    categories = categories 
    base_url = "https://www.amazon.com"
    search_path = "/s?"
    asin_numbers = set([])
    page = None 
    browser = None 
    chrome_executable = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'

    def __init__(self):
        pass

    def create_search_urls(self):
        search_args = {"k": ""}
        url_mapping = {}
        for category in self.categories:
            search_args["k"] = "wifi " + category
            next_url = self.base_url + self.search_path + urlencode(search_args)
            url_mapping[category] = next_url 
        return url_mapping

    # accepts an amazon start_url for category search, and fetches all urls for each page following
    def fetch_pagination_urls(self, start_url):
        pass

    def crawl_amazon(self):
        url_mapping = self.create_search_urls()
        for category, category_start_url in url_mapping.items():
            loop = asyncio.get_event_loop()
            v = loop.run_until_complete(self.crawl(category, category_start_url))
            print("\ndone with category\n")
            print(v)
            # asins_crawled = await self.crawl(category, category_start_url)
            # print("Found %s asins for category: %s" % (len(asins_crawled), category))
            # tasks = asyncio.Task.all_tasks()
            # loop.run_until_complete(self.get_tasks(tasks))


    async def get_tasks(self, tasks):
        doit = asyncio.gather(*tasks)
        print(doit)

    async def crawl(self, category, url):
        asin_numbers = set([])

        try:
            browser = await launch(args=['--disable-infobars'])
            page = await browser.newPage()
            page_num = 0

            while True:
                try:
                    await page.goto(url)

                    print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print("Category: %s" % category)
                    print("Url: %s" % url)
                    print("Current Page: %s" % page_num)
                    print("Fetching asin numbers")

                    asin_numbers_collected = await page.evaluate('''() => {
                            var asin_numbers = [];
                            var dom_asin_numbers = document.querySelectorAll("[data-asin]");
                            dom_asin_numbers.forEach(asin => {
                                asin_numbers.push(asin.getAttribute('data-asin'));
                            })

                            return asin_numbers;
                        }
                    ''')

                    print("Found %s asin numbers" % (len(asin_numbers_collected)))
                    asin_numbers = asin_numbers | set(asin_numbers_collected)   

                    next_button_disabled = await page.querySelector('.a-pagination .a-disabled.a-last')
                    
                    if next_button_disabled:
                        print("Last page crawled. Moving on to next category")
                        await page.close()
                        break

                    else:
                        next_button = await page.querySelector('.a-pagination .a-last a')
                        if not next_button:
                            break 
                        print("Next button found. Moving on to next page")
                        js_handle = await next_button.getProperty('href')

                        next_page_link = await js_handle.jsonValue()
                        url = next_page_link

                    page_num += 1
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")

                except Exception as e:
                    print(str(e))
                    print("Error fetching listings on url: %s" % (url))
                    time.sleep(2)
                    browser = await launch(args=['--disable-infobars'])
                    page = await browser.newPage()
                    print("Retrying") 

            return asin_numbers             

        except Exception as e:
            print(str(e))
            print("Error crawling url %s" % url)
            return asin_numbers

amazon_crawler = AmazonCrawler()
# loop = asyncio.get_event_loop()
amazon_crawler.crawl_amazon()



