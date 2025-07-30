# debug、info、warning、error、fatal
LOG_LEVEL = "error"

# mp4电影网的首页地址，例如："https://www.ddmp4.cc"
# 同一个网站可能部分域名有反爬虫，部分没有，可能和域名解析服务器配置有关
# mp4电影网特征：
# 1. 部分域名没有反爬虫，例如www.xlmp4.cc、www.gomp4.cc；部分有例如：www.ddmp4.cc
# 2. 10秒内小于20个请求，确定是爬虫时禁用该ip 10秒请求。（通过jmeter测试）
# 3. 要么不触发服务器，例如1个线程；要么反正会触发特征2，但尽可能快的在未触发前发送请求，但请求重试次数*延迟时间后不处于10秒禁用时段内，
# 例如MAX_THREADS=5、RETRY_TIMES=5、RETRY_DELAY_MS=5000
BASE_URL = "https://www.ddmp4.cc"

# 最新电影页面爬取最大的页数，例如：10
MAX_PAGE = 10
# 同时爬取页面的线程数，不宜过多以免被反爬虫，1-5比较合适，最保险是1；
# 可配合RETRY_TIMES、RETRY_DELAY_MS调参
MAX_THREADS = 10
# 网络请求失败时的重试次数
RETRY_TIMES = 5
# 单个网页尝试请求次数之间的间隔，单位毫秒，效果比RETRY_TIMES好
RETRY_DELAY_MS = 5000
# 是否定时爬取网页，0：只爬取1次；>0：爬取时间间隔，单位为分钟，例如设为1表示每1分钟爬取一次
INTERVAL_MINUTES = 0

# 限流相关参数
# 时间窗口，单位ms
RATE_LIMIT_TIME_WINDOW = 20 * 1000
# 时间窗口范围内最多执行网络请求次数
RATE_LIMIT_COUNT = 30


# 爬取到的数据文件保存路径，备份文件也保存同目录下
DATA_SAVE_PATH = r"./data/data.xlsx"
# 有时想拷贝一份数据到其他目录，可设置COPY_SAVE_PATH。原始文件保存在MOVIE_SAVE_PATH。
# 因为windows的路径\会转义，所以用r表示原始字符串。例如：r"D:/movie.xlsx"、r".\movie.xlsx"、r"\\192.168.1.2\home\movie.xlsx"
# COPY_SAVE_PATH = r"D:/data.xlsx"

# 爬取完成后是否进行消息推送
PUSH_NOTIFICATION = {
    "ENABLED": True,
    # 推送渠道，支持打开本地文件、email、企业微信
    "PUSH_CHANNEL": {
        # 爬取完成后是否自动打开本地数据文件，true或false
        "OPEN_FILE": False,
        # 爬取结束后是否自动发送邮件
        "EMAIL": {
            "ENABLED": False,
            # 发送邮件的smtp服务器，例如："smtp.163.com"
            "SMTP_SERVER": "replace your stmp server",
            # 发送时使用的发送者邮箱地址，例如："sender@163.com"
            "FROM_ADDR": "replace your from addr",
            # 发送时使用的发送者邮箱的授权码，例如："TPn8tKfF45612311"
            "AUTH_CODE": "replace your auth code",
            # 发送给谁的邮箱地址，例如："receiver@163.com"
            "TO_ADDR": "replace your to_addr",
        },
        # 爬取结束后是否自动发送企业微信消息
        "WECOM": {
            "ENABLED": False,
            # 企业微信的群机器人的webhook的key值，程序将通过该机器人发送消息，可查看手机端企业微信-某个群-设置-机器人，例如："ce57445a-ba75-4e6c-9200-41687b1cfdaa"
            "WEBHOOK_KEY": "replace your webhook key",
        },
    },
}

# 自定义配置参数，后续可用于框架和二次开发时使用
CUSTOM = {
    # 参数1
    "PARAM1": True,
}
