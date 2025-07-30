## 关于这个项目

**kkrobots** 是一款保证安全爬虫的工具，在爬取任何请求前调用 **Parse** 对象的 **can_crawl()** 方法即可判断是否符合 **robots.txt** 协议。

## 使用流程
使用流程非常简单，在每次爬虫前调用即可：
```python
from kkrobots import Parse

if __name__ == '__main__':
    parse = Parse(
        user_agent='your spider',
        # 该站点任意链接即可
        test_url='https://xxxx.com/xxx/xxx/xxx'
    )

    can_crawl = parse.can_crawl('https://xxxx.com/xxx/xxx')

    # 下方执行你的爬虫逻辑
    if can_crawl:
        pass

```

## 关于作者
微信公众号：Python卡皮巴拉

🌟【Python卡皮巴拉】—— 你的Python修炼秘籍，代码界的“神兽”驾到！🌟
