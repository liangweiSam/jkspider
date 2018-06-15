#-*- coding:utf-8 -*-
from lxml import etree
from ProxyPool import ProxyPool
from gevent import monkey,pool; monkey.patch_socket()
from gevent.queue import Queue
from lianzhong_api import main
from lianzhong_api import checkPoint
from lianzhong_api import reportError
from user_agent_Pool import user_agent

import gevent
import requests
import random
import os
import time
import threading
import re
import csv
import os
import xlrd, xlwt
import json
'''	
	目标网站：中华人民共和国被执行人信息查询
	author： sam
	date：2018/5/7
'''
class courtZhixing(object):

	def __init__(self):
		ua = random.choice(user_agent)
		self.headers = {'User-Agent' :  ua,
						'Connection' : 'keep-alive',
						'Referer'	: 'http://zxgk.court.gov.cn/'
						}
		self.proxies = {
						'http' : '',
						'https' : '',
						}				
		self.session = requests.Session()
		self.task = Queue()
		self.mark = False
		self.baned_Ip = set()

	def checkout_IP(self):
		# url = 'http://www.ueuz.com/index.php/home/Api/getips?select_package_id=2&num=1&dataType=2&areaname=&pro=&city=&manyregions=&ishow=2&port=4&client=1&time_whenlong=201&secret=rnd5rrKno6x9paaqgXaq4LHMiLCuq6bahX2Arg&callback=%s&tshow=2&cshow=2&break=2&csb=&remove=3' %(str(time.time())[:10])
		
		# url = 'http://47.106.170.4:8081/Index-generate_api_url.html?packid=1&fa=0&qty=1&port=1&format=json&ss=5&css=&ipport=1&pro=&city='
		# url = 'http://webapi.http.zhimacangku.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&pack=22232&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
		url = 'http://d.jghttp.golangapi.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&pack=318&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=0&regions='
		response = requests.get(url, headers = self.headers)
		json_data = json.loads(response.text)['data']

		json_ip = json_data[0]
		ip = json_ip['ip']
		# port = json_ip['ip_port']
		port = json_ip['port']

		# ip = json_ip['IP']
		# port = json_ip['Port']
		http = str(ip)+':'+str(port)
		https = str(ip)+':'+str(port)
		# ip = '183.129.207.74:12580'
		self.proxies['http'] = http
		self.proxies['https'] = https
		for i in range(5):
			self.task.put('checkouted')
		self.mark = False
		print(self.proxies)

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
			with open('progressRecord/courtZhixing.json', 'r', encoding = 'utf-8') as f:
				lines = f.readlines()
				last_line = json.loads(lines[-1].replace('\'', '\"'))
				for i in range(len(rows)):
					if last_line['company'].replace('(', '（').replace(')', '）') in rows[i].replace('(', '（').replace(')', '）'):
						
						if last_line['status'] == 'finish':
							rows = rows[i+1:]
							break
						else:
							rows = rows[i:]
							break
		except Exception as e:
			print(e)

		for i in rows:
			if re.search('.+(公司.+分公司|厂|加油站|店|集团|所|中心|院|公司)', i) is not None:
				s = re.search('.+(公司.+分公司|公司|厂|加油站|店|集团|所|中心|院)', i).group(0).strip()	
				if '变更后' in s:
					s = s.split('变更后')[1].strip()
				if '变更前' in s:
					s = s.split('变更前')[0].strip()

				s = s.replace('(', '（')
				s = s.replace(')', '）')	
				new_rows.append(s.strip())
				new_rows = list(set(new_rows))
		return new_rows

	def record_progress(self, company, status):
		with open(r'progressRecord/courtZhixing.json', 'a+', encoding = 'utf-8') as f:
			info = str({"company" : company, "status" : status})+'\n'
			f.write(info)	

	def checkPoiont(self):
		url = 'http://aiapi.c2567.com/api/info?username=wangang3&password=xieyueying1'
		try:
			response = requests.get(url, headers = self.headers).json()
			score = response['score']
			return score
		except Exception as e:
			print('检查剩余分数' %e)
			raise e

	def jizhiPlatform(self, img):
		point = self.checkPoiont()
		if point > 0:
			url = 'http://aiapi.c2567.com/api/create'
			formdata = {
						'username' : 'wangang3',
						'password' : 'xieyueying1',
						'typeid' : '3000',
						'timeout' : '60',
						}
			f = open(img, 'rb')
			im = f.read()
			files = {'image' : ('a.jpg', im)}
			response = requests.post(url, headers = self.headers, files=files, data = formdata)
			print(response.text)
			if response.text == 'Internal Server Error':
				print(response.status_code)
				print(files)

			jsondata = json.loads(response.text)
			valId = jsondata['data']['id']
			val = jsondata['data']['result']
			return val, valId
		else:
			assert False, print('点数不足..')

	def reportError(self, valId):
		url = '	http://aiapi.c2567.com/api/reporterror?username=wangang3&password=xieyueying1&id=%s' %(valId)
		response = requests.get(url, headers = self.headers).json()
		print('极智识别：返回结果: %s' %(str(response['data']['result'])))

	def getCaptcha(self, captchaId, session):
		# http://zhixing.court.gov.cn/search/captcha.do?captchaId=319fddf656474ffe88af7177066540b0&random=0.07751778279595545
		# captchaId = '319fddf656474ffe88af7177066540b0'
		rd = random.random()
		url = 'http://zhixing.court.gov.cn/search/captcha.do?captchaId=%s&random=%s' %(captchaId, rd)
		if os.path.exists('courtZhixingCaptcha') is False:
			os.mkdir('courtZhixingCaptcha')

		
		try:
			# response = self.session.get(url, headers = self.headers, proxies = self.proxies, timeout = 10)
			captcha_name = 'captcha_%s.png' %(time.time()*1000)
			response = session.get(url, headers = self.headers, proxies = self.proxies, timeout = 10)
			if 'image/jpeg' in response.headers['Content-Type']:
				with open('C:/Users/Administrator/Desktop/python/jkspider/courtZhixingCaptcha/'+captcha_name, 'wb') as file:
					file.write(response.content)
				print('验证码下载完成... ')
			else:
				return
		except Exception as e:
			print('验证码获取发生错误！！%s' %e)
		
		try:
			# val, valId = main('wangang3', 'xieyueying.001', 'courtZhixingCaptcha/'+captcha_name, '', '4', '1001', '')
			val, valId = self.jizhiPlatform('courtZhixingCaptcha/'+captcha_name)
			os.rename('courtZhixingCaptcha/'+captcha_name, 'courtZhixingCaptcha/%s%d.png' %(val, time.time()*1000))
			return val, valId
		except Exception as e:
			print('极智验证:%s' %(e))
			return 0, 0
		# return 0, 0

		# j_captcha = input('请输入验证码：')
		# return j_captcha, '1'

	def reset_Ip(self):
		ippool = ProxyPool()
		collection = ippool.get_IP('http')
		ip = collection['ip'] + ':' + collection['port']
		return ip

	def threadGetCaptcha(self):
		i = 0
		status = 0
		while(i < 1000):
			try:
				gevent.joinall([
				gevent.spawn(self.getCaptcha),
				gevent.spawn(self.getCaptcha),
				gevent.spawn(self.getCaptcha),
				])
				if (i % 10 == 0) and (i != 0):
					print('[Must]重新设置IP中...')
					ip = self.reset_Ip()
					self.proxies['http'] = ip
					# if ip not in self.baned_Ip:
						# self.proxies['http'] = ip
						# self.baned_Ip.add(ip)
				i+=1
			except Exception as e:
				print(e)
				print('[Error]重新设置IP中...')
				ip = self.reset_Ip()
				if ip not in self.baned_Ip:
					self.proxies['http'] = ip
					self.baned_Ip.add(ip)
				pass
					
	def firstVisit(self, session):
		url = 'http://zhixing.court.gov.cn/search/index_form.do'
		# response = self.session.get(url, headers = self.headers, proxies = self.proxies)
		response = session.get(url, headers = self.headers, proxies = self.proxies)
		html = etree.HTML(response.text)
		captchaId = html.xpath('.//input[@id="captchaId"]/@value')
		# self.getCaptcha(captchaId, response.headers['Set-Cookie'])
		return captchaId

	def search(self, pname, times = 0):
		print('%s 开始采集' %(pname))
		gevent.sleep(random.random()*3)	
		# val = 0
		session = requests.Session()	
		try:
			captchaId = self.firstVisit(session)
			val, valId = self.getCaptcha(captchaId, session)
			'''
			初始查询..
			'''
			if val != 0:	
				url = 'http://zhixing.court.gov.cn/search/newsearch'
				data = {
						'searchCourtName': '全国法院（包含地方各级法院）',
						'selectCourtId': '1',
						'selectCourtArrange': '1',
						'pname': '%s' %(pname),
						'cardNum': '',
						'j_captcha': '%s' %(val),
						'captchaId': '%s' %(captchaId)
						}
				# post(url, headers, cookies) 需要另外设置一个参数.

				# response = self.session.post(url, headers = self.headers, data = data, proxies = self.proxies)
				response = session.post(url, headers = self.headers, data = data, proxies = self.proxies)
				HTML = etree.HTML(response.text)
				error_result = HTML.xpath('.//title/text()')[0]
				pageNum = ''
				ids = ''
				totalPage = ''
				if '验证码出现错误' in error_result:
					# print(response.text)
					print('验证码识别错误！！')
					self.reportError(valId)
					if times < 5:
						times+=1
						self.search(pname, times)
						time.sleep(3)
						return
				else:
					# pageNum = HTML.xpath('.//div[@align="right"]/text()')[4] # 页 1/2 共16条
					pageNum = ''
					for i in HTML.xpath('.//div[@align="right"]/text()'):
						if '共' in i:
							pageNum = i
							break
					# assert False, print(HTML.xpath('.//div[@align="right"]/text()'))
					ids = HTML.xpath('.//a[@class="View"]/@id')
					totalPage = re.search(r'1/(\d{1,4})', pageNum).group(1)
					 # range 左闭右开 [start, end）
					'''
						查询所有页数..
					'''
					if len(ids) > 0:
						for i in range(1, int(totalPage)+1):
							if i == 1:
								continue
							data['currentPage'] = '%s' %(i)
							gevent.sleep(random.random()*2)
							# response = self.session.post(url, headers = self.headers, data = data, proxies = self.proxies)
							response = session.post(url, headers = self.headers, data = data, proxies = self.proxies)
							HTML = etree.HTML(response.text)
							ids = ids+HTML.xpath('.//a[@class="View"]/@id')
						self.parserDetailData(ids, val, captchaId, pname, session)
					else:
						self.parserDetailData(ids, val, captchaId, pname, session)
			else:
				print('%s 采集失败' %(pname))
		except Exception as e:
			self.headers['User-Agent'] = random.choice(user_agent)
			if self.task.empty() is not True:
				flag = self.task.get()
				print('IP已更换！！')
				if flag == 'checkouted':
					self.mark == False
			else:
				self.mark = True

			if self.mark == True:
				self.checkout_IP()
				print('切换IP中...')
				time.sleep(5) 
			if times < 5:
				times+=1
				self.search(pname, times)
				print('主程序 %s' %e)
			else:
				raise e
		
	def parserDetailData(self, Ids, j_captcha, captchaId, company, session):
		'''
			jsonData:
			{
				caseCode:"(2018)陕01执812号" # 案号
				caseCreateTime:"2018年04月11日" # 立案时间
				caseState:"0" # 
				execCourtName:"西安市中级人民法院" # 执行法院
				execMoney:35893204 # 执行标的
				gistId:"（2017）西证执字第242号" #？？
				id:24229187 # ？？
				partyCardNum:"91230199744****927K" # 身份证号码/组织机构码
				pname:"哈尔滨泰富电气有限公司" # 被执行人姓名
			}
		'''
		if len(Ids) > 0:
			for Id in Ids:
				timeS = time.time() * 1000
				detail_Url = 'http://zhixing.court.gov.cn/search/newdetail?id=%s&j_captcha=%s&captchaId=%s&_=%s' %(Id, j_captcha, captchaId, timeS)
				# detail_Data = self.session.get(detail_Url, headers = self.headers, proxies = self.proxies).json()
				detail_Data = session.get(detail_Url, headers = self.headers, proxies = self.proxies).json()
				caseCode = detail_Data['caseCode']
				caseCreateTime = detail_Data['caseCreateTime']
				caseState = detail_Data['caseState']
				execCourtName = detail_Data['execCourtName']
				execMoney = detail_Data['execMoney']
				gistId = detail_Data['gistId']
				id_ = detail_Data['id']
				partyCardNum = detail_Data['partyCardNum']
				pname = detail_Data['pname']
				data = (pname, partyCardNum, caseCode, caseCreateTime, caseState, execCourtName, execMoney, gistId, id_)
				self.saveData(data)
		else:
			data = (company, '', '', '', '', '', '', '', '')
			self.saveData(data)

	def saveData(self, data):		
		if os.path.exists('courtZhixing') is not True:
			os.mkdir('courtZhixing')
		headers = ['被执行人姓名', '身份证号码/组织机构码', '案号', '立案时间', '案件状态', '执行法院', '执行标的', 'gistId', '_id']
		flag2 = 0
		try:
			with open('courtZhixing/zhixing.csv', 'r', encoding = 'utf_8_sig') as f:
				readers = csv.reader(f)
				for row in readers:
					if row != None:
						flag2 = 1
						break	
		except Exception as e:
			print('打开文件失败 %s..' %e)
			pass

		with open('courtZhixing/zhixing.csv', 'a+', encoding='utf_8_sig', newline = '') as f:
			f_csv = csv.writer(f)
			if flag2 == 0:
				f_csv.writerow(headers)
			print('%s 数据写入..' %(data[0]))
			f_csv.writerow(data)
			self.record_progress(data[0], 'finish')

	def startSpider(self):
		p = pool.Pool(5)
		rows = self.getDataFromEx()
		threads = [p.spawn(self.search, row) for row in rows]
		gevent.joinall(threads)


if __name__ == '__main__':
	cz = courtZhixing()
	# print(len(cz.getDataFromEx()))
	# for i in set(cz.getDataFromEx()):
	# 	for a in cz.getDataFromEx():
	# 		if i == a:
	# 			print(a)

	# print(len(set(cz.getDataFromEx())))
	# [print(i) for i in cz.getDataFromEx()]
	# cz.search('山一电子制品（东莞）有限公司')
	# print(cz.jizhiPlatform('courtZhixingCaptcha/captcha_1528881887.3512.png'))
	
	# cz.search('祐鼎（福建）光电材料有限公司')
	# ids, val, captchaId = cz.search('哈尔滨泰富电气有限公司')
	# cz.parserDetailData(ids, val, captchaId)
	# cz.threadGetCaptcha()





