# -*- coding:utf-8 -*-
import requests
import json
import csv




class createChina(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}

	def getEncryStr(self, company):
		url = 'https://www.creditchina.gov.cn/api/credit_info_search?keyword=%s&templateId=&page=1&pageSize=10' %(company)
		response = requests.get(url, headers = self.headers)
		jsonData = json.loads(response.text)['data']['results']
		finalData = {}
		for i in jsonData:
			if i['name'] == company:
				finalData = i
		return finalData['encryStr'], finalData['dishonestyCount']

	def getCompanyData(self, encryStr):
		url = 'https://www.creditchina.gov.cn/api/credit_info_detail?encryStr=%s' %(encryStr)
		response = requests.get(url, headers = self.headers)
		jsonData = json.loads(response.text)['result']
		business = (jsonData['entName'], jsonData['creditCode'], jsonData['dom'], jsonData['regno'], jsonData['legalPerson'], jsonData['esdate'], jsonData['enttype'], jsonData['regorg'])
		return business


	def getDishonestForm(self, company, pageNum):
		encryStr, count = self.getEncryStr(company)
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
		r = (data['数据来源'], data['案号'], data['失信被执行人名称'], data['企业法人姓名'], data['执行法院'], data['地域名称'], data['执行依据文号'], data['作出执行依据单位'], data['法律生效文书确定的义务'],
		 data['被执行人的履行情况'], data['失信被执行人具体情形'], data['发布时间'], data['立案时间'], data['已履行部分'], data['未履行部分'], data['最新更新日期'])
		return r

	def saveData(self, data, businessData):
		bussinessInfo = ['公司名', '统一社会信用代码', '地址', '工商注册号', '法人信息', '成立日期', '企业类型', '登记机关']

		headers = ['数据来源', '案号', '失信被执行人名称', '企业法人姓名', '执行法院', '地域名称', '执行依据文号', '作出执行依据单位', '法律生效文书确定的义务',
				'被执行人的履行情况', '失信被执行人具体情形', '发布时间', '立案时间', '已履行部分', '未履行部分', '最新更新日期']

		with open('createChain.csv', 'w') as f:
			f_csv = csv.writer(f)
			f_csv.writerow(bussinessInfo)
			f_csv.writerow(businessData)

			f_csv.writerow(headers)
			f_csv.writerows(data)
		print('数据存储完成')


if __name__ == '__main__':
	createChina = createChina()
	createChina.getDishonestForm('哈尔滨泰富电气有限公司', 1)