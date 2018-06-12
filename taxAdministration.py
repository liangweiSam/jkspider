# -*- coding:utf-8 -*-
from lxml import etree
from user_agent_Pool import user_agent
from gevent.pool import Pool
from gevent import monkey;monkey.patch_socket()

import gevent
import requests
import csv
import re
import os
import csv
import random
import xlrd, xlwt
import json
import time

class tax(object):

	def __init__(self):
		UA = random.choice(user_agent)
		self.headers  = {'User-Agent' : UA,
						'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						'Connectionn' : 'keep-alive'
						}
		self.proxies = {
						'http': '',
						'https': '',
						}
		self.num = 0
		self.threads = None
		self.sess = requests.Session()

	def getData(self, date):
		url = 'http://hd.chinatax.gov.cn/xxk/action/ListXinxikucomXml.do?dotype=casetime&id=%s' %(date)
		response = requests.get(url = url, headers = self.headers, proxies = self.proxies)
		html = etree.HTML(response.content)
		ids = html.xpath('.//item/@id')
		row = []
		if response.status_code is 200 and len(ids) > 0:
			for i in ids:
				fileUrl = 'http://hd.chinatax.gov.cn/xxk/action/GetArticleView1.do?op=xxkweb&id=%s' %(i)
				response2 = requests.get(url = fileUrl, headers = self.headers, proxies = self.proxies)
				fileHtml = etree.HTML(response2.content)
				fileData = fileHtml.xpath('/html/body/table/tr/td//tr')
				# print(response2.text)
				t = []
				for file in fileData:
					if len(file.xpath('./td[2]/text()')) > 0:
						t.append(file.xpath('./td[2]/text()')[0])
					else:
						t.append('  ')
				print(t)
				row.append(list(t))
			print('采集完成..')
		else:
			print('网络被拒绝 或者 没有获取到数据')
	
		self.saveData(row, date)

	def saveData(self, datas, date):
		headers = ['纳税人名称', '纳税人识别号', '组织机构代码', '注册地址', '法定代表人或者负责人姓名、性别、证件名称及号码', 
					'负有直接责任的财务负责人姓名、性别、证件名称及号码', '负有直接责任的中介机构信息及其从业人员信息', 
					 '案件性质', '主要违法事实, 相关法律依据及税务处理处罚情况']

		try:
			with open('%s税务.csv' %(date), 'w') as f:
				f_csv = csv.writer(f)
				f_csv.writerow(headers)
				f_csv.writerows(datas)
		except Exception as e:
			print(e)			 


	def getDataFromEx(self):
		'''
			从excel获取数据
		'''
		workBook = xlrd.open_workbook(r'SpiderFiles/所有报告单new.xls')
		sheet1_name = workBook.sheet_names()[0]
		sheet1 = workBook.sheet_by_name(sheet1_name)
		rows = sheet1.col_values(0)[1:]
		last_line = ''
		new_rows = []
		try:
			with open('progressRecord/taxrecord.json', 'r', encoding = 'utf-8') as f:
				lines = f.readlines()
				last_line = json.loads(lines[-1].replace('\'', '\"'))
				for i in range(len(rows)):
					if last_line['company'].replace('（', '(').replace('）', ')') in rows[i].replace('（', '(').replace('）', ')'):
						if last_line['status'] == 'finish':
							rows = rows[i+1:]
							break
						else:
							rows = rows[i:]
							break
		except Exception as e:
			print(e)

		for i in rows:
			if re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i) is not None:
				s = re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i).group(0).strip()	
				s = s.replace('(', '（')
				s = s.replace(')', '）')	
				new_rows.append(s)
		return new_rows	

	def record_progress(self, company, status):
		with open('progressRecord/taxrecord.json', 'a+', encoding = 'utf-8') as f:
			info = str({"company" : company, "status" : status})+'\n'
			f.write(info)

	def searchCompany(self, searchword, times = 0):
		proxy = self.proxies
		gevent.sleep(random.random())
		print('!!!%s start_spider!!!' %(searchword))
		try:
			self.sess.get('http://hd.chinatax.gov.cn/xxk/#', headers = self.headers, proxies = proxy)
			url = 'http://hd.chinatax.gov.cn/xxk/action/ListXxk.do'
			formdata = {
						'categeryid': '24',
						'querystring24' : 'articlefield02',
						'querystring25' : 'articlefield02',
						'queryvalue' : searchword
						}
			gevent.sleep(random.random() * 2)
			response = self.sess.post(url, headers = self.headers, data = formdata, proxies = proxy)
			if response.status_code == 200:
				html = etree.HTML(response.text)
				hrefs = html.xpath('.//a/@href')
				response2 = self.sess.get('http://hd.chinatax.gov.cn/xxk/action/'+hrefs[0], headers = self.headers, proxies = proxy)
				gevent.sleep(random.random() * 2)
				self.parseData(searchword, response2.text)
			else:
				print('%s 搜索错误 %d' %(searchword, response.status_code))
				if times < 5:
					times = times + 1
					self.headers['User-Agent'] = random.choice(user_agent)
					# if self.num == 0:
					# 	self.checkout_IP()
					# 	self.num+=1
					# 	time.sleep(10)
					# else:
					# 	if proxy['http'] == self.proxies['http']:
					# 		self.checkout_IP()
					self.searchCompany(searchword, times)
				else:
					self.record_progress(searchword, 'error')
		except Exception as e:
			print(e)
			# self.start_spider()


	def parseData(self, company, html):
		'''
			数据处理
		'''
		header = ['纳税人名称', '纳税人识别号', '组织机构代码', '注册地址', '法定代表人或者负责人姓名、性别、证件名称及号码', '负有直接责任的财务负责人姓名、性别、证件名称及号码', '负有直接责任的中介机构信息及其从业人员信息',
					 '案件性质', '主要违法事实', '相关法律依据及税务处理处罚情况']
		result = etree.HTML(html)		
		taxName = result.xpath('/html/body/table/tr/td/table/tr[1]/td[2]/text()')
		taxNum = result.xpath('/html/body/table/tr/td/table/tr[2]/td[2]/text()')
		organizationCode = result.xpath('/html/body/table/tr/td/table/tr[3]/td[2]/text()')
		regAddress = result.xpath('/html/body/table/tr/td/table/tr[4]/td[2]/text()')
		legalPerson = result.xpath('/html/body/table/tr/td/table/tr[5]/td[2]/text()')
		officer = result.xpath('/html/body/table/tr/td/table/tr[6]/td[2]/text()')
		agencyInfo = result.xpath('/html/body/table/tr/td/table/tr[7]/td[2]/text()')
		caseNature = result.xpath('/html/body/table/tr/td/table/tr[8]/td[2]/text()')
		fact_punish = result.xpath('/html/body/table/tr/td/table/tr[9]/td[2]/text()')
		# punish = result.xpath('/html/body/table/tr/td/table/tr[9]/td[2]/text()')[1]

		data = (
				company,
				taxName[0] if len(taxName) > 0 else '', 
				taxNum[0] if len(taxNum) > 0 else '', 
				organizationCode[0] if len(organizationCode) > 0 else '', 
				regAddress[0] if len(regAddress) > 0 else '', 
				legalPerson[0] if len(legalPerson) > 0 else '', 
				officer[0] if len(officer) > 0 else '', 
				agencyInfo[0] if len(agencyInfo) > 0 else '', 
				caseNature[0] if len(caseNature) > 0 else '', 
				fact_punish[0] if  len(caseNature) > 0 else '',
				fact_punish[1] if  len(caseNature) > 0 else '',
			)

		try:
			flag = 0
			with open('taxFiles/tax.csv', 'r',  encoding = 'utf_8_sig') as f:
				readers = csv.reader(f)
				for row in readers:
					if row != None:
						flag = 1
						break
		except Exception as e:
			print('读取csv---%s' %e)

		if os.path.exists('taxFiles') is False:
			os.mkdir('taxFiles')

		with open('taxFiles/tax.csv', 'a+', encoding = 'utf_8_sig', newline = '') as f:
			f_csv = csv.writer(f)
			if flag == 0:
				f_csv.writerow(header)
			f_csv.writerow(data)
			print('****%s finish...****' %(company))
			self.record_progress(company, 'finish')

	def checkout_IP(self):
		# url = 'http://47.106.170.4:8081/Index-generate_api_url.html?packid=1&fa=0&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
		# response = requests.get(url, headers = self.headers)
		# print(response.text)
		# json_data = json.loads(response.text)['data']

		# json_ip = json_data[0]
		# ip = json_ip['IP']
		# port = json_ip['Port']
		# http = str(ip)+':'+str(port)
		# https = str(ip)+':'+str(port)
		ip = '183.129.207.74:12580'
		self.proxies['http'] = ip
		self.proxies['https'] = ip
		print(self.proxies)


	def start_spider(self):
		self.checkout_IP()
		rows = self.getDataFromEx()
		p = Pool(10)
		self.threads = [p.spawn(self.searchCompany, row) for row in rows]
		gevent.joinall(threads)

		print('finish')


if __name__ == '__main__':

	tax = tax()
	tax.start_spider()
	# tax.getData('2018年2月')