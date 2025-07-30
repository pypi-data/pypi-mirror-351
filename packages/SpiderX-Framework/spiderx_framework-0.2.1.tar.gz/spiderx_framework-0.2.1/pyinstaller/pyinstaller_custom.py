# encoding: utf-8
# desc: 自定义打包脚本 pyinstaller，必须处于当前目录执行打包命令，否则执行一半会中断
# auth: Kasper Jiang
# date: 2024-10-12 16:16:06
import os.path
import sys

# 必须先将上级目录（根目录）添加到python搜索路径，否则import报错找不到模块
cur_dir = os.path.dirname(__file__)
project_dir = os.path.dirname(cur_dir)
sys.path.append(f'{project_dir}')

# VERSION引入必须放在sys.path.append后面，否则运行找不到该模块
from src.spiderx_demo import version
from src.spiderx_demo.spider_demo import DEF_CONFIG_PATH
import PyInstaller.__main__

src_path = fr'{project_dir}\src'
main_path = fr'{src_path}\spiderx_demo\spider_demo.py'
config_path = DEF_CONFIG_PATH


def get_version():
    return version


def get_project_name():
    return 'spiderMovie'


def get_app_name():
    # return f'{get_project_name()}_{get_version()}'
    return f'{get_project_name()}'


if __name__ == '__main__':
    print(f'{os.path.curdir}')
    PyInstaller.__main__.run([
        '--onefile',  # 生成单个exe文件
        '--console',  # 带cmd窗口
        f'--add-data={config_path};.',  # 打包资源文件：原始目录;目标目录
        f'--name={get_app_name()}',  # 指定最终程序名称
        f'--clean',  # 清楚缓存
        # f'--debug=imports',         # 可查看打包了哪些模块
        # f'--log-level=TRACE',       # 日志最多，可查看打包了哪些模块
        # f'--hidden-import=a.b',   # 如pyinstaller未自动打包某些模块，可手动导入
        # f'--hidden-import=c.d',
        # f'--paths={src_path}',  #已废弃，改用--hidden-import参数;默认指向项目根路径，改为src目录
        f'{main_path}'  # 程序入口，必须放在参数列表的最后
    ])
