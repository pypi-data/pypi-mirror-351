# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2025-05-27 18:45:04
import logging
import os.path
from datetime import datetime
from pathlib import Path
from typing import override

import requests
from lxml import etree
from utilsz import logging_util

from src.spider_demo import version
from src.spider_framework.common_init import CommonInit
from src.spider_framework.scheduler import SpiderTask, NetWorkError
from src.spider_framework.spider_framework import SpiderFramework

DEF_CONFIG_PATH = os.path.join(Path(__file__).resolve().parent, 'configs', 'config_def.py')


class SpiderDemo(SpiderFramework):
    def __init__(self, config):
        super().__init__(config, self._spider_fun)

    def _spider_fun(self, data_list_exist):
        # you can define custom params in config_def.py to user modify
        logging.error(f'PARMA1 = {self.config.CUSTOM['PARAM1']}')

        # 1. spider your html and return list data

        # 2. 对数据进行排序等预处理

        # 3. 返回新数据和所有数据
        return [], []

    # The following overridden functions are optional.
    @override
    def _push_hook(self, data_list, new_data_list, config):
        return True

    @override
    def _send_email(self, new_data_list, data_list):
        super()._send_email(new_data_list, data_list)

    @override
    def _send_wecom(self, new_data_list, data_list):
        super()._send_wecom(new_data_list, data_list)


# proxies = {
#     "http": "http://127.0.0.1:8888",
#     "https": "http://127.0.0.1:8888"
# }
proxies = None


class SpiderDemoDouBan(SpiderFramework):
    def __init__(self, config):
        super().__init__(config, self._spider_fun)

    @staticmethod
    def parse_movies_per_page(html: str):
        """
        解析例如https://movie.douban.com/top250?start=0的网页内容
        :param html: 网页内容的字符串
        :return:
        """
        movie_list = []
        # 将html文档转换为XPath可以解析的
        tree = etree.HTML(html)
        # 获取 <ul> 元素下的所有 <li> 元素
        li_elements = tree.xpath('//ol[@class="grid_view"]//li')

        for li in li_elements:
            order_num = li.xpath('.//em/text()')[0]
            movie_detail_url = li.xpath('.//div[@class="pic"]/a/@href')[0]
            movie_name = li.xpath('.//div[@class="hd"]/a/span')[0].xpath('text()')[0]
            movie_others = li.xpath('.//div[@class="bd"]/p')[0].xpath('text()')[1]
            movie_others = movie_others.replace('\n', '').split('/')
            movie_year = movie_others[0].strip()
            movie_country = movie_others[1].strip()
            movie_type = movie_others[2].strip()
            movie_get_time = datetime.now().strftime(f"%Y-%m-%d %H:%M:%S")
            movie_list.append(
                {'排名': order_num, '名称': movie_name, '链接': movie_detail_url, '年份': movie_year,
                 '国家': movie_country, '类型': movie_type, '获取时间': movie_get_time, '备注': None})
        return movie_list

    @staticmethod
    def get_movies_per_page(url, config):
        """
        获取豆瓣top250某一页的电影列表
        :param url: https://movie.douban.com/top250?start=0
        :param config: 全局配置字典
        :return:
        """
        response = None

        try:
            # 不设置heads容易被反爬，cookie可在浏览器登录后获取
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
                "cookie": "bid=A_gDSgds6bY; dbcl2=\"204688940:IUWNXhPqrio\"; ck=Wa89; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1748416144%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_id.100001.4cf6=ff9e6b6ae13fb1ed.1748416144.; _pk_ses.100001.4cf6=1; __utma=30149280.64665610.1748416145.1748416145.1748416145.1; __utmb=30149280.0.10.1748416145; __utmc=30149280; __utmz=30149280.1748416145.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utma=223695111.620860133.1748416145.1748416145.1748416145.1; __utmc=223695111; __utmz=223695111.1748416145.1.1.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; __yadk_uid=EvyM11DdCiywlh8pngXrmcX8ORcKjguc; push_noty_num=0; push_doumail_num=0; __utmb=223695111.4.9.1748416145"
            }
            # 不设置超时的话会一致阻塞，导致程序卡死
            if proxies is None:
                response = requests.get(url, headers=headers, timeout=30)
            else:
                response = requests.get(url, headers=headers, proxies=proxies, verify=False, timeout=30)
            response.encoding = 'utf-8'
            if response.status_code != 200:
                raise NetWorkError(response.status_code)
        except Exception as e:
            if response is not None:
                raise NetWorkError(response.status_code)
            else:
                raise NetWorkError()
        # logging.debug(f'response:\n{response.text}')

        return SpiderDemoDouBan.parse_movies_per_page(response.text)

    def get_movies_pages(self, movie_list_exist: list):
        """
        获取豆瓣top250的所有电影数据
        :param movie_list_exist: 本地已保存的数据文件列表
        :return:
        """
        base_url = self.config.BASE_URL
        max_page = self.config.MAX_PAGE
        new_movie_list = []

        logging_util.pure(f'开始爬取：来自 {base_url} 的最新电影信息...')
        # 使用支持请求速率控制的线程池，控制参数在config.py
        spider_tasks = []
        for i in range(0, max_page):
            url = base_url + f'?start={25 * i}'
            st = SpiderTask(url, self.get_movies_per_page, self.config)
            spider_tasks.append(st)
        self.thread_pool.submit_tasks(spider_tasks)

        for i, task in enumerate(spider_tasks):
            # 阻塞等待请求结束
            new_list = self.thread_pool.result(task)
            if new_list is None:
                continue
            logging_util.pure(f'已爬取电影列表({i + 1}/{len(spider_tasks)}) "{task.url}"...')

            # 去重
            new_movie_list += new_list

        total_movie_list = new_movie_list + movie_list_exist
        logging_util.pure(f'本次爬取结束')
        logging.debug(new_movie_list)

        return new_movie_list, total_movie_list

    def _spider_fun(self, movie_list_exist: list):
        """
        爬取网页数据并返回
        :param movie_list_exist: 本地已保存的数据文件列表
        :return:
        """
        # you can define custom params in config_def.py to user modify
        logging.error(f'PARMA1 = {self.config.CUSTOM['PARAM1']}')

        # 1. 爬取网页
        new_movie_list, total_movie_list = self.get_movies_pages(movie_list_exist)

        # 2. 对数据进行排序等处理（可选）
        pass

        # 3. 返回新数据和所有数据
        return new_movie_list, total_movie_list

    # The following overridden functions are optional.
    @override
    def _push_hook(self, data_list, new_data_list, config):
        return True

    @override
    def _send_email(self, new_data_list, data_list):
        super()._send_email(new_data_list, data_list)

    @override
    def _send_wecom(self, new_data_list, data_list):
        super()._send_wecom(new_data_list, data_list)


if __name__ == '__main__':
    print(f'爬虫程序 v{version}启动...')
    CommonInit.init(version, DEF_CONFIG_PATH, debug=False)
    # sm = SpiderDemo(CommonInit.get_config())
    sm = SpiderDemoDouBan(CommonInit.get_config())
    sm.run()

    # 打包成exe时，保留cmd窗口，查看程序结果或异常信息
    input("按回车键退出...")
