# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2025-05-23 13:30:37
import logging
import os
import pprint
import time
import traceback
from datetime import datetime
from types import ModuleType

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from utilsz import logging_util, time_util, file_util, excel_util, email_util, str_util, wecom_util, json_util

from spiderx_framework.scheduler import Scheduler


class SpiderFramework:
    WEBHOOK_TEXT_MAX_SIZE = 2048
    WEBHOOK_MARKDOWN_MAX_SIZE = 4096

    def __init__(self, config: ModuleType, spider_func):
        self.config = config  # or DEFAULT_CONFIG
        self.spider_func = spider_func
        # 记得shutdown
        self.thread_pool = Scheduler(self.config.MAX_THREADS, self.config.RATE_LIMIT_TIME_WINDOW,
                                     self.config.RATE_LIMIT_COUNT)

    def __open_file(self, auto: bool):
        """
        自动打开电源文件或等待用户确认打开
        :param auto:
        :return:
        """
        if auto:
            logging_util.pure(f'****** 开始打开数据文件：{self.config.DATA_SAVE_PATH}... ')
            os.system(f'start excel "{self.config.DATA_SAVE_PATH}"')
        elif (s := input('是否打开数据文件（n/y）：')) == 'y':
            os.system(f'start excel "{self.config.DATA_SAVE_PATH}"')

    def _read_data(self):
        """
        从本地数据文件读取已有数据列表
        :return: data list
        """
        data_list = excel_util.read_excel_file(self.config.DATA_SAVE_PATH)
        logging.debug(f'{self.config.DATA_SAVE_PATH}:\n {pprint.pformat(data_list)}')
        if not data_list:
            data_list = []
        return data_list

    def _backup_data(self):
        """
        备份文件，始终保存在 self.config.DATA_SAVE_PATH
        :return:
        """
        if not os.path.exists(self.config.DATA_SAVE_PATH):
            return
        name_without_extension, extension = os.path.splitext(os.path.basename(self.config.DATA_SAVE_PATH))

        new_file_name = datetime.now().strftime(f"backup_{name_without_extension}_%Y-%m-%d_%H%M%S") + extension
        new_file_path = os.path.join(os.path.dirname(self.config.DATA_SAVE_PATH), new_file_name)
        file_util.copyfile(self.config.DATA_SAVE_PATH, new_file_path)

    def _save_data(self, data_list):
        """
        保存列表到excel文件
        :param data_list:
        :return:
        """
        if not data_list:
            return
        try:
            excel_util.write_excel_file(self.config.DATA_SAVE_PATH, data_list)
        except Exception as e:
            logging.error(traceback.format_exc())
            return None
        return data_list

    def _send_email_by_config(self, title, content, payload_enable, payload_show_name, config):
        """
        通过config里的邮箱配置发送邮件
        :param title:
        :param content:
        :param payload_enable:
        :param payload_show_name:
        :param config:
        :return:
        """
        email_config = config.PUSH_NOTIFICATION['PUSH_CHANNEL']['EMAIL']
        server = email_util.create_email(
            email_config['SMTP_SERVER'], email_config['FROM_ADDR'], email_config['AUTH_CODE'])
        if payload_enable:
            with open(config.DATA_SAVE_PATH, 'rb') as f:
                email_util.send_email(server, email_config['TO_ADDR'],
                                      title,
                                      content,
                                      payload=f.read(), payload_name=payload_show_name)
        else:
            email_util.send_email(server, email_config['TO_ADDR'], title, content)
        email_util.quit_email(server)

    def _send_email(self, new_data_list, data_list):
        self._send_email_by_config(f'来自"{self.config.BASE_URL}"的数据',
                                   f'本次爬取新数据{len(new_data_list)}条， 截至目前共收录{len(data_list)}条！',
                                   True,
                                   'data.xlsx',
                                   self.config)

    def _send_wecom_by_config(self, content, config):
        """
        通过配置里的企业微信配置发送企业微信消息消息
        :param content:
        :param config:
        :return:
        """
        logging.debug(f'企业微信发送内容：\n{content}')
        logging.debug(f'企业微信发送内容大小：{str_util.get_size(content)}')
        key = config.PUSH_NOTIFICATION['PUSH_CHANNEL']['WECOM']['WEBHOOK_KEY']
        base_response = wecom_util.send_robot_webhook_msg(key, markdown=content)
        if base_response['code'] != 200:
            logging.error(f'企业微信发送内容：\n{content}')
            logging.error(f'发送失败：{json_util.dumps(base_response)}')
            return False
        return True

    def _send_wecom(self, new_data_list, data_list):
        """
        通过企业微信的群机器人发送新爬取到的新数据
        :param data_list:
        :param new_data_list:
        :return:
        """
        send_data_list = new_data_list
        data_count = len(send_data_list)
        if data_count <= 0:
            return

        sned_title = f'## {data_count}部新片速递：\n'
        send_content = ''
        for index, new_data in enumerate(send_data_list):
            send_content += f'{index + 1}. {str(new_data)}\n'
            if str_util.get_size(sned_title + send_content) > SpiderFramework.WEBHOOK_MARKDOWN_MAX_SIZE:
                send_content = str_util.truncate_str_to_size(
                    send_content,
                    SpiderFramework.WEBHOOK_MARKDOWN_MAX_SIZE - str_util.get_size(sned_title) - str_util.get_size(
                        '......'))
                send_content += '......'
                break
        send_msg = sned_title + send_content
        return self._send_wecom_by_config(send_msg, self.config)

    def _spider_run(self):
        """
        爬取网页主流程
        :return:
        """
        start_time = time.time()
        logging_util.pure(f'****** 开始爬取...')
        data_list_exist = self._read_data()
        new_data_list, data_list = self.spider_func(data_list_exist)
        time_interval = time_util.format_time_interval(start_time, time.time())
        logging_util.pure(f'本次爬取耗时：{time_interval}')
        if new_data_list is None or len(new_data_list) == 0:
            return
        logging_util.pure(f'****** 开始备份：{os.path.dirname(self.config.DATA_SAVE_PATH)}...')
        self._backup_data()
        logging_util.pure(f'****** 开始保存：{self.config.DATA_SAVE_PATH}...')
        self._save_data(data_list)
        if hasattr(self.config, 'COPY_SAVE_PATH'):
            logging_util.pure(f'****** 开始保存副本：{self.config.COPY_SAVE_PATH}...')
            file_util.copyfile(self.config.DATA_SAVE_PATH, self.config.COPY_SAVE_PATH)
        self._save_data(data_list)
        push_config = self.config.PUSH_NOTIFICATION
        if push_config and push_config['ENABLED'] & self._push_hook(data_list, new_data_list, self.config):
            push_channel = push_config['PUSH_CHANNEL']
            if push_channel['EMAIL'] and push_channel['EMAIL']['ENABLED']:
                logging_util.pure(f'****** 开始发送邮件："{self.config['EMAIL']['TO_ADDR']}"... ')
                self._send_email(new_data_list, data_list)
            if push_channel['WECOM'] and push_channel['WECOM']['ENABLED']:
                logging_util.pure(f'****** 开始发送企业微信... ')
                self._send_wecom(new_data_list, data_list)
            # OPEN_FILE为false时，等待用户输入，导致阻塞
            self.__open_file(push_channel['OPEN_FILE'])

    def _push_hook(self, data_list, new_data_list, config) -> bool:
        """
        推送前提供钩子：1. 数据预处理；2.是否推送
        :param data_list:
        :param new_data_list:
        :param config:
        :return:
        """
        return True

    def run(self):
        """
        循环爬取或单次爬取
        :return:
        """
        if self.spider_func is None:
            logging.error('error, please register spider fun first!')
            return

        if getattr(self.config, 'INTERVAL_MINUTES') and self.config.INTERVAL_MINUTES > 0:
            # 周期性执行爬取任务
            # 设置调度器日志级别为 WARNING，避免过多打印干扰
            logging.getLogger('apscheduler').setLevel(logging.WARNING)
            scheduler = BlockingScheduler()
            # 立即运行一次，之后周期性执行
            trigger = OrTrigger([DateTrigger(run_date=datetime.now()), IntervalTrigger(minutes=1)])
            scheduler.add_job(self._spider_run, trigger)
            scheduler.start()
        else:
            # 只执行一次爬取任务
            self._spider_run()

        self.thread_pool.destroy()
