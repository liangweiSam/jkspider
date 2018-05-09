#-*- coding:utf-8 -*-
from lxml import etree
from pymongo import MongoClient
import re
import requests

# http://www.xicidaili.com/wn/
# http://www.data5u.com/free/gngn/index.shtml
# http://www.data5u.com/
# http://www.66ip.cn/index.html
# https://www.kuaidaili.com/free/inha/1/

# IP ipAdr port noName httpType

# test_url = http://2017.ip138.com/ic.asp

# Db JKSpider
# Collection Ipool 
# {'Ip' : '', 'ipAdr' : '', 'port' : '', 'noName' : '', 'httpType' : ''}


class Ippool(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}
		self.proxies = {
							"http": "http://111.90.179.42:8080",
							"https": "https://120.77.254.116:3128",
						}
		self.http = ['http://www.123cha.com/', 'http://www.ip5.me/', 'http://www.cip.cc/', 'http://ip.catr.cn/', 'http://service.cstnet.cn/ip',
					'http://www.64460.com/', 'http://ip.siteloop.net/', 'https://www.ipqi.co/', 'http://ip.t086.com/', 'http://ip.chaxun.la/',
					'http://ip.siteloop.net/', 'http://ip.cha127.com/']
		self.https = ['https://www.ipip.net/', 'https://www.boip.net/', 'https://www.slogra.com/', 'https://www.ipqi.co/#', 'https://dns.aizhan.com/']

	def connectTOdb(self):
		conn = MongoClient('127.0.0.1', 27017)
		db = conn.ipool
		collection = db.ip 
		# print(collection.find()[0])
		return collection


	def searchIP(self):
		url_nn = 'http://www.xicidaili.com/nn/%s' %('1')
		url_nt = 'http://www.xicidaili.com/nt/%s' %('1')	

		wy_url = 'http://www.data5u.com/free/gngn/index.shtml'
		
		# 筛选出速度 > 1.5s的
		# 西刺代理
		response = requests.get(url=url_nn, headers = self.headers)
		html = etree.HTML(response.text)
		ip_list = html.xpath('.//table[@id="ip_list"]')[0]

		odds = ip_list.xpath('.//tr[@class="odd"]')
		nOdds = ip_list.xpath('.//tr[@class=""]')
		ips = []	
		for odd in odds:
			o = {}
			o['ipAdr'] = odd.xpath('td[2]/text()')[0]
			o['port'] = odd.xpath('td[3]/text()')[0]
			o['noName'] = odd.xpath('td[5]/text()')[0]
			o['httpType'] = odd.xpath('td[6]/text()')[0]
			ips.append(o)

		for nOdd in nOdds:
			n = {}
			n['ipAdr'] = nOdd.xpath('td[2]/text()')[0]
			n['port'] = nOdd.xpath('td[3]/text()')[0]
			n['noName'] = nOdd.xpath('td[5]/text()')[0]
			n['httpType'] = nOdd.xpath('td[6]/text()')[0]
			ips.append(n)
		# 无忧代理IP
		# response = requests.get(url = wy_url, headers = self.headers, proxies = self.proxies)
		# html = etree.HTML(response.text)
		# wy_ipList = html.xpath('.//ul[@class="l2"]')[0]
		# for wy_ip in wy_ipList:
		# 	i = {}
		# 	lis = wy_ip.xpath('.//li')[0]
		# 	i['ipAdr'] = lis.xpath('li[1]/text()')
		# 	i['port'] = lis.xpath('li[2]/text()')
		# 	i['noName'] = lis.xpath('li[3]/a/text()')
		# 	i['httpType'] = lis.xpath('li[4]/a/text()')
		# 	ips.append(i)
		# print(ips)


		return ips
		
	def test_Ip(self, ipDict):

		test_Ip = ipDict['ipAdr']
		port = ipDict['port']
		noname = ipDict['noName']
		httpType = ipDict['httpType'].lower()

		if httpType == 'http':
			proxies = {'http' : 'http://%s:%s' %(test_Ip, port)}
			for i in self.http:
				try:
					response = requests.get(url = i, headers = self.headers, proxies = proxies, timeout = 5)
					if response.status_code == 200: break
				except Exception as e:
					print('网站不可用..')
					continue
		else:
			proxies = {'https' : 'https://%s:%s' %(test_Ip, port)}
			for i in self.https:
				try:
					response = requests.get(url = i, headers = self.headers, proxies = proxies, timeout = 5)
					if response.status_code == 200: break
				except Exception as e:
					print('网站不可用..')
					continue

		try:
			# if response.status_code == 200:
			response.encoding = 'gbk'
			result = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
			result = result.group(0)
			if test_Ip == result:
				# 使用mongoDB入库
				print('验证%s://%s:%s通过，可以入库' %(httpType, test_Ip, port))
			else:
				print('验证%s://%s:%s失败....' %(httpType, test_Ip, port))
				pass
		except Exception as e:
			print(e)			
		
		
		

	def test_Many_Ip(self):
		# ipDict = {'ipAdr' : '117.93.19.71', 'port' : '61234', 'noName' : '高匿', 'httpType' : 'http'}
		ips = self.searchIP()
		for ip in ips:	
			self.test_Ip(ip)



	def get_IP(self):
		ips = []
		# 从mongoDb中获取10个IP？

		return ips


if __name__ == '__main__':
	Ippool = Ippool()
	Ippool.test_Many_Ip()
	# Ippool.connectTOdb()