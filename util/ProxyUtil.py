# -*- coding: utf-8 -*-
import random
import time
#from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
from urllib.request import Request, urlopen
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from pdjus.conexao.Conexao import Singleton

class RequestProxy:
    def __init__(self):
        ua = UserAgent()  # From here we generate a random user agent
        self.proxies = []  # Will contain proxies [ip, port]

        proxies_req = Request('https://www.sslproxies.org/')
        proxies_req.add_header('User-Agent', ua.random)
        proxies_doc = urlopen(proxies_req).read().decode('utf8')

        soup = BeautifulSoup(proxies_doc, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')

        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            self.proxies.append({
                'ip': row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string,
                'source':  row.find_all('td')[3].string
            })

        # Choose a random proxy
        self.random_proxy()

    def random_proxy(self):
        proxy_index = random.randint(0, len(self.proxies) - 1)
        self.current_proxy = self.format_proxy(self.proxies[proxy_index])

    def get_proxy_list(self):
        return self.proxies

    def get_address(self,proxy):
        return "{0}:{1}".format(proxy['ip'], proxy['port'])

    def format_proxy(self,proxy):
        """ Method is heavily used for Logging - make sure we have a readable output

        :return: The address representation of the proxy
        """
        return "{0}".format(self.get_address(proxy))





class ProxyUtil(object, metaclass=Singleton):

    def __init__(self):
        self.__req_proxy = None

    def init_proxy(self):
        start = time.time()

        self.__req_proxy = RequestProxy()

        print("Initialization took: {0} sec".format((time.time() - start)))
        print("Size: {0}".format(len(self.__req_proxy.get_proxy_list())))
        print("ALL = {0} ".format(self.__req_proxy.get_proxy_list()))

    def get_proxy_ip(self, proxy,random=True):
        if proxy:
            if not self.__req_proxy:
                self.init_proxy()

            if random:
                self.__req_proxy.random_proxy()

            print("Using " + str(self.__req_proxy.current_proxy))
            return ({'http': str(self.__req_proxy.current_proxy),'https': str(self.__req_proxy.current_proxy)})
        else:
            return {}

