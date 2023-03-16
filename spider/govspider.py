import requests
from lxml import etree
import time
from tqdm import tqdm


class GovSpider:

    def __init__(self, primary_url = 'https://www.guizhou.gov.cn/zwgk/zfxxgk/yqlj/szzf/',
                 secondary_url = 'https://www.guizhou.gov.cn/zwgk/zfxxgk/yqlj/xsqtqzf/',
                 primary_rule = '//div[contains(@class,"zfxxgk_02Box")]//a/@title',
                 secondary_rule = '//div[contains(@class,"zfxxgk_02Box")]//a/text()',
                 gov_url = 'https://www.guizhou.gov.cn/home/sxdt/index.html',
                 gov_rule = '//div[contains(@class,"PageMainBox")]//a',
                 gov_rule2 = '//div[contains(@class,"PageMainBox")]//span/text()',
                 invest_url = 'http://invest.guizhou.gov.cn/dtzx/gzdt/dfdt/index.html',
                 invest_rule = '//div[@class="NewsList"]//a',
                 invest_rule2 = '//div[@class="NewsList"]//li/span/text()'):
        self.primary_url = primary_url
        self.secondary_url = secondary_url
        self.primary_rule = primary_rule
        self.secondary_rule = secondary_rule
        self.gov_url = gov_url
        self.gov_rule = gov_rule
        self.gov_rule2 = gov_rule2
        self.invest_url = invest_url
        self.invest_rule = invest_rule
        self.invest_rule2 = invest_rule2
        self.gov_data = []
        self.invest_data = []

        self.primary_list = self.get_gov_name(self.primary_url, self.primary_rule)
        self.primary_copy = [i[:-1] for i in self.primary_list]
        self.secondary_list = self.get_gov_name(self.secondary_url, self.secondary_rule)
        self.secondary_copy = [i[:-1] for i in self.secondary_list]
        self.all_gov = self.primary_copy + self.secondary_copy

        self.title_href_dict = {}
        self.data = []

    def get_gov_name(self, url:str, rule:str)->list:
        '''
        根据指定的url和指定的xpath规则
        :param url: 政府网址
        :param rule: xpath规则
        :return: 返回列表数据
        '''
        resp = requests.get(url=url)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)
        return html.xpath(rule)

    def spider_gov(self)->list:
        '''
        爬取贵州省人民政府网站地方动态的数据
        :return:包含地方动态的标题，链接，日期
        '''
        data = []
        resp = requests.get(url=self.gov_url)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)
        a_s = html.xpath(self.gov_rule)
        date_s = html.xpath(self.gov_rule2)
        for i, j in zip(a_s, date_s):
            data.append([i.attrib.get('title'), i.attrib.get('href'), ''.join(j).strip()])
            print([i.attrib.get('title'), i.attrib.get('href'), ''.join(j).strip()])
        for i in tqdm(range(1, 51)):
            new_url = f'https://www.guizhou.gov.cn/home/sxdt/index_{i}.html'
            new_resp = requests.get(new_url)
            new_resp.encoding = new_resp.apparent_encoding
            new_html = etree.HTML(new_resp.text)
            new_a_s = new_html.xpath(self.gov_rule)
            new_date_s = new_html.xpath(self.gov_rule2)
            for m, n in zip(new_a_s, new_date_s):
                data.append([m.attrib.get('title'), m.attrib.get('href'), ''.join(n).strip()])
                time.sleep(0.1)
        self.gov_data = data
        return data

    def spider_invest(self)->list:
        '''
        爬取投资促进局的地方动态数据
        :return: 包含标题，链接，日期的一个列表
        '''
        data = []
        resp = requests.get(url=self.invest_url)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)
        a_s = html.xpath(self.invest_rule)
        date_s = html.xpath(self.invest_rule2)
        for i, j in zip(a_s, date_s):
            data.append([i.attrib.get('title'), i.attrib.get('href'), ''.join(j).strip()])
        for i in tqdm(range(1, 51)):
            new_url = f'http://invest.guizhou.gov.cn/dtzx/gzdt/dfdt/index_{i}.html'
            new_resp = requests.get(new_url)
            new_resp.encoding = new_resp.apparent_encoding
            new_html = etree.HTML(new_resp.text)
            new_a_s = new_html.xpath(self.invest_rule)
            new_date_s = new_html.xpath(self.invest_rule2)
            for m, n in zip(new_a_s, new_date_s):
                data.append([m.attrib.get('title'), m.attrib.get('href'), ''.join(n).strip()])
        self.invest_data = data
        return data

