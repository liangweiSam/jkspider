# -*- coding:utf-8 -*-
from gevent import monkey,pool; monkey.patch_socket()
from ProxyPool import ProxyPool

import requests
import json
import csv
import gevent
import xlrd, xlwt
import re
import os
import user_agent_Pool
import random
import time
'''	
	目标网站：信用中国
	author： sam
	date：2018/5/7

'''



class createChina(object):

	def __init__(self):

		self.user_agent = random.choice(user_agent_Pool.user_agent)
		self.headers  = {'User-Agent' : self.user_agent,
						'Connection' : 'keep-alive',
						}		

	def checkout_UA(self):
		self.user_agent = random.choice(user_agent_Pool.user_agent)	

	def checkout_IP(self):
		# p = ProxyPool()
		# init_ip = p.get_IP('http')
		# ip = init_ip['ip'] + ':' + str(init_ip['port'])
		# return {'http' :  "http://" + ip,'https' :  "https://" + ip}
		return {'http' : '', 'https': ''}		

	def is_json(self, text):
		'''
			Is the text json? 
			return True or False
		'''
		if isinstance(text, str):
			try:
				json.loads(text)
			except Exception as e:
				return False
			return True
		else:
			return False
	
	def record_progress(self, company, status):
		with open('progressRecord/record.json', 'a+', encoding = 'utf-8') as f:
			info = str({"company" : company, "status" : status})+'\n'
			f.write(info)

	def getEncryStr(self, company):
		self.checkout_UA()
		proxy = self.checkout_IP()
		# self.checkout_IP()
		url = 'https://www.creditchina.gov.cn/api/credit_info_search?keyword=%s&templateId=&page=1&pageSize=10' %(company)
		response = requests.get(url, headers = self.headers, proxies = proxy, timeout = 15)
		try:
			if self.is_json(response.text):
				jsonData = json.loads(response.text)['data']['results']
				finalData = {}
				if len(jsonData) > 0:
					for i in jsonData:
						if i['name'] == company.replace('（', '(').replace('）', ')'):
							finalData = i
					return finalData['encryStr'], finalData['dishonestyCount'], proxy #失信数
				else:
					return False, 1, proxy
			else:
				print('非JSON')
				return False, 1, proxy
		except Exception as e:
			return False, 1, proxy

	def get_penalty(self, company, timef=0, times=0, timet=0):
		'''
			行政处罚
		'''
		time.sleep(random.randint(1, 3))
		proxy = self.checkout_IP()
		self.checkout_UA()
		try:
			url = 'https://www.creditchina.gov.cn/api/pub_penalty_name?name=%s&page=1&pageSize=10' %(company)
			response = requests.get(url, headers = self.headers, proxies = proxy, timeout = 15)
			if self.is_json(response.text):
				jsonData = json.loads(response.text)
				if len(jsonData) > 0:
					print(jsonData)
					jsonData = jsonData['result']
					total_page = jsonData['totalPageCount']
					results = jsonData['results']
					datas = []
					for i in results:
							# 公司名称  处罚名称	  决定文书号  法人代表人姓名	处罚类别	 处罚结果	处罚事由   处罚依据    处罚机关   处罚决定日期     数据更新时间   处罚期限 
						r = (company, i['cfCfmc'], i['cfWsh'], i['cfFr'], i['cfCflb1'], i['cfJg'], i['cfSy'], i['cfYj'], i['cfXzjg'], i['cfJdrq'],i['cfSjc'], i['cfQx'])
						datas.append(r)
					for x in range(1, total_page):
						x = x+1	
						urls = 'https://www.creditchina.gov.cn/api/pub_penalty_name?name=%s&page=%d&pageSize=10' %(company, x)
						response2 = requests.get(urls, headers = self.headers, proxies = proxy, timeout = 15)
						jsonData = json.loads(response2.text)['result']
						results2 = jsonData['results']
						for a in results2:
							r = (company, a['cfCfmc'], a['cfWsh'], a['cfFr'], a['cfCflb1'], a['cfJg'], a['cfSy'], a['cfYj'], a['cfXzjg'], a['cfJdrq'],a['cfSjc'], a['cfQx'])
							datas.append(r)
					if len(datas) == 0:
						r = (company, '', '', '', '', '', '', '', '', '', '', '')
						datas.append(r)
					self.record_progress(company, 'finish')
					return datas
				else:
					# return [(company, '无信息')]
					if timef < 10:
						timef = timef+1
						return self.get_penalty(company, timef=timef)
					else:
						self.record_progress(company, 'error')
						return [(company, '无信息')]
			else:
				# return [(company, '非json')]
				if times < 10:
					times = times+1
					return self.get_penalty(company)
				else:
					self.record_progress(company, 'error')
					return [(company, '非json')]
		except Exception as e:
			# return [(company, 'Error')]
			if timet < 10:
				timet = timet+1
				return self.get_penalty(company)
			else:
				self.record_progress(company, 'error')
				print('行政处罚 : %s' %(e))
				return [(company, 'Error')]
					
	def save_plenalty(self, company):
		'''
			获取行政处罚数据
		'''
		company = company.replace('（', '(').replace('）', ')')						
		print('%s_行政处罚' %(company))
		flag2 = 0
		datas = self.get_penalty(company)
		if datas is not None:
			headers = ['公司名称', '处罚名称', '决定文书号', '法人代表人姓名', '处罚类别', '处罚结果', '处罚事由', '处罚依据', '处罚机关', '处罚决定日期',
					'数据更新时间', '处罚期限']
		if os.path.exists('createChina/penalty.csv'):
			with open('createChina/penalty.csv', 'r') as f:
				readers = csv.reader(f)
				for row in readers:
					if row != None:
						flag2 = 1
					break			

		with open('createChina/penalty.csv', 'a+') as f:
			f_csv = csv.writer(f)
			if flag2 == 0:
				f_csv.writerow(headers)
			f_csv.writerows(datas)

	def getCompanyData(self, encryStr):
		'''
			公司信息
		'''
		url = 'https://www.creditchina.gov.cn/api/credit_info_detail?encryStr=%s' %(encryStr)
		response = requests.get(url, headers = self.headers, proxies = self.proxy, timeout = 15)
		jsonData = json.loads(response.text)['result']
		business = (jsonData['entName'], jsonData['creditCode'], jsonData['dom'], jsonData['regno'], jsonData['legalPerson'], jsonData['esdate'], jsonData['enttype'], jsonData['regorg'])
		return business

	def getDishonestForm(self, company, pageNum):
		'''
			失信信息获取
		'''
		print('%s_失信信息' %(company))
		try:
			encryStr, count, proxy = self.getEncryStr(company)
			if encryStr is not False:
				datas = []
				while pageNum*10 <= int(count):
						url = 'https://www.creditchina.gov.cn/api/record_param?encryStr=%s&creditType=8&dataSource=0&pageNum=%d&pageSize=10' %(encryStr, pageNum)
						pageNum += 1
						response = requests.get(url, headers = self.headers, proxies = proxy, timeout = 15)
						jsonData = json.loads(response.text)
						for d in jsonData['result']:
							data = self.parseData(d)
							datas.append(data)
				# businessData = self.getCompanyData(encryStr)
				print('数据清洗完成')	
				self.saveData(datas, 1)
			else:
				print('失信信息 : %s' %('Error'))
		except Exception as e:
			print('失信信息 : %s' %(e))	
			return 
	
	def parseData(self, data):
		'''
			处理数据
		'''
		r = (data['失信被执行人名称'], data['数据来源'], data['案号'], data['企业法人姓名'], data['执行法院'], data['地域名称'], data['执行依据文号'], data['作出执行依据单位'], data['法律生效文书确定的义务'],
		 data['被执行人的履行情况'], data['失信被执行人具体情形'], data['发布时间'], data['立案时间'], data['已履行部分'], data['未履行部分'], data['最新更新日期'])
		return r

	def saveData(self, data, businessData):
		'''
			存储失信被执行人
		'''
		flag1 = 0
		bussinessInfo = ['公司名', '统一社会信用代码', '地址', '工商注册号', '法人信息', '成立日期', '企业类型', '登记机关']
		headers = ['失信被执行人名称', '数据来源', '案号', '企业法人姓名', '执行法院', '地域名称', '执行依据文号', '作出执行依据单位', '法律生效文书确定的义务',
				'被执行人的履行情况', '失信被执行人具体情形', '发布时间', '立案时间', '已履行部分', '未履行部分', '最新更新日期']
		if os.path.exists('createChina/dishonest.csv'):
			with open('createChina/dishonest.csv', 'r') as f:
				readers = csv.reader(f)
				for row in readers:
					if row != None:
						flag1 = 1
					break

		with open('createChina/dishonest.csv', 'a+') as f:
			f_csv = csv.writer(f)
			# f_csv.writerow(bussinessInfo)
			# f_csv.writerow(businessData)
			if flag1 == 0:
				f_csv.writerow(headers)
			f_csv.writerows(data)
		print('数据存储完成')

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
		with open('progressRecord/record.json', 'r', encoding = 'utf-8') as f:
			lines = f.readlines()
			# for line in lines:
				# if 'finish' not in line:
				# 	last_line = json.loads(line.replace('\'', '\"'))
			last_line = json.loads(lines[-1].replace('\'', '\"'))
			for i in range(len(rows)):
				if last_line['company'].replace('（', '(').replace('）', ')') in rows[i].replace('（', '(').replace('）', ')'):
					if last_line['status'] == 'finish':
						rows = rows[i+1:]
						break
					else:
						rows = rows[i:]
						break

		# rows = rows[1765:]
		for i in rows:
			if re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i) is not None:
				s = re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i).group(0).strip()	
				s = s.replace('(', '（')
				s = s.replace(')', '）')	
				new_rows.append(s)
		return new_rows	

	def startSpider(self):
		rows = self.getDataFromEx()
		p = pool.Pool(8)
		threads = [p.spawn(self.save_plenalty(company)) for company in rows]
		# threads2 = [p.spawn(self.getDishonestForm(company, 1)) for company in rows]
		gevent.joinall(threads)

	def test(self):
		r = requests.get("https://ip.cn", headers=self.headers, proxies=self.proxy)
		print(r.status_code)
		print(r.text)
		if r.status_code == 302 or r.status_code == 301 :
		    loc = r.headers['Location']
		    url_f = "https://ip.cn" + loc
		    print(loc)
		    r = requests.get(url_f, headers=self.headers, proxies=self.proxy)
		    print(r.status_code)
		    print(r.text)

if __name__ == '__main__':
	createChina = createChina()
	# createChina.record_progress("厦顺控股有限公司", "finish")
	createChina.startSpider()
	# createChina.getDishonestForm('哈尔滨泰富电', 1)
	# createChina.save_plenalty('厦顺控股有限公司')
	# createChina.test()