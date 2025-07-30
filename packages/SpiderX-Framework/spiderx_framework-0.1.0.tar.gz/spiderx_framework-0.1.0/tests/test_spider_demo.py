# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2025-05-28 19:08:24
import os
from pathlib import Path

import pytest
from utilsz import file_util, logging_util

from src.spider_demo.spider_demo import SpiderDemoDouBan
from src.spider_framework.common_init import CommonInit

spider: SpiderDemoDouBan or None = None
DEF_CONFIG_PATH = os.path.join(Path(__file__).resolve().parent.parent, 'src', 'spider_demo', 'configs', 'config_def.py')


@pytest.fixture
def __test_init():
    CommonInit.init('1.0.0', DEF_CONFIG_PATH, debug=False, init_params=False)
    global spider
    spider = SpiderDemoDouBan(CommonInit.get_config())


def __check_movie_detail(movie_detail: dict) -> bool:
    if movie_detail is None:
        return False
    if len(movie_detail) != 25:
        return False
    for element in movie_detail:
        if element is None or element == '':
            return False
    return True


def __test_detail_html(test_init, url) -> bool:
    global spider
    movie_detail_dict = SpiderDemoDouBan.get_movies_per_page(url, spider.config)
    if __check_movie_detail(movie_detail_dict):
        logging_util.pure(f'Success!: {url}')
        return True
    else:
        logging_util.pure(f'Failed!: {url}')
        return False


def __test_html_file(test_init, file_path: str) -> bool:
    movie_detail_str = file_util.read_file_to_string(file_path)
    movie_ditail_dict = SpiderDemoDouBan.parse_movies_per_page(movie_detail_str)
    if __check_movie_detail(movie_ditail_dict):
        logging_util.pure(f'Success!: {file_path}')
        return True
    else:
        logging_util.pure(f'Failed!: {file_path}')
        return False


def test_html_file(__test_init):
    current_path = os.getcwd()
    test_data_dir = os.path.join(current_path, 'test_data')
    test_file_list = file_util.get_file_list(test_data_dir, True)
    for file_path in test_file_list:
        assert __test_html_file(__test_init, file_path)


def test_detail_html(__test_init):
    assert __test_detail_html(__test_init, 'https://movie.douban.com/top250?start=0')
    assert __test_detail_html(__test_init, 'https://movie.douban.com/top250?start=25')
    assert __test_detail_html(__test_init, 'https://movie.douban.com/top250?start=50')
