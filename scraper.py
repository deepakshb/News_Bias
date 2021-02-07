from bs4 import BeautifulSoup
import requests
import csv
from tqdm import tqdm

class TOIScraper:

    def __init__(self, main_url):
        self.main_url = main_url

    def get_links(self, topic):
        # This method searches a topic on Times of India Website and all picks the links of the
        # articles (also from pagination)
        urls = []
        num_pages = -1
        page_counter = 1
        page_link = ""
        print("Collecting URLs....", end='')
        while True:
            url = self.main_url + "/topic/" + topic + "/news" + page_link
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            if num_pages == -1:
                pages = soup.select('div.pagination a')
                num_pages = int(pages[-2].text)

            cards = soup.findAll('div', 'content')
            for card in cards:
                url = card.find('a').get('href')
                urls.append(self.main_url + url)

            page_counter = page_counter + 1
            page_link = "/" + str(page_counter)
            if page_counter > num_pages:
                print("Done.")
                break
        return urls

    def get_articles_from_urls(self, urls):
        # This methods scrapes the articles from the collected links
        with open('news.csv', 'w') as target:
            writer = csv.writer(target)
            writer.writerow(["articles",])
        print("Scraping News articles...")
        for i in tqdm(range(len(urls))):
            try:
                response = requests.get(urls[i])
                soup = BeautifulSoup(response.text, 'html.parser')
                # date = soup.find('div', "_3Mkg- byline").text
                article = soup.find('div', "ga-headlines").text
                with open('/Users/deepakrastogi/Documents/news_bias/news.csv', 'a') as target:
                    writer = csv.writer(target)
                    writer.writerow([article, ])
            except:
                pass
        print("All articles stored in CSV")

    def scrape_news_articles(self):
        # This method triggers the scraping process
        topics = ['politics','germany','trump','corona']
        all_urls = []
        for topic in topics:
            links = self.get_links(topic)
            all_urls = all_urls + links

        uniq_urls = list(dict.fromkeys(all_urls))
        self.get_articles_from_urls(uniq_urls)