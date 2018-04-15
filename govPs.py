# -*- coding:utf-8 -*-
import requests
from etree import lxml


class govPs(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}



	def searchBusiness(self, company):
		url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
		data = ''
		requests.get