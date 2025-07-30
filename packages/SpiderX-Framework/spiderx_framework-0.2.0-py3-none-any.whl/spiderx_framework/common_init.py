# encoding: utf-8
# desc: 
# auth: Kasper Jiang
# date: 2024-09-29 18:04:39
import argparse
import logging
import os
import sys

from utilsz import file_util, module_util, time_util

# 全局配置
CONFIG_FILE_NAME = 'config.py'
CONFIG_LOAD_NAME = 'config'
DEF_CONFIG_IN_EXE_PATH = 'config_def.py'


class CommonInit:
    static_input_args = argparse.Namespace()
    static_config = {}
    static_default_config = {}
    static_init_flag = False
    version = "1.0.0"
    def_config_path = None

    @staticmethod
    def get_def_config_path():
        """
        获取程序所在路径，兼容项目和单个执行文件的路径获取
        :return:
        """
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包后的可执行文件（单文件模式），配置文件在临时解压目录
            return os.path.join(sys._MEIPASS, DEF_CONFIG_IN_EXE_PATH)
        else:
            # 如果是未打包的代码，配置文件在项目目录下
            return CommonInit.def_config_path

    @staticmethod
    def init_config():
        """
        初始化配置参数：
        1. 如果本地存在配置文件，则读取配置文件
        2. 如果本地不存在，且用户设置了默认配置，则保存默认配置到本地文件
        注意：logging初始化前不要使用，否则logging初始化后，会生成2个logger，导致输出2遍
        :return:
        """
        if not os.path.exists(CONFIG_FILE_NAME):
            config_def_path = CommonInit.get_def_config_path()
            file_util.copyfile(config_def_path, CONFIG_FILE_NAME)
        CommonInit.static_config = module_util.load_module(CONFIG_LOAD_NAME, CONFIG_FILE_NAME)
        # 注意：logging初始化前不要使用，否则logging初始化后，会生成2个logger，导致输出2遍
        # print(CommonInit.static_config)

    @staticmethod
    def init_log():
        # log level支持3处设置：init参数（调试时使用）、命令行参数（无config的程序使用）、config配置文件（有config的程序使用）
        # 最接近程序运行时刻优先级越高：init参数 > 命令行参数 > config配置文件
        if getattr(CommonInit.static_input_args, 'debug', False):
            log_level = logging.DEBUG
        elif hasattr(CommonInit.static_config, 'LOG_LEVEL'):
            match CommonInit.static_config.LOG_LEVEL.strip().lower():
                case 'debug':
                    log_level = logging.DEBUG
                case 'info':
                    log_level = logging.INFO
                case 'warning':
                    log_level = logging.WARNING
                case 'error':
                    log_level = logging.ERROR
                case 'fatal':
                    log_level = logging.FATAL
                case _:
                    log_level = logging.INFO
        else:
            log_level = logging.INFO

        # 创建一个logger，不指定name则获取根logger
        logger = logging.getLogger()
        logger.setLevel(log_level)
        # logging.getLogger("requests").setLevel(log_level)
        # logging.getLogger("urllib3").setLevel(log_level)

        # 创建一个handler，用于写入日志文件
        file_util.create_parent_directory('log/')
        fh = logging.FileHandler(f'log/log_{time_util.get_cur_datetime_str(f'%Y%m%d_%H%M%S')}.log', mode='w',
                                 encoding='utf-8')
        fh.setLevel(log_level)

        # 创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        # logging默认输出到stderr，导致所有日志都是红色的
        ch.setStream(sys.stdout)

        # 创建一个formatter，用于设置日志格式
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s(): %(message)s')

        # 设置handler的格式
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 为logger添加handler
        logger.addHandler(fh)
        logger.addHandler(ch)
        # logging.getLogger("urllib3").addHandler(fh)
        # logging.getLogger("urllib3").addHandler(ch)
        # logging.getLogger("requests").addHandler(fh)
        # logging.getLogger("requests").addHandler(ch)

        # stream=sys.stdout：logging默认输出到stderr，导致所有日志都是红色的
        # logging.basicConfig(format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(funcName)s(): %(message)s',
        #                     level=log_level, stream=sys.stdout,
        #                     filename=f'log/log_{get_cur_datetime_str(f'%Y%m%d_%H%M%S')}.log',
        #                     filemode='w')

    @staticmethod
    def parse_params():
        parser = argparse.ArgumentParser(
            description='将windows系统自动重启一次。因为本人家用电脑重装win10'
                        '系统后，第一次手动启动后总是黑屏（但已进入系统），必须按重启键才能点亮屏幕，所以用此工具自动执行重启系统功能')
        # action='store_true': 只需要-v，不需要后面再跟参数
        parser.add_argument('-v', '--version', action='store_true', help='print app version')
        parser.add_argument('-d', '--debug', action='store_true', help='print debug info')
        return parser.parse_args()

    @staticmethod
    def init(version, def_config_path, debug=False, init_params=True):
        """
        :param version: 程序的版本号，用于程序运行时 -v 参数的输出打印
        :param def_config_path: config_def.py文件路径，供用户添加自定义配置参数，所以不放在此模块里。
        :param init_params: 解析程序运行时带入参数；部分场景例如单元测试时自动传入的参数会导致解析错误并自动退出，可置为False
        :param debug:
        :return:
        """
        CommonInit.version = version
        CommonInit.def_config_path = def_config_path
        if CommonInit.static_init_flag:
            return
        if init_params:
            CommonInit.static_input_args = CommonInit.parse_params()
        if debug:
            CommonInit.static_input_args.debug = True

        # config包含log level配置，所以放前面，但config就无法使用log，只能用print
        CommonInit.init_config()
        CommonInit.init_log()
        CommonInit.static_init_flag = True

    @staticmethod
    def run_base_cmd():
        cmd = CommonInit.static_input_args
        if cmd.version:
            print(f'Version: {CommonInit.version}')
            return False

        return True

    @staticmethod
    def get_config():
        return CommonInit.static_config
