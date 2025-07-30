# -*- coding: utf-8 -*-
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, unquote
import urllib.parse
import urllib.request
import re


class InvalidURLError(Exception):
    pass


class KKRobotFileParser(RobotFileParser):
    def __init__(self, headers: dict = {}, *args, **kwargs):
        self.disallow_all = False
        self.allow_all = False
        self.headers = headers
        super().__init__(*args, **kwargs)

    def read(self) -> None:
        try:
            request = urllib.request.Request(self.url, headers=self.headers)
            f = urllib.request.urlopen(request)
        except urllib.error.HTTPError as err:
            if err.code in (401, 403):
                self.disallow_all = True
            elif 400 <= err.code < 500:
                self.allow_all = True
        else:
            raw = f.read()
            self.parse(raw.decode('utf-8').splitlines())

    def _add_entry(self, entry):
        if "*" in entry.useragents:
            if self.default_entry is None:
                self.default_entry = entry
            else:
                self.default_entry.rulelines.extend(entry.rulelines)
        else:
            self.entries.append(entry)


class Parse:
    def __init__(self, user_agent: str = None, test_url: str = None, headers: dict = {}):
        if user_agent is None:
            raise ValueError('user_agent must be a non-empty str')

        self.user_agent = user_agent

        if test_url is None:
            raise ValueError('test_url must be a non-empty str')

        if isinstance(headers, dict):
            headers['User-Agent'] = user_agent
            self.headers = headers
        else:
            self.headers = {
                'User-Agent': user_agent
            }

        self.validate_url(test_url)

        parsed_url = urlparse(test_url)
        self.rp = KKRobotFileParser(headers=self.headers)

        # 设置 robots.txt 文件的 URL
        robots_url = f'{parsed_url.scheme}://{parsed_url.netloc}/robots.txt'
        self.rp.set_url(robots_url)

        # 不存在 robots.txt 表示可以任何爬虫爬取
        try:
            self.rp.read()
        except Exception as e:
            self.rp = None

        if self.rp is not None:
            # 不存在 robots.txt 表示可以任何爬虫爬取
            if self.rp.default_entry is None and len(self.rp.entries) == 0:
                self.rp = None

        self.regex_dict = {}

    def validate_url(self, url: str):
        if not re.match(r'^https?://', url, re.IGNORECASE):
            raise InvalidURLError("url must start with http:// or https://")

        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise InvalidURLError("invalid url structure - missing scheme or network location")
        except:
            raise InvalidURLError("failed to parse url")

        return url

    def pattern_to_regex(self, pattern: str = ''):
        regex = []
        i = 0
        n = len(pattern)

        while i < n:
            c = pattern[i]
            if c == '*':
                regex.append('.*')
                i += 1
            elif c == '?':
                regex.append('.')
                i += 1
            else:
                if c in r'.^$*+?{}[]\|()':
                    regex.append('\\' + c)
                else:
                    regex.append(c)
                i += 1

        regex_pattern = '^' + ''.join(regex) + '$'
        return regex_pattern

    def can_crawl(self, url: str = ''):
        '''
        是否可安全爬取
        :param url: 链接
        :return:
        '''
        self.validate_url(url)

        if self.rp is None:
            return True

        parsed_url = urlparse(url)
        location = url.replace(f'{parsed_url.scheme}://{parsed_url.netloc}', '')
        if not location.endswith('/'):
            location += '/'

        checked_entries = [entry for entry in self.rp.entries if self.user_agent in entry.useragents]

        if len(checked_entries) == 0 and self.rp.default_entry is not None:
            checked_entries = [self.rp.default_entry]

        is_allowed = False
        if self.rp.can_fetch(self.user_agent, parsed_url.geturl()):
            is_allowed = True

            for entry in checked_entries:
                for r in entry.rulelines:
                    allowance = r.allowance
                    path = r.path
                    path = unquote(path)

                    if path not in self.regex_dict:
                        regex = self.pattern_to_regex(path)
                        compiled = re.compile(regex)
                        self.regex_dict[path] = compiled
                    else:
                        compiled = self.regex_dict[path]

                    if compiled.match(location):
                        if not allowance:
                            is_allowed = False
                            break
                        if allowance:
                            break

        return is_allowed
