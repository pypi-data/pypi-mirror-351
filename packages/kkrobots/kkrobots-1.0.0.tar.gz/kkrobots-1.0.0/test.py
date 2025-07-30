# -*- coding: utf-8 -*-
from kkrobots import Parse

if __name__ == '__main__':
    parse = Parse(
        user_agent='your spider',
        # 该站点任意链接即可
        test_url='https://xxxx.com'
    )

    can_crawl = parse.can_crawl('https://xxxx.com/xxx/xxx')

    # 下方执行你的爬虫逻辑
    if can_crawl:
        pass
