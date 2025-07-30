# SpiderFramework
爬取网页数据框架，并保存到data目录里的excel文件；
1. 支持自定义请求、解析网页
2. 支持指定时间窗口内的爬取速度控制：匀速爬取、最快爬取
3. 支持爬取失败时进行重试和延迟
4. 支持自动打开数据excel文件
5. 支持自动发送email
6. 支持自动发送企业微信

## 使用说明
首次运行后会生成配置文件config.py，配置如下(最新参考config_def.py)：  
* LOG_LEVEL：日志等级，例如："debug"、"info"、"warning"、"error"、"fatal"
* BASE_URL: 爬取网页的地址，例如："https://movie.douban.com"
* MAX_PAGE：爬取最大的页数，例如：10
* MAX_THREADS：同时爬取页面的线程数，不宜过多以免被反爬虫，5-10比较合适
* RETRY_TIMES：网络请求失败时的重试次数，例如：5
* RETRY_DELAY_MS：请求失败后重试的延迟，单位毫秒，例如5000
* INTERVAL_MINUTES：是否定时爬取网页，0：只爬取1次；>0：爬取时间间隔，单位为分钟，例如设为1表示每1分钟爬取一次
* RATE_LIMIT_TIME_WINDOW：限流相关参数，时间窗口，单位ms，例如20 * 1000
* RATE_LIMIT_COUNT：时间窗口范围内最多执行网络请求次数，例如30
* DATA_SAVE_PATH：爬取到的数据文件保存路径，备份文件也保存同目录下
* COPY_SAVE_PATH：有时想拷贝一份数据到其他目录，可设置COPY_SAVE_PATH。原始文件保存在MOVIE_SAVE_PATH。例如：r"D:/data.xlsx"
* PUSH_NOTIFICATION:爬取完成后是否进行消息推送
  * ENABLED：True、False
  * PUSH_CHANNEL：推送渠道，支持打开本地文件、email、企业微信
    * OPEN_FILE：爬取完成后是否自动打开本地数据文件，True、False
    * EMAIL：
        * ENABLED：爬取结束后是否自动发送邮件：True、False
        * SMTP_SERVER：发送邮件的smtp服务器，例如："smtp.163.com"
        * FROM_ADDR：发送时使用的发送者邮箱地址，例如："sender@163.com"
        * AUTH_CODE：发送时使用的发送者邮箱的授权码，例如："TPn8tKfF45612345"
        * TO_ADDR：发送给谁的邮箱地址，例如："receiver.163.com"
    * WECOM：
        * ENABLED：爬取结束后是否自动发送企业微信消息：True、False
        * WEBHOOK_KEY：企业微信的群机器人的webhook的key值，程序将通过该机器人发送消息，可查看手机端企业微信-某个群-设置-机器人，例如："ce57445a-ba75-4e6c-9200-41687b1cfdef"
* CUSTOM：自定义配置参数，后续可用于框架和二次开发时使用
  * PARAM1：用户自定义参数PARAM1

## 项目说明
### 执行依赖安装
pip install -r requirements.txt

### 依赖固化
pip freeze > requirements.txt

### 打包模块
1. pip install build
2. rmdir /S /Q "dist" "src\Spider_Framework.egg-info" & python -m build

### 打包exe
cd pyinstaller; python.exe .\pyinstaller_custom.py; cd ..

### 发布模块到pypi
1. pip install twine  
2. python -m twine upload --repository pypi dist/*
3. 输入用户名和API Token。