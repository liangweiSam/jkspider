#-*- coding:utf-8 -*-
from lxml import etree
from pymongo import MongoClient
from gevent import monkey,pool; monkey.patch_socket()

import re
import requests
import random
import gevent
import time
'''
	http://www.xicidaili.com/wn/
	http://www.data5u.com/free/gngn/index.shtml
	http://www.data5u.com/
	http://www.66ip.cn/index.html
	https://www.kuaidaili.com/free/inha/1/
	http://ip.zdaye.com/#Free
	http://www.66ip.cn/mo.php?sxb=&tqsl=20&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=
	
	https://proxy.mimvp.com/free.php
'''
'''
	IP ipAdr port noName httpType
	test_url = http://2017.ip138.com/ic.asp

	Db JKSpider
	Collection Ipool 
	{'Ip' : '', 'ipAdr' : '', 'port' : '', 'noName' : '', 'httpType' : ''}
'''


class ProxyPool(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}
		self.proxies = {
							"http": "http://111.90.179.42:8080",
							"https": "https://120.77.254.116:3128",
						}
		# http://httpbin.org/get
		self.http = ['http://www.123cha.com/', 'http://www.ip5.me/', 'http://www.cip.cc/', 'http://ip.catr.cn/', 'http://service.cstnet.cn/ip',
					'http://www.64460.com/', 'http://ip.siteloop.net/', 'https://www.ipqi.co/', 'http://ip.t086.com/', 'http://ip.chaxun.la/',
					'http://ip.siteloop.net/', 'http://ip.cha127.com/', 'http://ip.taobao.com/ipSearch.html', 'http://www.365zn.com/ip/', 'http://ip.qq.com/', 
					'http://www.whatismyip.com.tw/', 'http://ip.lockview.cn/']
		self.https = ['https://www.ipip.net/', 'https://www.boip.net/', 'https://www.slogra.com/', 'https://www.ipqi.co/#', 'https://dns.aizhan.com/',
					 'https://ip.cn/', 'https://www.ipip5.com/', 'https://ip.51240.com/']

	def connectTOdb(self):
		time.sleep(1.5)
		conn = MongoClient('127.0.0.1', 27017)
		db = conn.ipool
		collection = db.ip 
		return collection

	def searchIp(self):
		kuaiUrl = 'https://www.kuaidaili.com/free/inha/1/'

	def searchIP(self, page):
		'''
			搜索IP
		'''
		url_nn = 'http://www.xicidaili.com/nn/%s' %(page)
		url_nt = 'http://www.xicidaili.com/nt/%s' %(page)	
		url_http = 'http://www.xicidaili.com/wt/%s' %(page)
		wy_url = 'http://www.data5u.com/free/gngn/index.shtml'
		
		# 筛选出速度 > 1.5s的
		# 西刺代理
		response = requests.get(url=url_nt, headers = self.headers)
		html = etree.HTML(response.text)
		ip_list = html.xpath('.//table[@id="ip_list"]')[0]

		odds = ip_list.xpath('.//tr[@class="odd"]')
		nOdds = ip_list.xpath('.//tr[@class=""]')
		ips = []	
		for odd in odds:
			o = {}
			o['ip'] = odd.xpath('td[2]/text()')[0]
			o['port'] = odd.xpath('td[3]/text()')[0]
			o['noname'] = odd.xpath('td[5]/text()')[0]
			o['httptype'] = odd.xpath('td[6]/text()')[0].lower()
			ips.append(o)

		for nOdd in nOdds:
			n = {}
			n['ip'] = nOdd.xpath('td[2]/text()')[0]
			n['port'] = nOdd.xpath('td[3]/text()')[0]
			n['noname'] = nOdd.xpath('td[5]/text()')[0]
			n['httptype'] = nOdd.xpath('td[6]/text()')[0].lower()
			ips.append(n)
		'''	
			无忧代理IP
			response = requests.get(url = wy_url, headers = self.headers, proxies = self.proxies)
			html = etree.HTML(response.text)
			wy_ipList = html.xpath('.//ul[@class="l2"]')[0]
			for wy_ip in wy_ipList:
				i = {}
				lis = wy_ip.xpath('.//li')[0]
				i['ipAdr'] = lis.xpath('li[1]/text()')
				i['port'] = lis.xpath('li[2]/text()')
				i['noName'] = lis.xpath('li[3]/a/text()')
				i['httpType'] = lis.xpath('li[4]/a/text()')
				ips.append(i)
			print(ips)
		'''
		return ips
		
	def test_Ip_From_Web(self, ipDict):
		'''
			测试抓取的IP
		'''
		test_Ip = ipDict['ip']
		port = ipDict['port']
		noname = ipDict['noname']
		httpType = ipDict['httptype'].lower()
		response = None

		if httpType == 'http':
			proxies = {'http' : 'http://%s:%s' %(test_Ip, port)}
			print('\n[正在验证%s' %(proxies['http']))
			for i in self.http:
				try:	
					response = requests.get(url = i, headers = self.headers, proxies = proxies, timeout = 5)
					if response.status_code == 200: 
						break
				except Exception as e:
					print('|%s网站不可用..' %(i))
					continue
		else:
			proxies = {'https' : 'https://%s:%s' %(test_Ip, port)}
			print('\n[正在验证%s' %(proxies['https']))
			for i in self.https:
				try:
					response = requests.get(url = i, headers = self.headers, proxies = proxies, timeout = 5)
					if response.status_code == 200:	
						break
				except Exception as e:
					print('|%s网站不可用..' %(i))
					continue
		try:
			if response is not None:
				# result = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
				result = re.search('\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{2,3}', response.text)
				result = result.group(0)
				if test_Ip == result:
					# 使用mongoDB入库
					self.insert_in_DB(ipDict)
					print('验证%s://%s:%s通过，结果为：%s, 已入库\n' %(httpType, test_Ip, port, result))
				else:
					print('验证%s://%s:%s失败, 结果为：%s....\n' %(httpType, test_Ip, port, result))
		except Exception as e:
			print(e)

	def search_and_insertDB(self, page):
		for i in self.searchIP(page):
			self.test_Ip_From_Web(i)
	
	def insert_in_DB(self, dict_In_list):
		dict_In_list = [{"ip":"113.236.93.112","port":1648},{"ip":"218.2.17.59","port":2671},{"ip":"211.93.54.175","port":6410},{"ip":"175.150.239.77","port":2589},{"ip":"114.99.16.183","port":6890},{"ip":"60.173.24.208","port":6890},{"ip":"123.152.66.172","port":2682},{"ip":"118.120.228.164","port":6534},{"ip":"117.43.53.69","port":5632},{"ip":"113.143.14.167","port":7689},{"ip":"114.234.24.95","port":2646},{"ip":"123.152.67.50","port":2682},{"ip":"119.5.181.80","port":3979},{"ip":"121.234.120.87","port":3456},{"ip":"113.223.101.38","port":7524},{"ip":"119.7.199.106","port":7684},{"ip":"1.85.72.147","port":7689},{"ip":"113.237.236.69","port":8943},{"ip":"113.137.81.229","port":1346},{"ip":"140.255.3.125","port":5649}]
		list = []
		for i in dict_In_list:
			i['httptype'] = 'http'
			list.append(i)

		collection = self.connectTOdb()
		collection.insert(list)

	def remove_from_DB(self, ip):
		collection = self.connectTOdb()
		collection.remove({'ip' : '%s' %(ip)})

	def test_Many_Ip(self):
		# ipDict = {'ipAdr' : '117.93.19.71', 'port' : '61234', 'noName' : '高匿', 'httpType' : 'http'}
		p = pool.Pool(6)
		threads = [p.spawn(self.search_and_insertDB, page) for page in range(1, 6)]
		gevent.joinall(threads)
		# for i in range(1, 10):
		# 	gevent.joinall([
		# 			gevent.spawn(self.search_and_insertDB, i),
		# 			gevent.spawn(self.search_and_insertDB, i+1),
		# 			gevent.spawn(self.search_and_insertDB, i+2),
		# 			gevent.spawn(self.search_and_insertDB, i+3),
		# 	])

		# 	i+= 4
		# for i in range(1, 5):
		# 	ips = self.searchIP(i)
		# 	for ip in ips:
		# 		self.test_Ip_From_Web(ip)

	def get_IP(self, httptype):
		'''
			IP池的使用：
				1. 当爬虫发现IP被ban时，从ip池中获取ip并验证
				2. 更换代理IP，再进行从新爬取。
				3. IP需要分https，http
		'''
		collection = self.connectTOdb()
		ips = []
		ipCursor = collection.find({'httptype' : '%s' %(httptype)})
		for i in range(0, ipCursor.count()):
			ips.append(ipCursor.next())
		# assert 1 > 5, print(len(ips))
		for i in range(0, len(ips)):
			ip = random.choice(ips)
			# usable = self.test_Ip(ip)
			usable = True
			if usable:
				print('-%s-可用....' %(ip['ip']))
				return ip
				break
			else:
				self.remove_from_DB(ip['ip'])
				print('不可用且从DB中移除.')

	def test_Ip(self, ipDict):
		test_Ip = ipDict['ip']
		port = ipDict['port']
		# noname = ipDict['noname']
		httpType = ipDict['httptype'].lower()
		response = None

		if httpType == 'http':
			proxies = {'http' : 'http://%s:%s' %(test_Ip, port)}
			print('\n[正在验证%s' %(proxies['http']))
			for i in self.http:
				try:	
					response = requests.get(url = i, headers = self.headers, proxies = proxies, timeout = 5)
					if response.status_code == 200: 
						break
				except Exception as e:
					print('|%s网站不可用..' %(i))
					continue
		else:
			proxies = {'https' : 'https://%s:%s' %(test_Ip, port)}
			print('\n[正在验证%s' %(proxies['https']))
			for i in self.https:
				try:
					response = requests.get(url = i, headers = self.headers, proxies = proxies, timeout = 5)
					if response.status_code == 200:	
						break
				except Exception as e:
					print('|%s网站不可用..' %(i))
					continue
		try:
			if response is not None:
				# result = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
				result = re.search('\d{2,3}\.\d{2,3}\.\d{2,3}\.\d{2,3}', response.text)
				result = result.group(0)
				if test_Ip == result:
					# 返回IP
					return True
					print('验证%s://%s:%s通过，结果为：%s, 已入库\n' %(httpType, test_Ip, port, result))
				else:
					print('验证%s://%s:%s失败, 结果为：%s....\n' %(httpType, test_Ip, port, result))
					return False
		except Exception as e:
			print(e)		


if __name__ == '__main__':
	ippool = ProxyPool()
	# ippool.get_IP('http')
	ippool.insert_in_DB('1')
	# ip = ippool.get_IP('http')
	# print(ip['ip'])
	# Ippool.connectTOdb()
	# Ippool.get_IP()