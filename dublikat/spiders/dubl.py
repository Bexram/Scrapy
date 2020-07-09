# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import scrapy
from urlparse import urljoin


class DublSpider(scrapy.Spider):
    name = 'dubl'
    allowed_domains = ['my.dublikat.shop']
    start_urls = ['https://my.dublikat.shop/']
    visited_urls = []

    def use_bs(self, p_cont1, p_cont2, p_items1, p_items2, html_file):
        soup = BeautifulSoup(html_file)
        page_cont = soup.find(p_cont1, p_cont2)
        if page_cont is not None:
            items = page_cont.find_all(p_items1, p_items2)
            return items

    def parse(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.append(response.url)
            for forum_link in response.xpath('//div[@class="block-container"]/h2/a/@href').extract():
                url = urljoin(response.url, forum_link)
                # print('Parse_F1- '+url)
                yield response.follow(url, callback=self.parse_f)

    def parse_f(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.append(response.url)
            for forum2_link in response.xpath('//h3[@class="node-title"]/a/@href').extract():
                url = urljoin('https://my.dublikat.shop/', forum2_link)
                # print('Parse_F2- '+url)
                yield response.follow(url, callback=self.parse_t)

    def parse_t(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.append(response.url)
            for themes_link in response.xpath('//div[@class="structItem-title"]/a/@href').extract():
                url = urljoin(response.url, themes_link)
                # print(url)
                yield response.follow(url, callback=self.parse_m)
            next_page = response.xpath('//a[@class="pageNav-jump pageNav-jump--next"]/@href').extract()
            if next_page:
                next_page_url = urljoin(response.url + '/', next_page[0])
                yield response.follow(next_page_url, callback=self.parse_t)

    def parse_m(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.append(response.url)
            for item in self.use_bs('div', {'class': 'p-body-main'}, 'div', {'class': 'message-inner'}, response.text):
                if item.find('h4', {'class': 'message-name'}).find('span') is not None:
                    message_user = item.find('h4', {'class': 'message-name'}).find('span').text
                else:
                    message_user = item.find('h4', {'class': 'message-name'}).find('a').text

                message_date = item.find('time', {'class': 'u-dt'}).text
                text_message = item.find('div', {'class': 'bbWrapper'}).text
                if 'class="username' in text_message:
                    ans_user = item.find('a', {'class': 'username'}).text
                    text_message = text_message['</a>':]
                    text_message = ans_user + ', ' + text_message['</a>':]

                if 'blockquote' in text_message:
                    ans_user = item.find('a', {'class': 'bbCodeBlock-sourceJump'}).text
                    ans_text = item.find('div', {'class': 'bbCodeBlock-expandContent '}).text
                    text_message = ans_user + ': ' + ans_text + ' - ' + text_message[
                                                                        '</blockquote>':]

                # images_link = ''
                # img_items=item.find_all('a', {'class': 'link link--external'})
                # if img_items is not None:
                # for item in img_items:
                # images_link=images_link+' '+item.find('img', {'class': 'bbImage'}).data-url
                if '\'' in text_message:
                    text_message = text_message.replace('\'', '')
                if '\'' in message_user:
                    message_user = message_user.replace('\'', '')

                print(message_user+"  "+message_date+"  "+text_message)
            next_page = response.xpath('//a[@class="pageNav-jump pageNav-jump--next"]/@href').extract()
            if next_page:
                next_page_url = urljoin(response.url + '/', next_page[0])
                yield response.follow(next_page_url, callback=self.parse_m)
