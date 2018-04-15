# -*- coding:utf-8 -*-
import requests
import json
import time
import re
import csv




class shixin(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}


	def getData(self):
		nowTime = str(int(time.time() * 1000))
		query = '失信被执行人名单'
		name = '哈尔滨泰富电气有限公司'
		url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?resource_id=6899&query=%s&cardNum=&iname=%s&areaName=&ie=utf-8&oe=utf-8&format=json&t=%s&cb=jQuery1102019160163910639327_1523667010450&_=1523667010456' %(query, name, nowTime)
		response = requests.get(url = url, headers = self.headers)
		jsonData = re.search('\((.*)\)', response.text)
		datas = json.loads(jsonData.group(1))['data'][0]['result']

		rows = []
		for data in datas:
			rows.append((data['iname'], data['cardNum'], data['businessEntity'], data['courtName'], data['areaName'], data['gistId'],
				data['regDate'], data['caseCode'], data['gistUnit'], data['duty'], data['performance'], data['disruptTypeName'], data['publishDate']))
		self.saveData(rows)
	


	def saveData(self, datas):
		headers = ['被执行人姓名/名称', '身份证号码/组织机构代码', '法定代表人或负责人姓名', '执行法院', '省份', '执行依据文号',
					'立案时间', '案号', '做出执行依据单位', '生效法律文书确定的义务', '被执行人的履行情况', '失信被执行人行为具体情形',
					'发布时间']
		
		try:
			with open('shixin.csv', 'w') as f:
				f_csv = csv.writer(f)
				f_csv.writerow(headers)
				f_csv.writerows(datas)
		except Exception as e:
			print('Error')



if __name__ == '__main__':
	s = shixin()
	s.getData()


