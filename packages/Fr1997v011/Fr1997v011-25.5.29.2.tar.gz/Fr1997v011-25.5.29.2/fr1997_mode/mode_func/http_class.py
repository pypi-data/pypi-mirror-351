import json
import random
import requests
from .base_class import *

us = config_dict['base_ua']


# requests 封装
class HttpJike(object):
    us = us

    def __init__(self):
        self.status_code = 500
        self.msg = 'ok'
        self.text = None
        self.json = None
        self.ret_url = None

    # cookie 分隔
    @staticmethod
    def cookie_format(cookie):
        cookie_dict = {}
        c = cookie.split(";")
        for i in c:
            cc = i.split('=')
            if len(cc) > 1:
                cookie_dict[str(cc[0]).strip()] = str(cc[1]).strip()
            else:
                cookie_dict[str(cc[0]).strip()] = ''
        return cookie_dict

    # ip代理 隧道代理
    @staticmethod
    def proxies_choose(p=1, httpx=0):
        # 注意:目前只有 1,2 两个可以使用  httpx特殊请求
        if p is None:
            p = random.randint(1, 2)

        proxy = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['proxy']
        port = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['port']
        acc = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['acc']
        pwd = config_dict["proxy"]["tunnel"][f"proxy_{p}"]['pwd']

        proxies = {
            "http": f"http://{acc}:{pwd}@{proxy}:{port}/",
            "https": f"http://{acc}:{pwd}@{proxy}:{port}/"
        }
        if httpx == 1:
            proxies = {
                "http://": f"http://{acc}:{pwd}@{proxy}:{port}/",
                "https://": f"http://{acc}:{pwd}@{proxy}:{port}/"
            }
        return proxies

    # scrapy 代理选择 数据返回
    @classmethod
    def proxies_choose_dict(cls, p):
        # 注意:目前只有 1,2,3 两个可以使用
        proxies_dict = {
            'proxy': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['proxy'],
            'port': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['port'],
            'acc': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['acc'],
            'pwd': config_dict["proxy"]["tunnel"][f"proxy_{p}"]['pwd']
        }
        return proxies_dict

    # 异步代理 的使用
    @staticmethod
    def aiohttp_proxy():
        ret = []
        ip_tunnel = config_dict['proxy']['tunnel']
        for i in ip_tunnel:
            ret.append({
                'proxy': f'http://{ip_tunnel[i]["proxy"]}:15818',
                'a': ip_tunnel[i]['acc'],
                'p': ip_tunnel[i]['pwd'],
            })
        return ret

    @staticmethod
    def get_headers(headers):
        if headers is None:
            return config_dict['base_headers']
        return headers

    @classmethod
    def get(cls, url, headers=None, proxies=None):
        req = cls()
        try:
            response = requests.get(
                url=url,
                headers=cls.get_headers(headers=headers),
                proxies=proxies
            )
            req.status_code = response.status_code
            req.ret_url = response.url
            req.text = response.text
            req.json = response.json()

            if response.status_code != 200:
                req.msg = '状态码错误'
        except Exception as e:
            req.msg = f'err {e}'
        return req

    @classmethod
    def post(cls, url, headers=None, data=None):
        req = cls()
        try:
            response = requests.post(
                url=url,
                headers=cls.get_headers(headers=headers),
                data=json.dumps(data),
            )
            req.status_code = response.status_code
            req.text = response.text
            req.json = response.json()

            if response.status_code != 200:
                req.msg = '状态码错误'
        except Exception as e:
            req.msg = f'err {e}'
        return req

    # 代理
    @classmethod
    def http_ip(cls, ip):
        proxies = {
            'https': ip,
            'http': ip
        }
        return proxies

    # 返回一个http代理
    @classmethod
    def http_proxy(cls):
        return {'https': '49.70.176.21:31919', 'http': '49.70.176.21:31919'}

    @classmethod
    def params_link(cls, url, params):
        return f"{url}?" f"{'&'.join([f'{k}={v}' for k, v in params.items()])}"

    @classmethod
    def base_headers(cls):
        try:
            return config_dict['base_headers']
        except:
            return {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46'}

    @staticmethod
    def scrapy_simple_sitting(ts=0.1, tt=8, log=False, cookie=True):
        def_sitting = {
            "LOG_ENABLED": log,  # 日志开启
            "HTTPERROR_ALLOWED_CODES": [i for i in range(999)],  # 允许所有 HTTP 错误码
            "REDIRECT_ENABLED": False,  # 禁用重定向
            "DOWNLOAD_DELAY": ts,  # 每次请求间隔 1 秒
            "CONCURRENT_REQUESTS": tt,  # 最大并发请求数
            "DOWNLOADER_MIDDLEWARES": {
                'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 1,  # 启用代理中间件
            }
        }
        if cookie:
            def_sitting['COOKIES_ENABLED'] = False
        return def_sitting
