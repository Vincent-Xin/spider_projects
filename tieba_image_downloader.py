'''
爬取百度贴吧杉本有美吧里杉本有美的图片，来自github：Show-Me-the-Code，python练习册第13题
'''

import os

import requests
from scrapy import Selector
from PIL import Image
from io import BytesIO

headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    }

class ImagesDownloader():
    def __init__(self):
        self.article_hrefs = []
        self.list_urls = self.all_list_urls()

    def parse_run(self):
        # 走起
        self.parse_page_list()
        for href in self.article_hrefs:
            self.parse_article(href)

    def parse_page_list(self):
        # 贴吧限制，只能浏览到第10页左右
        limit_text = '这一页的贴子被限制访问了，我们已加快审核速度，会尽快解除限制，看看其他贴子吧～'
        for url in self.list_urls:
            response = requests.get(url, headers=headers, verify=False)
            if limit_text in response.text:
                break
            text = response.text.replace('<!--','').replace('--></code>','</code>')
            sel = Selector(text=text)
            article_hrefs = sel.xpath('//ul[@id="thread_list"]//div[@class="threadlist_title pull_left j_th_tit "]/a/@href').extract()
            self.article_hrefs.extend(article_hrefs)

    def parse_article(self,href):
        cur_url = f'http://tieba.baidu.com{href}'
        print(cur_url)
        response = requests.get(cur_url, headers=headers, verify=False)
        # 返回的response的html代码被注释掉，xpath无法查找，需要去掉注释
        text = response.text.replace('<!--', '').replace('--></code>', '</code>')
        sel = Selector(text=text)
        # 处理图片
        image_sels = sel.css('#container .d_post_content.j_d_post_content.clearfix>img')
        for image_sel in image_sels:
            image_width = int(image_sel.xpath('./@width').extract()[0])
            image_heigth = int(image_sel.xpath('./@height').extract()[0])
            # 过滤掉无关的表情包和小尺寸图片
            if image_width * image_heigth >= 2 * 10 ** 4:
                image_url = image_sel.xpath('./@src').extract()[0]
                self.save_image(image_url)
        page_num = int(sel.css('.l_posts_num .l_reply_num>span.red::text').extract()[1])
        # 下一页
        if page_num > 1 and sel.css('.l_pager.pager_theme_4.pb_list_pager>span.tP::text').extract()[0] == '1':
            for i in range(2,page_num+1):
                self.parse_article(f'{href}?pn={i}')

    def save_image(self, image_url):
        # 保存图片
        print(image_url)
        response = requests.get(image_url, headers=headers, verify=False)
        path = '/Users/xinych/Desktop/杉本有美'
        image_name = os.path.join(path, image_url[-11:])
        with open(image_name, 'wb') as f:
            f.write(response.content)
        # image = Image.open(BytesIO(response.content))
        # image.save(os.path.join('/Users/xinych/Desktop/杉本有美', image_url[-11:]))

    def all_list_urls(self):
        # 杉本有美吧网址
        return [f'http://tieba.baidu.com/f?kw=%E6%9D%89%E6%9C%AC%E6%9C%89%E7%BE%8E&ie=utf-8&pn={n*50}' for n in range(30)]

if __name__ == '__main__':
    image_downloader = ImagesDownloader()
    image_downloader.parse_run()
