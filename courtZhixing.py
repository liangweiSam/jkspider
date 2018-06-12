#-*- coding:utf-8 -*-
from lxml import etree
from ProxyPool import ProxyPool
from gevent import monkey,pool; monkey.patch_socket()
from lianzhong_api import main
from lianzhong_api import checkPoint
from lianzhong_api import reportError

import gevent
import requests
import random
import os
import time
import threading
import re
'''	
	目标网站：中华人民共和国被执行人信息查询
	author： sam
	date：2018/5/7
'''
class courtZhixing(object):

	def __init__(self):
		self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}
		self.proxies = {
						'http' : ''
						}				
		self.session = requests.Session()
		self.baned_Ip = set()

	def getCaptcha(self, captchaId):
		print('正在下载验证码。。。')
		# http://zhixing.court.gov.cn/search/captcha.do?captchaId=319fddf656474ffe88af7177066540b0&random=0.07751778279595545
		# captchaId = '319fddf656474ffe88af7177066540b0'
		rd = random.random()
		url = 'http://zhixing.court.gov.cn/search/captcha.do?captchaId=%s&random=%s' %(captchaId, rd)
		if os.path.exists('courtZhixingCaptcha') is False:
			os.mkdir('courtZhixingCaptcha')

		captcha_name = 'captcha_%s.png' %(time.time())
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxies, timeout = 3)
			if 'image/jpeg' in response.headers['Content-Type']:
				with open('C:/Users/Administrator/Desktop/python/jkspider/courtZhixingCaptcha/'+captcha_name, 'wb') as file:
					file.write(response.content)
				print('下载完成... ')
			else:
				return
		except Exception as e:
			print('发生错误！！%s' %e)
		
		val, valId = main('wangang3', 'xieyueying.001', 'courtZhixingCaptcha/'+captcha_name, '', '4', '1001', '')
		return val, valId
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
			
		
					
	def firstVisit(self):
		url = 'http://zhixing.court.gov.cn/search/index_form.do'
		response = self.session.get(url, headers = self.headers)
		html = etree.HTML(response.text)
		captchaId = html.xpath('.//input[@id="captchaId"]/@value')
		# self.getCaptcha(captchaId, response.headers['Set-Cookie'])
		return captchaId

	def search(self, pname):
		captchaId = self.firstVisit()
		val, valId = self.getCaptcha(captchaId)

		'''
			初始查询..
		'''
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
		response = self.session.post(url, headers = self.headers, data = data)
		HTML = etree.HTML(response.text)
		error_result = HTML.xpath('.//title/text()')[0]
		pageNum = ''
		ids = ''
		totalPage = ''
		if '验证码出现错误' in error_result:
			print(response.text)
			reportError('wangang3', 'xieyueying.001', valId)
		else:
			pageNum = HTML.xpath('.//div[@align="right"]/text()')[4] # 页 1/2 共16条
			ids = HTML.xpath('.//a[@class="View"]/@id')
			totalPage = re.search(r'1/(\d{1,4})', pageNum).group(1)
			 # range 左闭右开 [start, end）
			'''
				查询所有页数..
			'''
			for i in range(1, int(totalPage)+1):
				if i == 1:
					continue
				data['currentPage'] = '%s' %(i)
				response = self.session.post(url, headers = self.headers, data = data)
				HTML = etree.HTML(response.text)
				ids = ids+HTML.xpath('.//a[@class="View"]/@id')
			return ids, val, captchaId
		
	

	def parserDetailData(self, Ids, j_captcha, captchaId):
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
		for Id in Ids:
			timeS = time.time() * 1000
			detail_Url = 'http://zhixing.court.gov.cn/search/newdetail?id=%s&j_captcha=%s&captchaId=%s&_=%s' %(Id, j_captcha, captchaId, timeS)
			detail_Data = self.session.get(detail_Url, headers = self.headers).json()
			
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






if __name__ == '__main__':
	cz = courtZhixing()
	ids, val, captchaId = cz.search('哈尔滨泰富电气有限公司')
	cz.parserDetailData(ids, val, captchaId)
	# cz.threadGetCaptcha()





