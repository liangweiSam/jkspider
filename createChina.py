# -*- coding:utf-8 -*-
from gevent import monkey,pool; monkey.patch_socket()

import requests
import json
import csv
import gevent
import xlrd, xlwt
import re


'''	
	目标网站：信用中国
	author： sam
	date：2018/5/7

'''
class createChina(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}
		self.flag1 = 0
		self.flag2 = 0

	def getEncryStr(self, company):
		url = 'https://www.creditchina.gov.cn/api/credit_info_search?keyword=%s&templateId=&page=1&pageSize=10' %(company)
		response = requests.get(url, headers = self.headers)
		jsonData = json.loads(response.text)['data']['results']
		finalData = {}
		if len(jsonData) > 0:
			for i in jsonData:
				if i['name'] == company:
					finalData = i                  
			return finalData['encryStr'], finalData['dishonestyCount'] #失信数
		else:
			return False, 1

	def get_penalty(self, company):
		'''
			行政处罚
		'''
		try:
			url = 'https://www.creditchina.gov.cn/api/pub_penalty_name?name=%s&page=1&pageSize=10' %(company)
			response = requests.get(url, headers = self.headers)
			print(response.text)
			jsonData = json.loads(response.text)['result']
			total_page = jsonData['totalPageCount']
			results = jsonData['results']
			datas = []
			for i in results:
					# 处罚名称	  决定文书号  法人代表人姓名	处罚类别	 处罚结果	处罚事由   处罚依据    处罚机关   处罚决定日期     数据更新时间   处罚期限 
				r = (i['cfCfmc'], i['cfWsh'], i['cfFr'], i['cfCflb1'], i['cfJg'], i['cfSy'], i['cfYj'], i['cfXzjg'], i['cfJdrq'],i['cfSjc'], i['cfQx'])
				datas.append(r)
			for x in range(1, total_page):
				x = x+1	
				urls = 'https://www.creditchina.gov.cn/api/pub_penalty_name?name=%s&page=%d&pageSize=10' %(company, x)
				response2 = requests.get(urls, headers = self.headers)
				jsonData = json.loads(response2.text)['result']
				results2 = jsonData['results']
				for a in results2:
					r = (a['cfCfmc'], a['cfWsh'], a['cfFr'], a['cfCflb1'], a['cfJg'], a['cfSy'], a['cfYj'], a['cfXzjg'], a['cfJdrq'],a['cfSjc'], a['cfQx'])
					datas.append(r)
			return datas
		except Exception as e:
			print(e)
			return None

	def save_plenalty(self, company):
		print('%s_行政处罚' %(company))
		datas = self.get_penalty(company)
		if datas is not None:
			headers = ['处罚名称', '决定文书号', '法人代表人姓名', '处罚类别', '处罚结果', '处罚事由', '处罚依据', '处罚机关', '处罚决定日期',
					'数据更新时间', '处罚期限']

			with open('createChina/penalty.csv', 'a+') as f:
				f_csv = csv.writer(f)
				if self.flag2 == 0:
					f_csv.writerow(headers)
					self.flag2 = 1
				f_csv.writerows(datas)
			print('数据存储完成')	

	def getCompanyData(self, encryStr):
		'''
			公司信息
		'''
		url = 'https://www.creditchina.gov.cn/api/credit_info_detail?encryStr=%s' %(encryStr)
		response = requests.get(url, headers = self.headers)
		jsonData = json.loads(response.text)['result']
		business = (jsonData['entName'], jsonData['creditCode'], jsonData['dom'], jsonData['regno'], jsonData['legalPerson'], jsonData['esdate'], jsonData['enttype'], jsonData['regorg'])
		return business

	def getDishonestForm(self, company, pageNum):
		'''
			失信信息获取
		'''
		print('%s_失信信息' %(company))
		encryStr, count = self.getEncryStr(company)
		if encryStr is not False:
			datas = []
			while pageNum*10 <= int(count):
					url = 'https://www.creditchina.gov.cn/api/record_param?encryStr=%s&creditType=8&dataSource=0&pageNum=%d&pageSize=10' %(encryStr, pageNum)
					pageNum += 1
					response = requests.get(url, headers = self.headers)
					jsonData = json.loads(response.text)
					for d in jsonData['result']:
						data = self.parseData(d)
						datas.append(data)
			businessData = self.getCompanyData(encryStr)
			print('数据清洗完成')	
			self.saveData(datas, businessData)


	def parseData(self, data):
		r = (data['失信被执行人名称'], data['数据来源'], data['案号'], data['企业法人姓名'], data['执行法院'], data['地域名称'], data['执行依据文号'], data['作出执行依据单位'], data['法律生效文书确定的义务'],
		 data['被执行人的履行情况'], data['失信被执行人具体情形'], data['发布时间'], data['立案时间'], data['已履行部分'], data['未履行部分'], data['最新更新日期'])
		return r

	def saveData(self, data, businessData):
		bussinessInfo = ['公司名', '统一社会信用代码', '地址', '工商注册号', '法人信息', '成立日期', '企业类型', '登记机关']

		headers = ['失信被执行人名称', '数据来源', '案号', '企业法人姓名', '执行法院', '地域名称', '执行依据文号', '作出执行依据单位', '法律生效文书确定的义务',
				'被执行人的履行情况', '失信被执行人具体情形', '发布时间', '立案时间', '已履行部分', '未履行部分', '最新更新日期']

		with open('createChina/dishonest.csv', 'a+') as f:
			f_csv = csv.writer(f)
			# f_csv.writerow(bussinessInfo)
			# f_csv.writerow(businessData)
			if self.flag1 == 0:
				f_csv.writerow(headers)
				self.flag1 = 1
			f_csv.writerows(data)
		print('数据存储完成')

	def getDataFromEx(self):
		workBook = xlrd.open_workbook(r'SpiderFiles/所有报告单new.xls')
		sheet1_name = workBook.sheet_names()[0]
		sheet1 = workBook.sheet_by_name(sheet1_name)
		rows = sheet1.col_values(0)[1:]
		new_rows = []
		for i in rows:
			if re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i) is not None:
				s = re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i).group(0).strip()	
				s = s.replace('(', '（')
				s = s.replace(')', '）')	
				new_rows.append(s)
		return new_rows	

	def startSpider(self):
		rows = self.getDataFromEx()
		p = pool.Pool(10)
		threads = [p.spawn(self.save_plenalty(company)) for company in rows]
		threads2 = [p.spawn(self.getDishonestForm(company, 1)) for company in rows]
		gevent.joinall(threads+threads2)

if __name__ == '__main__':
	createChina = createChina()
	createChina.startSpider()
	# createChina.getDishonestForm('柏斯音乐集团', 1)
	# createChina.save_plenalty('厦顺控股有限公司')