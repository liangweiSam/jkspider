# -*- coding:utf-8
from lxml import etree
from pymongo import MongoClient
from gevent import monkey,pool; monkey.patch_socket()
from province import get_spell

import gevent
import time, datetime
import user_agent_Pool
import requests
import re
import execjs
import json
import random

useful_url = { 	
				# 双随机抽查结果信息 : getDrRaninsResUrl
				'getDrRaninsResUrl' : '',
				# 抽查检查结果信息 : spotCheckInfoUrl
				'spotCheckInfoUrl' : '',
				# 股东 : shareholderUrl
				'shareholderUrl' : '',
				# 清算信息 : liquidationUrl
				'liquidationUrl' : '',
				# 变更信息 : alterInfoUrl
				'alterInfoUrl' : '',
				# 分支信息 : branchUrl
				'branchUrl' : '',
				# 动产抵押登记 : proPledgeRegInfoUrl
				'proPledgeRegInfoUrl ' : '',
				# 商标注册 ： trademarkInfoUrl 
				'trademarkInfoUrl' : '',
				# 企业年报信息 : anCheYearInfo 
				'anCheYearInfo' : '',
				# 行政许可信息 : insLicenceInfoNull 
				'insLicenceInfoNull' : '',
				# 行政处罚信息 : insPunishmentinfoUrl
				'insPunishmentinfoUrl' : '', 
				# 知识产权出质登记信息 : insProPledgeRegInfoUrl 
				'insProPledgeRegInfoUrl' : '',
				# 简易注销信息 : simpleCancelUrl
				'simpleCancelUrl' : '',
				# 行政许可信息 ： otherLicenceDetailInfoUrl
				'otherLicenceDetailInfoUrl' : '',
				# 基本信息中的行政许可信息：insLicenceinfoUrl
				'insLicenceinfoUrl' : '',
				# 行政处罚信息 : punishmentDetailInfoUrl
				'punishmentDetailInfoUrl' : '',			
				# 列入经营异常名录信息 : entBusExcepUrl
				'entBusExcepUrl' : '',
				# 严重违法失信 : IllInfoUrl
				'IllInfoUrl' : '',
				# 主要人员 : keyPersonUrl
				'keyPersonUrl' : '',
				# 股权变更信息 ： insAlterstockinfoUrl
				'insAlterstockinfoUrl' : '',
				# 动产抵押登记信息 ： mortRegInfoUrl
				'mortRegInfoUrl' : '',
				# 司法协助信息 ： assistUrl
				'assistUrl' : '',
				# 股权变更信息 : insAlterstockinfoUrl
				'insAlterstockinfoUrl' : '',
				# 股东及出资信息 ： insInvinfoUrl
				'insInvinfoUrl' : '',
				# 全部商标信息 ： 用于获取不分页的信息
				'allTrademarkUrl' : '',
				}

mainContent_url = {
				'''
					不分页的信息 在商标注册信息内的网页，暂未找到入口
				'''
				# 全部变更信息   
				'allAlterInfoUrl' : '',
				# 全部股东及出资信息   
				'allShareHolderDetailInfoUrl' : '',
				# 全部行政处罚信息
				'allPunishmentInfoUrl' : '',
				# 全部行政许可信息
				'allOtherLicenceInfoUrl' : '',
				# 全部动产抵押信息
				'allMortRegInfoUrl' : '',
				# 全部股权出质登记信息
				'allStakQualitInfoUrl' : '',
				# 全部个体工商户
				'allGtAlterInfoUrl' : '',
				# 全部分支机构信息
				'branchUrl' : '',
				} 

useful_url_list = ['spotCheckInfoUrl', 'insInvinfoUrl', 'assistUrl', 'mortRegInfoUrl','insAlterstockinfoUrl','keyPersonUrl', 'IllInfoUrl', 'entBusExcepUrl', 'punishmentDetailInfoUrl',
					 'otherLicenceDetailInfoUrl', 'simpleCancelUrl', 'insProPledgeRegInfoUrl', 'insPunishmentinfoUrl', 'insLicenceInfoNull', 'anCheYearInfo', 'trademarkInfoUrl', 'proPledgeRegInfoUrl', 
					 'branchUrl', 'alterInfoUrl', 'liquidationUrl', 'shareholderUrl', 'insLicenceinfoUrl', 'getDrRaninsResUrl', 'allTrademarkUrl']

mainContent_url_list = ['allAlterInfoUrl', 'allShareHolderDetailInfoUrl', 'allPunishmentInfoUrl', 'allOtherLicenceInfoUrl', 'allMortRegInfoUrl', 'allStakQualitInfoUrl', 'allGtAlterInfoUrl', 'branchUrl']

user_agent = random.choice(user_agent_Pool.user_agent)

headers = {
			'User-Agent' : user_agent,
			'Connection' : 'keep-alive',
			'Cache-Control' : 'max-age=0',}

headers2 = {
			'User-Agent' : user_agent,
			'Accept' : 'application/json, text/javascript, */*; q=0.01',
			'Cache-Control' : 'max-age=0',
			'Upgrade-Insecure-Requests': '1'}

session = requests.Session()

def shift(x):
	t = x[0:1]
	x = x[1:]
	return t, x

def parseInt36(a, type = 36):
	x36 = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13,
			 'E':14, 'F':15, 'G':16, 'H':17, 'I':18, 'J':19, 'K':20, 'L':21, 'M':22, 'N':23, 'O':24,
			'P':25, 'Q':26, 'R':27, 'S':28, 'T':29, 'U':30, 'V':31, 'W':32, 'X':33, 'Y':34, 'Z':35}
	total = len(a[0])
	number36 = 0
	for i in range(total):
		t = x36[a[0][i].upper()] * pow(36, total-1)
		number36+= t
		total-= 1
	return number36

def clear_and_formateJs_test():
	'''
		method for test and get local file cookies
	'''
	cat = ''
	with open('../512Error/js2.html') as f:
		cat = f.readlines()[0].replace('\x00', '')
	cat = cat.replace('try{eval(y', 'try{s=y')
	cat = cat.replace(');break', ';break')
	cat = cat.replace('f=function(x,y)', 's="", f=function(x,y)')
	cat = cat.replace('</script>', 'function sss(){ return s}')
	cat = cat.replace('<script>', '')
	ctx = execjs.compile(cat)
	s = ctx.call('sss')
	print(s+'\n')
	# 清理settime
	rex = re.compile('setTimeout.*1500\);')
	s = re.sub(rex, '', s)
	# 清理结尾
	rex2 = re.compile('if\(\(function\(\).*')
	s = re.sub(rex2, '', s)
	s = s.replace('document.cookie', 'var cookie')
	rex3 = re.compile('var _1m=document.create.*firstChild.href;')
	# s = s.replace('_1m.innerHTML=\'<a href=\'/\'>_8</a>\';', 'var _1m="http://www.gsxt.gov.cn/";')
	s = re.sub(rex3, 'var _1m="http://www.gsxt.gov.cn/";', s)
	s = s.replace('GMT;Path=/;\'};', 'GMT;Path=/;\' return cookie};')
	s = s + ' function ssss(){ return %s() }' %(s[4:7])
	ctx_s = ''

	with open('./jsbeautify.js', 'r') as f:
		for line in f.readlines():
			ctx_s+= line
		
	ctx = execjs.compile(ctx_s)	
	s = ctx.call('js_beautify', s, 4, ' ')
	ctx_2 = execjs.compile(s)
	cookies = ctx_2.call('ssss')
	# assert 1>5, print(cookies)
	return cookies

def parser_page(html=None):
	'''
		get api from page
	'''
	# html = ''
	# with open('../512Error/gsxt.html', 'rb') as f:
	# 	for line in f.readlines():
	# 		html+= line.decode('utf-8', 'ignore')
	html = etree.HTML(html.text)
	if html is not None:
		script = html.xpath('.//div[@id="url"]/script')[0]
		# parser_business_license_info(html)
		# assert 1 >5, print(useful_url.values())
		# print(script.xpath('text()'))
		for i in script.xpath('text()')[0].replace('\r', '').replace('\n', '').replace(' ', '').replace(';', '').split('var'):
			# print(i.split('=')[0])
			for url in useful_url_list:
				if url == i.split('=')[0]:
					useful_url[url] = re.search(r'/%7B.*%7D', i.strip()).group(0)
	else:
		print('空值？？？')

def is_json(text):

	if isinstance(text, str):
		try:
			json.loads(text)
		except Exception as e:
			return False
		return True
	else:
		return False

def get_maincontent_url(cookies, province = 'www', times = 0):
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['allTrademarkUrl']
	response = requests.get(url, headers = headers, cookies = cookies)

	html = etree.HTML(response.text)
	if html is not None:
		script = html.xpath('.//div[@id="url"]/script')[0]
		for i in script.xpath('text()')[0].replace('\r', '').replace('\n', '').replace(' ', '').replace(';', '').split('var'):
			for url in mainContent_url_list:
				if url == i.split('=')[0]:
					mainContent_url[url] = re.search(r'/%7B.*%7D', i.strip()).group(0)
	else:
		if times < 20:
			times = times + 1
			print('尝试 %d 次' %(times))
			get_maincontent_url(cookies, province, times)
			print('空值？？？')

def get_branchUrl(cookies, company, province='www', times = 0):
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['branchUrl']
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		if is_json(response.text):
			print('分支机构信息')
			json_data = json.loads(response.text)
			datas = json_data['data']
			if datas is not None:
				# 分页查询
				# if json_data['totalPage'] > 1:
				# 	for i in range(i, int(json_data['totalPage'])):
				# 		# new_url = 'http://%s.gsxt.gov.cn' %(province)+detail_url+'?draw=%s&start=%s&length=%s&_=%s' %(i+1, i*5, 5, time.time()*1000)
				# 		form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
				# 		response2 = requests.get(url, headers = headers, cookies = cookies, data = form_data)
				# 		datas+= response2.json()['data']
				# 存入list
				branch_infos = []
				for data in datas:
					branch_info = {}
					# 公司信息
					branch_info['brName'] = data['brName']
					# 信用代码
					branch_info['regNo'] = data['regNo']
					# 注册机关
					branch_info['regOrg_CN'] = data['regOrg_CN']
					branch_info['full_name'] = company
					branch_infos.append(branch_info)
				print(branch_infos)	
				insert_into_db('branch_info', branch_infos)
	except Exception as e:
		print('---分支机构信息----Error.')
		print(e)
		return	

def get_allStakQualitInfoUrl(company, province='www'):
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['allStakQualitInfoUrl']
	response = session.get(url, headers = headers)
	try:
		if is_json(response.text):
			print('股权出质登记信息')
			json_data = json.loads(response.text)
			datas = json_data['data']
			if datas is not None:
				stakQualit_infos = []
				for data in datas:
					stakQualit_info = {}
					# 登记编号
					stakQualit_info['equityNo'] = data['equityNo']
					# 出质人
					stakQualit_info['pledgor'] = data['pledgor']
					# 出质人证照/证件号码
					stakQualit_info['pledCerNo'] = data['pledCerNo']
					# 出质股权数额(万元)
					stakQualit_info['impAm'] = data['impAm']
					# 质权人
					stakQualit_info['impOrg'] = data['impOrg']
					# 质权人证照/证件号码
					stakQualit_info['impOrgBLicNo'] = data['impOrgBLicNo']
					# 股权出质设立登记日期
					stakQualit_info['equPleDate'] = data['equPleDate']
					# 状态 1=有效， 2=无效
					stakQualit_info['type'] = data['type']
					# 公示日期
					stakQualit_info['canDate'] = data['canDate']
					# 详情
					# stakQualit_info['equityNo'] = data['equityNo']
					stakQualit_infos.append(stakQualit_info)
				print(stakQualit_infos)
				insert_into_db('stakQualit_infos', stakQualit_infos)
	except Exception as e:
		print('----股权出质登记信息----Error.')
		print(e)
		return

def get_getDrRaninsResUrl(cookies, company, province='www', times = 0):
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['getDrRaninsResUrl']
	response = requests.get(url, headers = headers, cookies = cookies)	
	try:
		if is_json(response.text):
			print('双随机抽查结果信息')
			json_data = json.loads(response.text)
			datas = json_data['data']
			if datas is not None:
				# 分页查询
				if json_data['totalPage'] > 1:
					for i in range(i, int(json_data['totalPage'])):
						# new_url = 'http://%s.gsxt.gov.cn' %(province)+detail_url+'?draw=%s&start=%s&length=%s&_=%s' %(i+1, i*5, 5, time.time()*1000)
						form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
						response2 = requests.get(url, headers = headers, cookies = cookies, data = form_data)
						datas+= response2.json()['data']
				# 存入list				
				getDrRanins_infos = []
				for data in datas:
					getDrRanins_info = {}
					# 抽查计划编号
					getDrRanins_info['raninsPlanId'] = data['raninsPlanId']
					# 抽查计划名称	
					getDrRanins_info['raninsPlaneName'] = data['raninsPlaneName']
					# 抽查任务编号	
					getDrRanins_info['raninsTaskId'] = data['raninsTaskId']
					# 抽查任务名称	
					getDrRanins_info['raninsTaskName'] = data['raninsTaskName']
					# 抽查类型	
					getDrRanins_info['raninsTypeName'] = data['raninsTypeName']
					# 抽查机关	
					getDrRanins_info['insAuth'] = data['insAuth']
					# 抽查完成日期	
					getDrRanins_info['insDate'] = data['insDate']
					# 抽查结果
					getDrRanins_info['details'] = get_getDrRanins_details(cookies, data['url'], province)
					getDrRanins_info['full_name'] = company
					getDrRanins_infos.append(getDrRanins_info)
				print(getDrRanins_infos)
				insert_into_db('getDrRanins_info', getDrRanins_infos)						
	except Exception as e:
		print('---双随机抽查结果信息----Error.')
		print(e)
		return

def get_getDrRanins_details(cookies, detail_url, province='www', times = 0):
	url = 'http://%s.gsxt.gov.cn' %(province)+detail_url
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		# 检查json格式
		if is_json(response.text):
			print('---双随机抽查结果信息详情---')
			json_data = json.loads(response.text)
			datas = json_data['data']
			if datas is not None:
				# 分页查询
				if json_data['totalPage'] > 1:
					for i in range(i, int(json_data['totalPage'])):
						new_url = 'http://%s.gsxt.gov.cn' %(province)+detail_url+'?draw=%s&start=%s&length=%s&_=%s' %(i+1, i*5, 5, time.time()*1000)
						response2 = requests.get(new_url, headers = headers, cookies = cookies)
						datas+= response2.json()['data']
				# 存入list中
				getDrRanins_details = []
				for data in datas:
					getDrRanins_detail = {}
					# 检查事项
					getDrRanins_detail['raninsItemName'] = data['raninsItemName']
					# 检查结果
					getDrRanins_detail['raninsCheckResName'] = data['raninsCheckResName']
					getDrRanins_details.append(getDrRanins_detail)
				return getDrRanins_details
	except Exception as e:
		print('---双随机抽查结果信息详情----Error.')
		print(e)
		return
		
def get_insAlterstockinfoUrl(cookies, company, province='www', times = 0):
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['insAlterstockinfoUrl']
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		if is_json(response.text):
			print('股权变更信息')
			json_data = json.loads(response.text)
			datas = json_data['data']
			if datas is not None:
				if json_data['totalPage'] > 1:
					for i in range(1, int(json_data['totalPage'])):
						form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
						response2 = requests.post(url, headers = headers, cookies = cookies, data = form_data)
						datas+= response2.json()['data']
				insAlterstock_infos = []
				for data in datas:
					insAlterstock_info = {}
					# 股东
					insAlterstock_info['inv'] = data['inv']
					# 变更前股权比例
					insAlterstock_info['transAmPrBf'] = data['transAmPrBf']
					# 变更后股权比例
					insAlterstock_info['transAmPrAf'] = data['transAmPrAf']
					# 股权变更日期
					insAlterstock_info['altDate'] = data['altDate']
					# 公示日期
					insAlterstock_info['publicDate'] = data['publicDate']
					insAlterstock_info['full_name'] = company
					insAlterstock_infos.append(insAlterstock_info)
				print(insAlterstock_infos)
				insert_into_db('insAlterstock_info', insAlterstock_infos)
		else:
			if times < 30:
				times = times + 1
				print('try : %s ' %(times))
				get_insAlterstockinfoUrl(cookies, company, province, times)		
	except Exception as e:
		print('---股权变更信息----Error.')
		print(e)
		return

def get_anCheYearInfo(cookies, company, province='www', times = 0):
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['anCheYearInfo']
	response = requests.get(url, headers = headers, cookies = cookies)
	null = ''
	try:
		print('年报信息：')
		json_data = response.text
		anCheYear_Infos = []
		print(json_data[:15])
		json_data = list(eval(json_data))
		if isinstance(json_data, list):
			for data in json_data:
				anCheYear_Info = {}
				# 公示日期
				anCheYear_Info['anCheDate'] = data['anCheDate']
				# 细节访问ID
				anCheYear_Info['anCheId'] = data['anCheId']
				# 所属年份
				anCheYear_Info['anCheYear'] = data['anCheYear']
				anCheYear_Info['details'] = get_anCheYearInfo_detail(data['anCheId'], cookies, province)
				anCheYear_Info['full_name'] = company
				anCheYear_Infos.append(anCheYear_Info)				
			print(anCheYear_Infos)
			insert_into_db('anCheYear_info', anCheYear_Infos)
	except Exception as e:
			if times < 30:
				times = times + 1
				print('try : %s ' %(times))
				get_anCheYearInfo(cookies, company, province, times)		
			else:
				print(e)
			# print('---年报信息---, 爬取失败..')

def get_anCheYearInfo_detail(anCheId, cookies, province='www'):
	info_type = ['corp-query-entprise-info-annualAlter-', 'corp-query-entprise-info-AnnSocsecinfo-',
				'corp-query-entprise-info-baseinfo-', 'corp-query-entprise-info-sponsor-', 'corp-query-entprise-info-vAnnualReportBranchProduction-',
				'corp-query-entprise-info-webSiteInfo-', 'corp-query-entprise-info-forGuaranteeinfo-']
	all_details = []
	try:
		all_details.append(get_anCheYearInfo_sponsor(anCheId, cookies, province))
		all_details.append(get_anCheYearInfo_baseinfo(anCheId, cookies, province))
		all_details.append(get_anCheYearInfo_AnnSocsecinfo(anCheId, cookies, province))
		return all_details	
	except Exception as e:
		print('年报信息：')
		print(e)

def get_anCheYearInfo_baseinfo(anCheId, cookies, province='www'):
	ty = 'corp-query-entprise-info-baseinfo-'
	url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
	details = {}
	try:
		response = requests.get(url, headers = headers, cookies = cookies)
		if response.text is not None:
			json_data = json.loads(response.text)
			if json_data['data'] is not None and len(json_data['data']) > 0:
				datas = json_data['data'][0]
				details['title'] = '基本信息'
				# 统一社会信用代码/注册号
				details['uniscId'] = datas['uniscId']
				# 企业名称
				details['entName'] = datas['entName']
				# 企业通信地址
				details['addr'] = datas['addr']
				# 邮政编码
				details['postalCode'] = datas['postalCode']
				# 企业联系电话
				details['tel'] = datas['tel']
				# 企业电子邮箱
				details['email'] = datas['email']
				# 企业经营状态
				details['busSt_CN'] = datas['busSt_CN']
				# 企业主营业务活动
				details['mainBusiAct'] = datas['mainBusiAct']
				# 从业人数
				details['empNum'] = datas['empNum']
				# 女性从业人数
				details['womemPNum'] = datas['womemPNum']
				# 企业控股情况
				details['holdingSmsg'] = datas['holdingSmsg']
				# 是否有投资信息或购买其他公司股权
				details['forInvestmentUrl'] = datas['forInvestmentUrl']
				# 是否有对外提供担保信息
				details['forGuaranteeinfoUrl'] = datas['forGuaranteeinfoUrl']
				# 有限责任公司本年度是否发生股东股权转让
				details['alterStockInfoUrl'] = datas['alterStockInfoUrl']
				return details
	except Exception as e:
		print('年报-基本信息：')
		print(e)

def get_anCheYearInfo_sponsor(anCheId, cookies, province='www'):
	ty = 'corp-query-entprise-info-sponsor-'
	url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
	details = {}
	try:
		response = requests.get(url, headers = headers, cookies = cookies)
		if response.text is not None:
			json_data = json.loads(response.text)
			if json_data['data'] is not None and len(json_data['data']) > 0:
				datas = json_data['data'][0]
				details['title'] = '股东及出资信息'
				# 股东名称
				details['invName'] = datas['invName']
				# 认缴金额
				details['liSubConAm'] = datas['liSubConAm']
				# 认缴日期
				details['subConDate'] = datas['subConDate']
				# 实缴金额
				details['liAcConAm'] = datas['liAcConAm']
				# 实缴日期
				details['acConDate'] = datas['acConDate']
				# 实缴出资方式
				details['subConFormName'] = datas['subConFormName']
				return details
	except Exception as e:
		print('年报-股东及出资信息：')
		print(e)

def get_anCheYearInfo_AnnSocsecinfo(anCheId, cookies, province='www'):
	ty = 'corp-query-entprise-info-AnnSocsecinfo-'
	url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
	details = {}
	try:
		response = requests.get(url, headers = headers, cookies = cookies)
		if response.text is not None:
			json_data = json.loads(response.text)
			if json_data['data'] is not None and len(json_data['data']) > 0:
				datas = json_data['data'][0]
				details['title'] = '社保信息'
				# 城镇职工基本养老保险
				details['so110'] = datas['so110']
				# 失业保险
				details['so210'] = datas['so210']
				# 职工基本医疗保险
				details['so310'] = datas['so310']
				# 工伤保险	
				details['so410'] = datas['so410']
				# 生育保险	
				details['so510'] = datas['so510']
				return details
	except Exception as e:
		print('年报-社保信息：')
		print(e)

def get_entBusExcepUrl(cookies, company, province='www', times = 0):
	maxtimes = 30
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['entBusExcepUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		print('列入经营异常名录信息：')
		if is_json(response.text):
			json_data = json.loads(response.text)
			datas = json_data['data']
			if datas is not None:
				entBusExcep_infos = []
				for data in datas:
					entBusExcep_info = {}
					# 列入经营异常名录原因
					entBusExcep_info['speCause_CN'] = data['speCause_CN']
					# 列入日期
					entBusExcep_info['abntime'] = data['abntime']
					# 作出决定机关(列入)
					entBusExcep_info['decOrg_CN'] = data['decOrg_CN']
					# 移出经营异常名录原因
					entBusExcep_info['remExcpRes_CN'] = data['remExcpRes_CN']
					# 移出日期
					entBusExcep_info['remDate'] = data['remDate']
					# 作出决定机关(移出)
					entBusExcep_info['reDecOrg_CN'] = data['reDecOrg_CN']
					entBusExcep_info['full_name'] = company
					entBusExcep_infos.append(entBusExcep_info)
				print(entBusExcep_infos)
				insert_into_db('entBusExcep_info', entBusExcep_infos)
			else:
				if times < maxtimes:
					times = times + 1
					time.sleep(0.2)
					print('数据为None---经营异常名录信息--- trying %d..' %(times))
					get_entBusExcepUrl(cookies, company, province, times)
				else:
					print('访问失败,次数：%d！！' %(times))
		else:
			if times < maxtimes:
				times = times + 1
				time.sleep(0.2)
				print('非json ---经营异常名录信息--- trying %d..' %(times))
				get_entBusExcepUrl(cookies, company, province, times)
			else:
				print('访问失败,次数：%d！！' %(times))
	except Exception as e:
		print('---列入经营异常名录信息---')
		print(e)

def get_mortRegInfoUrl(cookies, company, province='www'):
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['allMortRegInfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		json_data = json.loads(response.text)
		datas = json_data['data']
		if datas is not None:
			print('动产抵押登记信息')
			mort_reg_infos = []
			for data in datas:
				mort_reg_info = {}
				# 登记编号
				mort_reg_info['morRegCNo'] = data['morRegCNo']
				# 登记日期
				mort_reg_info['regiDate'] = data['regiDate']
				# 公示日期
				mort_reg_info['publicDate'] = data['publicDate']
				# 登记机关
				mort_reg_info['regOrg_CN'] = data['regOrg_CN']
				# 登记ID
				mort_reg_info['morReg_Id'] = data['morReg_Id']
				# 货币
				mort_reg_info['regCapCur_Cn'] = data['regCapCur_Cn']
				# 数量
				mort_reg_info['priClaSecAm'] = data['priClaSecAm']
				# 详细信息
				mort_reg_info['details'] = mortreg_detail_info(data['morReg_Id'], cookies)
				mort_reg_info['full_name'] = company
				mort_reg_infos.append(mort_reg_info)
			insert_into_db('mort_reg_info', mort_reg_infos)
			print(mort_reg_infos)
	except Exception as e:
		print('---动产抵押登记信息---')
		print(e)

def mortreg_detail_info(morReg_Id, cookies, province='www'):
	info_type = ['corp-query-entprise-info-mortregpersoninfo-', 'corp-query-entprise-info-mortCreditorRightInfo-',
				'corp-query-entprise-info-mortGuaranteeInfo-', 'corp-query-entprise-info-getMortAltItemInfo-',
				'corp-query-entprise-info-getMortRegCancelInfo-']
	details = {}
	try:
		for ty in info_type:
			url = 'http://%s.gsxt.gov.cn/' %(province)+ty+morReg_Id+'.html' 
			response = requests.get(url, headers = headers, cookies = cookies)	
			if response.text is not None:
				print('details . . . . ')
				json_data = json.loads(response.text)
				details[ty[25:-1]] = json_data['data']
		return details
	except Exception as e:
		print('动产抵押详情, 爬取失败.....')
				
def get_insInvinfoUrl(cookies, company, province='www'):
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['insInvinfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	json_data = json.loads(response.text)
	ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
	datas = json_data['data']

	print('股东及出资信息')
	if datas is not None:
		insInv_infos = []
		for data in datas:
			insInv_info = {}
			# 股东
			insInv_info['inv'] = data['inv']
			# 认缴额（万元）
			insInv_info['subSum'] = data['subSum']
			# 实缴额（万元）
			insInv_info['aubSum'] = data['aubSum']
			# 认缴明细
			sub_details = []
			for s in data['subDetails']:
				sub_detail = {}
				# 认缴出资方式
				sub_detail['subConForm_CN'] = s['subConForm_CN']
				# 认缴出资金额(万元)	
				sub_detail['subConAmStr'] = s['subConAmStr']
				# 认缴出资日期
				sub_detail['currency'] = s['currency']
				sub_details.append(sub_detail)
			# sub_details = {	
			# 				# 认缴出资方式
			# 				'subConForm_CN' : data['subDetails'][0]['subConForm_CN'],
			# 				# 认缴出资金额(万元)	
			# 				'subConAmStr' : data['subDetails'][0]['subConAmStr'],
			# 				# 认缴出资日期	
			# 				'currency' : data['subDetails'][0]['currency'],
			# 				}
			insInv_info['sub_details'] = sub_details
			# 实缴明细
			aub_details = []
			for a in data['aubDetails']:
				aub_detail = {}
				# 实缴出资方式
				aub_detail['acConFormName'] = a['acConFormName']
				# 实缴出资额(万元)	
				aub_detail['acConAmStr'] = a['acConAmStr']
				# 实缴出资日期
				aub_detail['conDate'] = a['conDate']
				aub_details.append(aub_detail)			
			# aub_details = {
			# 				# 实缴出资方式	
			# 				'acConFormName' : data['aubDetails'][0]['acConFormName'],
			# 				# 实缴出资额(万元)	
			# 				'acConAmStr' : data['aubDetails'][0]['acConAmStr'],
			# 				# 实缴出资日期
			# 				'conDate' : data['aubDetails'][0]['conDate'],
			# 				}
			insInv_info['aub_details'] = aub_details
			insInv_info['full_name'] = company

			insInv_infos.append(insInv_info)
		print(insInv_infos)
		insert_into_db('insInv_info', insInv_infos)

def get_insLicenceinfoUrl(cookies, company, province='www'):
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['insLicenceinfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		json_data = json.loads(response.text)
		datas = json_data['data']
		print('基本信息中的—行政许可信息')
		insLicenceinfos = []
		for data in datas:
			insLicenceinfo = {}
			insLicenceinfo['licNo'] = data['licNo']
			insLicenceinfo['licName_CN'] = data['licName_CN']
			insLicenceinfo['valFrom']  = data['valFrom'] 
			insLicenceinfo['valTo']  = data['valTo'] 
			insLicenceinfo['licAnth']  = data['licAnth'] 
			insLicenceinfo['licItem']  = data['licItem']
			insLicenceinfo['full_name']  = company
			insLicenceinfos.append(insLicenceinfo)
		print(insLicenceinfos)
		insert_into_db('insLicence_info', insLicenceinfos)
	except Exception as e:
		print(e)
		
def get_spotCheck_info(cookies, company, province='www'):

	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['spotCheckInfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	datas = response.json()['data']
	print('抽查抽检信息：')	
	
	spotChecks = []
	for data in datas:
		spotCheck = {}
		spotCheck['insAuth_CN'] = data['insAuth_CN']
		spotCheck['insRes_CN'] = data['insRes_CN']
		spotCheck['insType'] = data['insType']
		spotCheck['insDate'] = data['insDate']
		spotCheck['full_name'] = company
		spotChecks.append(spotCheck)
	print(spotChecks)
	insert_into_db('spotCheck_info', spotChecks)

def get_shareHolder_info(cookies, company, province='www'):
	'''
		get shareHolder_info from shareHolderUrl
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['allShareHolderDetailInfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		datas = response.json()['data']
		totalPage = response.json()['totalPage']
		ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
		print('股东:')
		# for i in range(1, int(totalPage)):
		# 	form_data = {'draw' : i+1, 'start' : 5*i, 'length' : 5}
		# 	res = requests.post(url, headers = headers, cookies = cookies, data = form_data)
		# 	res_datas = res.json()['data']
		# 	datas+= res_datas	
		shareholders = []
		for data in datas:
			shareholder = {}
			# 证照/证件号码
			shareholder['blicNo'] = re.sub(ctx, '', data['bLicNo'])
			# 股东名称
			shareholder['inv'] = data['inv']
			# 股东类型
			shareholder['invType_CN'] = re.sub(ctx, '', data['invType_CN'])
			# 证照/证件类型
			shareholder['blicType_CN'] = data['blicType_CN']
			shareholder['full_name'] = company
			shareholders.append(shareholder)
		print(shareholders)
		insert_into_db('shareholder_info', shareholders)
	except Exception as e:
		print(e)
	
def get_key_person_info(cookies, company, province='www'):
	'''
		parser key_person_info
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['keyPersonUrl'] 
	# assert 1>5, 
	response = requests.get(url, headers = headers, cookies = cookies)
	try:
		datas = response.json()['data']
		ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
		print('关键人物:')
		
		names = []
		for data in datas:
			name_dict = {}
			# 姓名
			name = re.sub(ctx, '', data['name'])
			name_dict['name'] = name
			name_dict['full_name'] = company
			print(name_dict)
			names.append(name_dict)
		insert_into_db('keyperson_info', names)
	except Exception as e:
		print(e)
	
def get_otherLicenceDetailInfoUrl(cookies, company, province='www'):
	'''
		parser otherLicenceDetailInfo
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['allOtherLicenceInfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	json_data = json.loads(response.text)
	datas = json_data['data']
	ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
	
	if json_data['data'] is not None:
		print('行政许可信息:')
		# if int(json_data['totalPage']) > 1:
			# for i in range(1, json_data['totalPage']):
			# 	form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
			# 	response2 = requests.post(url, headers = headers, data = form_data, cookies = cookies)
			# 	json_data = json.loads(response2.text)
			# 	datas+= json_data['data']
		other_licence_infos = []
		for data in datas:
			info = {}
			# 许可文件编号
			info['licNo'] = data['licNo']
			# 许可文件名称	
			info['licName_CN'] = data['licName_CN']
			# 有效期自	
			info['valFrom'] = data['valFrom']
			# 有效期至	
			info['valTo'] = data['valTo']
			# 许可机关	
			info['licAnth'] = data['licAnth']
			# 许可内容
			info['licItem'] = data['licItem']
			info['full_name'] = company
			other_licence_infos.append(info)
		print(other_licence_infos)
		insert_into_db('other_licence_info', other_licence_infos)	

def get_liquidationUrl(cookies, company, province='www'):
	'''
		parser liquidation
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['liquidationUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	datas = response.json()['data']
	ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
	print('清算信息:')
	
	liqs = []
	for data in datas:
		liq = {}
		# 清算组成员
		liq['liqMen'] = re.sub(ctx, '', data['liqMem'])
		# 疑似级别 递减 
		liq['ligpriSign'] = data['ligpriSign']
		liq['full_name'] = company
		liqs.append(liq)
	print(liqs)
	insert_into_db('liquidation_info', liqs)	

def get_alterInfoUrl(cookies, company, province='www', times = 0):
	'''
		parser alterInfo
	'''
	maxtimes = 30
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['allAlterInfoUrl'] 
	response = requests.get(url, headers = headers2, cookies = cookies)
	try:
		total_data = response.text
		if is_json(total_data):
			total_data = json.loads(total_data)
			datas = total_data['data']
			if datas is not None:
				print('变更信息 :')
				# for i in range(1, int(total_data['totalPage'])):
				# 	form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
				# 	response2 = requests.post(url, headers = headers2, data = form_data, cookies = cookies)
				# 	json_Data = json.loads(response2.text)
				# 	if json_Data['data'] is not None:
				# 		datas+= json_Data['data']
				ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
				altDatas = []
				for data in datas:
					altData = {}
					# 变更事项
					altData['altItem_CN'] = altItem_CN = re.sub(ctx, '', data['altItem_CN'])
					# 变更后
					altData['altAf'] = data['altAf']
					# 变更前
					altData['altBe'] =  data['altBe']
					# 变更日期 时间戳（毫秒）
					altData['altDate'] = time.strftime("%Y--%m--%d %H:%M:%S", time.localtime(data['altDate']//1000))
					altData['full_name'] = company
					altDatas.append(altData)
				print(altDatas)
				insert_into_db('alter_info', altDatas)
			else:
				if times < maxtimes:
					times = times + 1
					time.sleep(0.2)
					print('变更信息 :trying %d..' %(times))
					get_alterInfoUrl(cookies, company, province, times)
				else:
					print('访问失败,次数：%d！！' %(times))
		else:
			if times < maxtimes:
				times = times + 1
				time.sleep(0.2)
				print('非json 变更信息 :trying %d..' %(times))
				get_alterInfoUrl(cookies, company, province, times)
			else:
				print('访问失败,次数：%d！！' %(times))			
	except Exception as e:
		print('----变更信息----Error')
		print(e)
		return
		
def get_trademarkInfoUrl(cookies, company, province='www'):
	'''
		parser trademark
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['trademarkInfoUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	total_data = response.json()
	datas = total_data['data']
	ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
	if  datas is not None:
		print('商标信息:')
		for i in range(1, total_data['totalPage']):
			responses = requests.get(url+'?start=%d' %(i*4), headers = headers, cookies = cookies)
			trade_data = responses.text
			trade_data = json.loads(trade_data)
			if trade_data['data'] is not None:
				datas+= trade_data['data']
		
		trade_marks = []
		for data in datas:
			trade_mark = {}
			# 商标共有人
			trade_mark['coownerCnName'] = data['coownerCnName']
			# 商品/服务项目
			trade_mark['goodsCnName'] =data['goodsCnName']
			# 类别
			trade_mark['intCls'] =data['intCls']
			# 起日期
			trade_mark['propertyBgnDate'] =data['propertyBgnDate']
			# 止日期
			trade_mark['propertyEndDate'] =data['propertyEndDate']
			# 注册公告日期
			trade_mark['regAnncDate'] =data['regAnncDate']
			# 注册公告期号
			trade_mark['regAnncIssue'] =data['regAnncIssue']
			# 商标注册号
			trade_mark['regNum'] =data['regNum']
			trade_mark['full_name'] = company
			trade_marks.append(trade_mark)		
		print(trade_marks)
		insert_into_db('trademark_info', trade_marks)	

def get_punishmentDetailInfoUrl(cookies, company, province='www'):
	'''
		parser punishmentDetailInfoUrl
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+mainContent_url['allPunishmentInfoUrl']
	response = requests.get(url, headers = headers, cookies = cookies)
	if is_json(response.text):
		json_data = json.loads(response.text)
		datas = json_data['data']
		ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
		punishment_infos = []
		if datas is not None:
			print('行政处罚信息:')
			for data in datas:
				punishment_info = {}
				# 决定文书号
				punishment_info['penDecNo'] = data['penDecNo']
				# 违法行为类型	
				punishment_info['illegActType'] = data['illegActType']
				# 行政处罚内容
				punishment_info['penContent'] = data['penContent']
				# 决定机关名称
				punishment_info['penAuth_CN'] = data['penAuth_CN']
				# 处罚决定日期
				punishment_info['penDecIssDate'] = data['penDecIssDate']
				# 公示日期
				punishment_info['publicDate'] = data['publicDate']
				punishment_info['full_name'] = company
				punishment_infos.append(punishment_info)
			print(punishment_infos)
			insert_into_db('punishment_info', punishment_infos)

def get_assistUrl(cookies, company, province='www'):
	'''
		parser assistUrl
	'''
	url = 'http://%s.gsxt.gov.cn' %(province)+useful_url['assistUrl'] 
	response = requests.get(url, headers = headers, cookies = cookies)
	datas = response.json()['data']
	ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
	print('司法协助信息：')
	
	assists = []
	for data in datas:
		assist = {}
		# 执行通知书文号
		assist['executeNo'] = data['executeNo']
		# 股权数额
		assist['froAm'] = data['froAm']
		# 执行法院
		assist['froAuth'] = data['froAuth']
		# 被执行人
		assist['inv'] = data['inv']
		# 货币
		assist['regCapCur_CN'] = data['regCapCur_CN']
		# 详细信息 http://www.gsxt.gov.cn/corp-query-entprise-info-judiciaryStockfreeze-PROVINCENODENUM2300001230610001522590908.html
		# assist['parent_Id'] = data['parent_Id']
		assist['details'] = get_assistUrl_details(province, data['parent_Id'])
		assist['full_name'] = company
		assists.append(assist)
		print(assist)
	insert_into_db('assist_info', assists)

def get_assistUrl_details(province='www', parent_Id):
	'''
		details for assistUrl
	'''
	url = 'http://%s.gsxt.gov.cn/corp-query-entprise-info-judiciaryStockfreeze-%s.html' %(province, parent_Id)
	response = session.get(url, headers = headers)
	if is_json(response.text):
		json_data = json.loads(response.text)
		detail = []
		if json_data['data'] is not None:
			for data in json_data['data']:
				details = {}
				# 执行法院
				details['froAuth'] = data['froAuth']
				# 执行事项	
				details['executeItem_CN'] = data['executeItem_CN']
				# 执行裁定书文号	
				details['executeNo'] = data['executeNo']
				# 执行通知书文号	
				details['froDocNo'] = data['froDocNo']				
				# 被执行人	
				details['inv'] = data['inv']
				# 被执行人持有股权、其它投资权益的数额 (美元)
				details['froAm'] = data['froAm']				
				# 被执行人证照种类	
				details['bLicType_CN'] = data['bLicType_CN']				
				# 被执行人证照号码	
				details['bLicNo'] = data['bLicNo']
				# 冻结期限自	
				details['froFrom'] = data['froFrom']
				# 冻结期限至	
				details['froTo'] = data['froTo']
				# 冻结期限
				details['frozDeadline'] = data['frozDeadline']	
				# 公示日期	
				details['publicDate'] = data['publicDate']
				# title
				details['title'] = '司法协助详细信息'
				detail.append(details)
			return detail

def parser_business_license_info(html = None):
	if html is not None:
		# 营业执照信息 - No 1
		# 企业全名
		# 统一社会信用代码
		# 法定代表人
		# 登记机关
		# 成立日期
		# 类型
		# 注册资本
		# 营业期限自
		# 营业期限至
		# 企业状态
		# 核准日期
		# 住址
		# 经营范围
		html = etree.HTML(html.text)
		if html is not None:
			size = 0
			business_license_info = {}
			start_date = ''
			end_date = ''
			reg_capital = ''
			fullName =  html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[2]/dd/text()')[0].strip()
			society_id = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[1]/dd/text()')[0].strip('"').strip()
			company_Type = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[3]/dd/text()')[0].strip()	
			owner = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[4]/dd/text()')[0].strip()
			if len(html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl')) == 12:
				start_date = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[5]/dd/text()')[0].strip() 
				end_date = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[6]/dd/text()')[0].strip()	
				size = -1
			else:
				reg_capital = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[5]/dd/text()')[0].strip('"').strip() 
				start_date = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[7]/dd/text()')[0].strip() 
				end_date = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[8]/dd/text()')[0].strip()	
				business_license_info['reg_capital'] = reg_capital

			reg_authority = html.xpath('/html/body/div[5]/div[4]/div[2]/div[27]/div[4]/div[2]/span[3]/span/text()')[0].strip()
			reg_date = html.xpath('/html/body/div[5]/div[4]/div[2]/div[27]/div[4]/div[2]/span[4]/span/text()')[0].strip()
			
			company_status = html.xpath('/html/body/div[5]/div[4]/div[2]/div[27]/div[4]/div[2]/div/span[1]/text()')[0].strip()	
			issue_date = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[10]/dd/text()')[0].strip() 
			address = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[%d]/dd/text()' %(12 + size))[0].strip()	
			manage_scope = html.xpath('//*[@id="primaryInfo"]/div/div[2]/dl[%d]/dd/text()' %(13 + size))[0].strip()	


			business_license_info = {'full_name' : fullName, 'society_id' : society_id, 'owner' : owner, 'reg_capital' : reg_capital, 'reg_date' : reg_date,  'company_Type' : company_Type,
									 'start_date' : start_date, 'end_date' : end_date, 'company_status' : company_status, 'issue_date' : issue_date, 'address' : address,
									'manage_scope' : manage_scope}
			print('基本信息:')
			data = []
			data.append(business_license_info)
			insert_into_db('business_license_info', data)
			print(business_license_info)
		else:
			print(html)

def clear_and_formateJs_test(js):
	'''
		method for get web cookies
	'''
	js = js.replace('\x00', '')
	cat = ''
	ctx = ''
	s = ''
	functionName = ''
	try:
		# 替换k的生成方式
		cat = js.replace('try{eval(y', 'try{z=z+1;s=(y')
		cat = cat.replace('f=function(x,y)', 's="", f=function(x,y)')
		cat = cat.replace('</script>', 'function sss(){ return s}')
		cat = cat.replace('<script>', '')
		ctx = execjs.compile(cat)
		s = ctx.call('sss')
		print(s[:50])
		if re.search(r'var (.*)=function\(\){setTimeout', s) is not None:
			functionName = re.search(r'var (.*)=function\(\){setTimeout', s).group(1)
			# 清理settime
			rex = re.compile('setTimeout.*\d{1,4}\);')
			s = re.sub(rex, '', s)
			# 清理结尾
			rex2 = re.compile('GMT;.*')
			s = re.sub(rex2, 'GMT;\' \nreturn cookie};', s)
			# 清理其中未定义的document
			s = s.replace('document.cookie', 'var cookie')
			rex3 = re.compile('var %s=document.create.*firstChild.href;' %(functionName))
			s = re.sub(rex3, 'var %s="http://www.gsxt.gov.cn/";' %(functionName), s)
			s = s.replace('GMT;Path=/;\'};', 'GMT;\' \nreturn cookie};')
			ctx_s = ''

			with open('./jsbeautify.js', 'r') as f:
				for line in f.readlines():
					ctx_s+= line	

			ctx = execjs.compile(ctx_s)	
			s = ctx.call('js_beautify', s, 4, '')
			rex8 = re.compile("return cookie};\n.*", flags = re.MULTILINE)
			# 清理未定义的Windows
			s = s.replace("window['__p' + 'hantom' + 'as']", "undefined")
			s = s.replace("window['_p' + 'hantom']", "undefined")
			s = s.replace('window.headless', 'undefined')
			s = s.replace("window['callP' + 'hantom']", "undefined")
			s = s.replace("D.headless", "undefined")
			s = re.sub(rex8, 'return cookie};', s)
			s = s + '\n function ssss(){ return %s() }' %(functionName)

			# rex4 = re.compile("window\['callP'.*'hantom'\]", flags = re.MULTILINE)
			# rex5 = re.compile("window\['__p'.*'hantom'.*'as'\]", flags = re.MULTILINE)
			# rex6 = re.compile("window\['_p'.*'hantom'\]", flags = re.MULTILINE)
			# rex7 = re.compile("window.*headless", flags = re.MULTILINE)

			# s = re.sub(rex4, 'undefined', s)
			# s = re.sub(rex5, 'undefined', s)
			# s = re.sub(rex6, 'undefined', s)
			# s = re.sub(rex7, 'undefined', s)
			ctx_2 = execjs.compile(s)
			# print(s)
			cookies = ctx_2.call('ssss')
			return cookies
		else:
			# 替换k的生成方式
			cat = js.replace('try{eval(y', 'try{s=(y')
			cat = cat.replace('f=function(x,y)', 's="", f=function(x,y)')
			cat = cat.replace('</script>', 'function sss(){ return s}')
			cat = cat.replace('<script>', '')
			ctx = execjs.compile(cat)
			s = ctx.call('sss')
			print(s[:50])
			functionName = re.search(r'var (.*)=function\(\){setTimeout', s).group(1)
			# 清理settime
			rex = re.compile('setTimeout.*\d{1,4}\);')
			s = re.sub(rex, '', s)
			# 清理结尾 并加上 return cookie
			rex2 = re.compile('GMT;.*')
			s = re.sub(rex2, 'GMT;\' \nreturn cookie};', s)
			s = s.replace('document.cookie', 'var cookie')
			rex3 = re.compile('var %s=document.create.*firstChild.href;' %(functionName))
			s = re.sub(rex3, 'var %s="http://www.gsxt.gov.cn/";' %(functionName), s)
			# s = s.replace('GMT;Path=/;\'};', 'GMT;\' \nreturn cookie};')
			ctx_s = ''

			with open('./jsbeautify.js', 'r') as f:
				for line in f.readlines():
					ctx_s+= line	

			ctx = execjs.compile(ctx_s)	
			s = ctx.call('js_beautify', s, 4, '')

			# 替换各种防止无头
			rex8 = re.compile("return cookie};\n.*", flags = re.MULTILINE)
			s = s.replace("window['__p' + 'hantom' + 'as']", "undefined")
			s = s.replace("window['_p' + 'hantom']", "undefined")
			s = s.replace('window.headless', 'undefined')
			s = s.replace("window['callP' + 'hantom']", "undefined")
			s = s.replace('D.headless', "undefined")
			s = re.sub(rex8, 'return cookie};', s)
			# 添加 ssss()
			s = s + '\n function ssss(){ return %s() }' %(functionName)

			# rex4 = re.compile("window\['callP'.*'hantom'\]", flags = re.MULTILINE)
			# rex5 = re.compile("window\['__p'.*'hantom'.*'as'\]", flags = re.MULTILINE)
			# rex6 = re.compile("window\['_p'.*'hantom'\]", flags = re.MULTILINE)
			# rex7 = re.compile("window.*headless", flags = re.MULTILINE)
			# s = re.sub(rex4, 'undefined', s)
			# s = re.sub(rex5, 'undefined', s)
			# s = re.sub(rex6, 'undefined', s)
			# s = re.sub(rex7, 'undefined', s)
			ctx_2 = execjs.compile(s)
			# print(s)
			cookies = ctx_2.call('ssss')
			return cookies	
	except Exception as e:
		with open('../512Error/%s.html' %(time.time()), 'w', encoding='utf-8') as f:
			f.write(js.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			f.write(cat.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			f.write(s.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			raise e
	# try:
	# 	# 清理settime
	# 	rex = re.compile('setTimeout.*1500\);')
	# 	s = re.sub(rex, '', s)
	# 	# 清理结尾
	# 	rex2 = re.compile('if\(\(function\(\).*')
	# 	s = re.sub(rex2, '', s)
	# 	s = s.replace('document.cookie', 'var cookie')
	# 	rex3 = re.compile('var _1m=document.create.*firstChild.href;')
	# 	s = re.sub(rex3, 'var _1m="http://www.gsxt.gov.cn/";', s)
	# 	s = s.replace('GMT;Path=/;\'};', 'GMT;Path=/;\' return cookie};')
	# 	s = s + ' function ssss(){ return %s() }' %(functionName)
	# 	ctx_s = ''

	# 	with open('./jsbeautify.js', 'r') as f:
	# 		for line in f.readlines():
	# 			ctx_s+= line	

	# 	ctx = execjs.compile(ctx_s)	
	# 	s = ctx.call('js_beautify', s, 4, ' ')
	# 	# print(s)
	# 	s = s.replace("window['__p' + 'hantom' + 'as']", "undefined")
	# 	s = s.replace("window['_p' + 'hantom']", "undefined")
	# 	s = s.replace('window.headless', 'undefined')
	# 	s = s.replace("window['callP' + 'hantom']", "undefined")
	# 	# s = s.replace('! false', '!false')undefined
	# 	# print(s)
	# 	ctx_2 = execjs.compile(s)
	# 	cookies = ctx_2.call('ssss')
	# 	return cookies
	# except Exception as e:

def clear_and_formateJs(jst = None, times = 0):
	'''
		author: sam
		整理cookies加密函数
		并取得cookies

	'''
	js = jst.replace('\x00', '')
	cat = ''
	ctx = ''
	s = ''
	functionName = ''
	try:
		# 替换k的生成方式
		cat = js.replace('try{eval(y', 'try{z=z+%s; s=(y' %(times))
		cat = cat.replace('f=function(x,y)', 's="", f=function(x,y)')
		cat = cat.replace('</script>', 'function sss(){ return s}')
		cat = cat.replace('<script>', '')
		ctx_s = ''

		ctx = execjs.compile(cat)
		s = ctx.call('sss')
		print(s[:50])
		if re.search(r'var (.*)=function\(\){setTimeout', s) is not None:
			functionName = re.search(r'var (.*)=function\(\){setTimeout', s).group(1)
			# 清理settime
			rex = re.compile('setTimeout.*\d{1,4}\);')
			s = re.sub(rex, '', s)
			# 清理结尾
			rex2 = re.compile('GMT;.*')
			s = re.sub(rex2, 'GMT;\' \nreturn cookie};', s)
			# 清理其中未定义的document
			s = s.replace('document.cookie', 'var cookie')
			rex3 = re.compile('var %s=document.create.*firstChild.href;' %(functionName))
			s = re.sub(rex3, 'var %s="http://www.gsxt.gov.cn/";' %(functionName), s)
			s = s.replace('GMT;Path=/;\'};', 'GMT;\' \nreturn cookie};')
			ctx_s = ''
			# 美化JS以便解密
			with open('./jsbeautify.js', 'r') as f:
				for line in f.readlines():
					ctx_s+= line	
			ctx = execjs.compile(ctx_s)	
			s = ctx.call('js_beautify', s, 4, '')
			rex8 = re.compile("return cookie};\n.*", flags = re.MULTILINE)
			# 清理未定义的Windows
			s = s.replace("window['__p' + 'hantom' + 'as']", "undefined")
			s = s.replace("window['_p' + 'hantom']", "undefined")
			s = s.replace('window.headless', 'undefined')
			s = s.replace("window['callP' + 'hantom']", "undefined")
			s = s.replace("D.headless", "undefined")
			s = re.sub(rex8, 'return cookie};', s)
			s = s + '\n function ssss(){ return %s() }' %(functionName)
			ctx_2 = execjs.compile(s)
			cookies = ctx_2.call('ssss')
			return cookies
		else:
			times = times + 1
			if times > 20:
				return
			else:
				return clear_and_formateJs(jst = jst, times = times)

	except Exception as e:
		with open('../512Error/%s.html' %(time.time()), 'w', encoding='utf-8') as f:
			f.write(js.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			f.write(cat.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			f.write(s.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
		return clear_and_formateJs(jst = jst, times = times)
		print(e)

def getTarget_cookies(tail_url=None, province='www', times = 0):
	'''
		get page_source and cookies
	'''
	try:
		url = 'http://%s.gsxt.gov.cn' %(province)+tail_url
		response = session.get(url, headers = headers)
		set_cookies = response.headers['set-cookie'].split(';')
		encry_cookies = clear_and_formateJs(response.text).split(';')

		name, value = encry_cookies[0].split('=', 1)
		name2, value2 = set_cookies[0].split('=', 1)
		cookies = {name:value, name2:value2}

		session.cookies['__jsl_clearance'] = value

		response2 = session.get(url, headers = headers)
		while response2.status_code != 200:
			print(response2.status_code)
			response2 = session.get(url, headers = headers)
			times+= 1
			if times > 20:
				break
		return response2, cookies
	except Exception as e:
		raise e
	
def mongo(collection_name):
	conn = MongoClient('127.0.0.1', 27017)
	db = conn.jkspider
	collection = db['%s' %(collection_name)]
	return collection
	# other_licence_info = db.other_licence_info
	# href_collections = db.business_hrefs
	# business_license_info = db.business_license_info
	# shareholder_info = db.shareholder_info
	# keyperson_info = db.keyperson_info
	# assist_info = db.assist_info
	# trademark_info = db.trademark_info
	# liquidation_info = db.liquidation_info
	# spotCheck_info = db.spotCheck_info
	# alter_info = db.alter_info
	# insLicence_info = db.insLicence_info

def insert_into_db(collection_name, datas):
	collection = mongo(collection_name)
	if len(datas) > 0:
		collection.insert_many(datas)

def insert_name_in_db(business, url):
	collection = mongo('business_url')
	collection.insert({'business_name': business, 'url' : url})

def find_business_from_db(business = None):
	collection = mongo('business_url')
	if business is None:
		data =  collection.find({'business_name': {'$regex' : r'.*'}})
	else:
		data = collection.find({'business_name' : business})
	return data

def test():
	'''
		just a test!!
	'''
	s = '''
		var _2p=function(){setTimeout('location.href=location.pathname+location.search.replace(/[\?|&]captcha-challenge/,\'\')',1500);document.cookie='__jsl_clearance=1527470647.484|0|'+(function(){var _1w=[function(_2p){return _2p},function(_1w){return _1w},(function(){var _2p=document.createElement('div');_2p.innerHTML='_19';_2p=_2p.firstChild.href;var _1w=_2p.match(/https?:\/\//)[0];_2p=_2p.substr(_1w.length).toLowerCase();return function(_1w){for(var _19=0;_19<_1w.length;_19++){_1w[_19]=_2p.charAt(_1w[_19])};return _1w.join('')}})(),function(_2p){return eval('String.fromCharCode('+_2p+')')}],_19=[[-~[((+!!!window.headless)|-~(+!!!window.headless))+4]],'B',(window['callP'+'hantom']+[]).charAt(~~!{})+([][[]]+[]+[[]][0]).charAt(2),'4',[{}+[]+[]][0].charAt(-~[-~(+!{})-~(+!{})])+(window['callP'+'hantom']+[]).charAt(~~!{})+({}+[[]][0]).charAt((-~[]<<-~[])-~(+!{})-~(-~[]-~[-~(+!{})-~(+!{})])),[(-~[]+(-~!/!/<<-~(+!{})-~(+!{}))+[]+[[]][0])],(2+[]+[]),'U',[[-~(+!{})]+[-~(+!{})]],[((-~[]+[(-~[]<<-~[])])/[(-~[]<<-~[])]+[]+[[]][0])+(((+!!!window.headless)|-~(+!!!window.headless))+4+[[]][0]),((-~[]+[(-~[]<<-~[])])/[(-~[]<<-~[])]+[]+[[]][0])+((+!!!window.headless)-~[((+!!!window.headless)|-~(+!!!window.headless))+4]+[]+[[]][0])],'r',[(-~[]+(-~!/!/<<-~(+!{})-~(+!{}))+[]+[[]][0])],'bl',[((-~[]+[(-~[]<<-~[])])/[(-~[]<<-~[])]+[]+[[]][0])+(-~[]+(-~!/!/<<-~(+!{})-~(+!{}))+[]+[[]][0])],'Om',[[-~(+!{})]+[-~(+!{})]+(((+!!!window.headless)|2)+[[]][0])],[((-~[]+[(-~[]<<-~[])])/[(-~[]<<-~[])]+[]+[[]][0])],(2+[]+[]),'sy8',[(((+!!!window.headless)|2)+[[]][0])+(((+!!!window.headless)|-~(+!!!window.headless))+4+[[]][0])],'3',[((-~[]+[(-~[]<<-~[])])/[(-~[]<<-~[])]+[]+[[]][0])+[-~[((+!!!window.headless)|-~(+!!!window.headless))+4]]]];for(var _2p=0;_2p<_19.length;_2p++){_19[_2p]=_1w[[0,1,0,1,0,2,0,1,2,3,1,2,1,3,1,3,2,0,1,3,1,3][_2p]](_19[_2p])};return _19.join('')})()+';Expires=Mon, 28-May-18 02:24:07 GMT;Path=/;'};if((function(){try{return !!window.addEventListener;}catch(e){return false;}})()){document.addEventListener('DOMContentLoaded',_2p,false)}else{document.attachEvent('onreadystatechange',_2p)}		
	'''
	functionName = re.search(r'var (.*)=function\(\){setTimeout', s).group(1) 	
	# rex = re.compile('setTimeout.*, \d{1,4}\);', flags = re.MULTILINE)
	# s = re.sub(rex, '', s)
	# 清理结尾
	# rex2 = re.compile('if\(\(function\(\).*')
	# s = re.sub(rex2, '', s)

	rex2 = re.compile('GMT;.*')
	s = re.sub(rex2, 'GMT;\' \nreturn cookie};', s)
	s = s.replace('document.cookie', 'var cookie')
	rex3 = re.compile('var %s=document.create.*firstChild.href;' %(functionName))
	s = re.sub(rex3, 'var %s="http://www.gsxt.gov.cn/";' %(functionName), s)
	rex = re.compile('setTimeout.*\d{1,4}\);')
	s = re.sub(rex, '', s)
	# s = s.replace('GMT;Path=/;\'};','GMT;\' \n return cookie};')
	
	ctx_s = ''
	with open('./jsbeautify.js', 'r') as f:
		for line in f.readlines():
			ctx_s+= line	

	ctx = execjs.compile(ctx_s)	
	s = ctx.call('js_beautify', s, 4, ' ')
	rex4 = re.compile("window\['callP'.*'hantom'\]", flags = re.MULTILINE)
	rex5 = re.compile("window\['__p'.*'hantom'.*'as'\]", flags = re.MULTILINE)
	rex6 = re.compile("window\['_p'.*'hantom'\]", flags = re.MULTILINE)
	rex7 = re.compile("window.*headless", flags = re.MULTILINE)
	rex9 = re.compile("D.headless", flags = re.MULTILINE)
	rex8 = re.compile("return cookie};\n.*", flags = re.MULTILINE)
	s = re.sub(rex4, 'undefined', s)
	s = re.sub(rex5, 'undefined', s)
	s = re.sub(rex6, 'undefined', s)
	s = re.sub(rex7, 'undefined', s)
	s = re.sub(rex9, 'undefined', s)
	s = re.sub(rex8, 'return cookie};', s)
	s = s + '\n function ssss(){ return %s() }' %(functionName)
	# rex4 = re.compile("window\['callP'.*'hantom'\]", flags = re.MULTILINE)
	# s = s.replace("window['__p' + 'hantom' + 'as']", "undefined")
	# s = s.replace("window['_p' + 'hantom']", "undefined")
	# s = s.replace('window.headless', 'undefined')
	# s = re.sub(rex4, 'undefined', s)
	# s = s.replace("window['callP' + 'hantom']", "undefined")
	print(s)
	# ctx_s = ''
	# with open('./jsbeautify.js', 'r') as f:
	# 	for line in f.readlines():
	# 		ctx_s+= line
		
	# ctx = execjs.compile(ctx_s)	
	# ss = ctx.call('js_beautify', ss, 4, ' ')
	# print(ss.replace("window['__p' + 'hantom' + 'as']", 'false'))
	# s = '<div class="dp">5aSW5Zu9KOWcsOWMuinkvIHkuJo=</div>外<div class="dp">5aSW5Zu9KOWcsOWMuinkvIHkuJo=</div>国<div class="dp">5aSW5Zu9KOWcsOWMuinkvIHkuJo=</div>(<div class="dp">5aSW5Zu9KOWcsOWMuinkvIHkuJo=</div>地<div class="dp">5aSW5Zu9KOWcsOWMuinkvIHkuJo=</div>区)企业'
	# ss = '<div class="dp">MzIwNTk0MDAwMTU3Nw==</div>32<div class="dp">MzIwNTk0MDAwMTU3Nw==</div><div class="dp">MzIwNTk0MDAwMTU3Nw==</div>0594<div class="dp">MzIwNTk0MDAwMTU3Nw==</div>0<div class="dp">MzIwNTk0MDAwMTU3Nw==</div><div class="dp">MzIwNTk0MDAwMTU3Nw==</div>00<div class="dp">MzIwNTk0MDAwMTU3Nw==</div>15<div class="dp">MzIwNTk0MDAwMTU3Nw==</div>7<div class="dp">MzIwNTk0MDAwMTU3Nw==</div>7<div class="dp">MzIwNTk0MDAwMTU3Nw==</div>62'

	# ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
	# altItem_CN = re.sub(ctx, '', ss)
	# print(altItem_CN)

def get_all_info(business, tail, cookies, province = 'www', times = 0):
	# business = '上海永巧塑料有限公司'
	# tail = '/%7BD3937CA5B4F58D285881D697E7863120F93383F3B27819C22D6C7DA46E0A2DF4A36908D33C7DCD687A6BCEDC6C3B8BCAFFEC13C4E225E109CE31CF27E003A95F8CDC8CDC8C7AA9F9A9F9A9F9A9F9A92B77277781D16B37D383D38F0DFB392295F1FABDCDAC1B8ED9C8B8F79A49247402B21705B57FC8B8F7247424742474-1527474744125%7D'
	# js 江苏 苏州 昆山 无锡
	url = 'http://%s.gsxt.gov.cn' %(province)+tail
	response = requests.get(url, headers = headers, cookies=cookies)

	if response.status_code == 200:
		# 取得大量Url
		parser_page(response)
		# 取得免分页的信息
		get_maincontent_url(cookies, province)
		# 基本信息
		parser_business_license_info(response)
		# 股东
		get_shareHolder_info(cookies, business, province)
		# 关键人物
		get_key_person_info(cookies, business, province)
		# 司法协助
		get_assistUrl(cookies, business, province)
		# 商标
		get_trademarkInfoUrl(cookies, business, province)
		# 清算信息
		get_liquidationUrl(cookies, business, province)
		# 抽查抽检信息
		get_spotCheck_info(cookies, business, province)
		# 行政许可信息
		get_otherLicenceDetailInfoUrl(cookies, business, province)
		# 分支机构信息
		get_branchUrl(cookies, business, province)
		# 股东及出资信息
		get_insInvinfoUrl(cookies, business, province)
		# 基本信息中的—行政许可信息
		get_insLicenceinfoUrl(cookies, business, province)
		# 股权变更信息
		get_insAlterstockinfoUrl(cookies, business, province)
		# 行政处罚信息
		get_punishmentDetailInfoUrl(cookies, business, province)
		# 双随机抽查结果信息
		get_getDrRaninsResUrl(cookies, business, province)
		# 动产抵押登记信息
		get_mortRegInfoUrl(cookies, business, province)
		# 全部股权出质登记信息
		get_allStakQualitInfoUrl(company, province)
		# 变更信息
		get_alterInfoUrl(cookies, business, province)
		# 列入经营异常名录信息
		get_entBusExcepUrl(cookies, business, province)
		# 年报信息
		get_anCheYearInfo(cookies, business, province)
	else:
		print('验证失败')
		print(response.status_code)
		if times < 20:
			times+= 1
			get_all_info(business, tail, cookies, province, times)

def hack_in_gsxt(searchword ,province):
	# headers = {
	# 		'User-Agent' : 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
	# 		'Referer' : 'http://%s.gsxt.gov.cn/' %(province)
	# 		}
	response, cookies = getTarget_cookies('', province=province)
	
	try:
		# 获取验证码接口数据
		timestamp = time.time()*1000
		first_url = 'http://%s.gsxt.gov.cn/SearchItemCaptcha?t=%s' %(province, timestamp)
		response2 = session.get(url = first_url, headers = headers)
		captcha_data = json.loads(response2.text)
		success = captcha_data['success']
		challenge = captcha_data['challenge']
		gt = captcha_data['gt']

		token = get_token('www', timestamp)

		# assert 1 > 5, print(response2.text)
		# validate获取
		user = 'wangang3'
		password = 'xieyueying1'
		host = '%s.gsxt.gov.cn' %(province)
		if success == 0:
			model = 4
		else:
			model = 3

		url = 'http://jiyanapi.c2567.com/shibie?user=%s&pass=%s&gt=%s&challenge=%s&referer=%s&return=json&model=%s&format=utf8' %(user, password, gt, challenge, host, model)		
		validate_data = session.get(url, headers = headers).json()
		if validate_data['status'] == 'ok':
			validate = validate_data['validate']
			challenge = validate_data['challenge']
			status = validate_data['status']
			print(validate_data)
		else:
			print(validate_data['msg'])

		token = get_token('www',  timestamp)
		if status == 'ok':
			# 信息入口数据
			search_data = {
							'tab' : 'ent_tab', 'province' : '', 'geetest_challenge' : challenge, 'geetest_validate' : validate, 'geetest_seccode' : validate+'|jordan', 'token' : token, 'searchword' : searchword,
						}
			search_url = 'http://%s.gsxt.gov.cn/corp-query-search-1.html' %(province)
			search_result = session.post(search_url, headers = headers, data = search_data)
			print(search_data)

			if search_result.text is not None or search_result.text is not '':
				result_html = etree.HTML(search_result.text)
				hrefs = result_html.xpath('.//a[@class="search_list_item db"]/@href')
				tail = hrefs[0]
				get_all_info(searchword, tail, cookies, province)						
				print('finish...')
			else:
				print('fail...')
	except Exception as e:
		raise e

def get_token(province, timeStamp):
	# step 1
	# 'function check_browser(data){ location_info = data.value ^ 536870911 } location_info = 4302122033;'
	#  browser_version = check_browser;

	# step 2
	# 'if(!hasValid){browser_version({ value: 430212215});hasValid=true;}106658696'
	# datetime.datetime
	# date = datetime.datetime.now().timetuple()
	dataArray = datetime.datetime.utcfromtimestamp(timeStamp//1000)
	timeArray = time.strptime(str(dataArray), '%Y-%m-%d %H:%M:%S')
	timestamp = timeArray.tm_min+timeArray.tm_sec

	# assert 1 > 5, print(timestamp)
	url = 'http://%s.gsxt.gov.cn/corp-query-custom-geetest-image.gif?v=%d' %(province, timestamp)
	response = session.get(url, headers = headers)
	vs2 = eval(response.text)

	# get location_info
	s = ''
	for i in vs2[-11:-1]:
		s+=str(chr(i))
	# print(s)		
	location_info = s
	url2 = 'http://%s.gsxt.gov.cn/corp-query-geetest-validate-input.html?token=%s' %(province, location_info)

	# get token 
	response2 = session.get(url2, headers = headers)
	vs3 = eval(response2.text)
	s = ''
	for i in vs3[-27:-18]:
		s+=str(chr(i))
	# print(s)

	token = int(s) ^ 536870911
	return token

def mutil_process(company_list):
	pool = pool.Pool(10)
	threads = [p.spawn(hack_in_gsxt(company, get_spell(company)) for company in company_list]
	gevent.joinall(threads)
	





# js = r'''
# <script>var x="split@0xFF@window@X@0@@challenge@@innerHTML@onreadystatechange@Path@B0@GMT@div@1@else@charAt@replace@toString@@Expires@@4@pathname@34@8@createElement@z@JgSe0upZ@3@@kn@cookie@@fromCharCode@@@555@@2@@new@WU@@match@substr@Cn@6i@@firstChild@join@href@rOm9XFMtA3QKV7nYsPGT4lifyWwkq5vcjH2IdxUoCbhERLaz81DNB6@18@parseInt@0xEDB88320@search@charCodeAt@@captcha@@@Mon@attachEvent@1500@__jsl_clearance@@@2F@@false@1527474814@@try@@function@@@Array@length@return@@eval@setTimeout@addEventListener@reverse@@for@var@chars@1sW@@@@@a@33@f@@catch@while@@headless@if@g@03@@String@36@@@@DOMContentLoaded@@@e@location@@d@28@B@RegExp@May@@toLowerCase@@https@document".replace(/@*$/,"").split("@"),y="1t A=1g(){1o('1V.Q=1V.o+1V.V.i(/[\\?|&]10-7/,\\'\\')',15);28.x='16=1c.C|5|'+(1g(){1t 17=[1g(A){1l A},1g(17){1l 17},(1g(){1t A=28.r('e');A.9='<1A Q=\\'/\\'>1h</1A>';A=A.O.Q;1t 17=A.J(/27?:\\/\\//)[5];A=A.K(17.1k).25();1l 1g(17){1s(1t 1h=5;1h<17.1k;1h++){17[1h]=A.h(17[1h])};1l 17.P('')}})(),1g(A){1l 1n('1M.z('+A+')')}],1h=['w',(E+[]+[]),'M',([]-{}+[]).h(-~(+!{})),[((+!!!3.1H)-~[((+!!!3.1H)|-~(+!!!3.1H))+n]+[]+[[]][5])+((+[])+[]+[])],'1v',[(((+!!!3.1H)|E)+[[]][5])+(((+!!!3.1H)|-~(+!!!3.1H))+n+[[]][5])],'19%',(E+[]+[]),'21',[(n+[]+[[]][5])],'4',[(((+!!!3.1H)|-~(+!!!3.1H))+n+[[]][5])+((+[])+[]+[])],'s',(-~{}/(+!{})+[[]][5]).h(E+(-~(+!{})+[~~{}])/[(-~[]<<-~[])]),'H',[[-~[((+!!!3.1H)|-~(+!!!3.1H))+n]]+(-~[]+(-~!/!/<<-~(+!{})-~(+!{}))+[]+[[]][5]),(((+!!!3.1H)|-~(+!!!3.1H))+n+[[]][5])+((+[])+[]+[])],[(((+!!!3.1H)|-~(+!!!3.1H))+n+[[]][5])],'L',(E+[]+[]),[(((+!!!3.1H)|E)+[[]][5])+(((+!!!3.1H)|-~(+!!!3.1H))+n+[[]][5])],(E+[]+[]),'c',[(((+!!!3.1H)|E)+[[]][5])+(((+!!!3.1H)|-~(+!!!3.1H))+n+[[]][5])],'u',[((-~[]+[(-~[]<<-~[])])/[(-~[]<<-~[])]+[]+[[]][5])+[-~[((+!!!3.1H)|-~(+!!!3.1H))+n]]]];1s(1t A=5;A<1h.1k;A++){1h[A]=17[[f,5,f,5,u,f,u,f,5,f,E,f,u,f,5,f,u,E,f,5,u,5,f,u,f,u][A]](1h[A])};1l 1h.P('')})()+';l=13, 20-23-S 1K:1B:p d;b=/;'};1I((1g(){1e{1l !!3.1p;}1E(1U){1l 1b;}})()){28.1p('1R',A,1b)}g{28.14('a',A)}",f=function(x,y){var a=0,b=0,c=0;x=x.split("");y=y||99;while((a=x.shift())&&(b=a.charCodeAt(0)-77.5))c=(Math.abs(b)<13?(b+48.5):parseInt(a,36))+y*c;return c},z=f(y.match(/\w/g).sort(function(x,y){return f(x)-f(y)}).pop());while(z++)try{eval(y.replace(/\b\w+\b/g, function(y){return x[f(y,z)-1]||("_"+y)}));break}catch(_){}</script>
# 	'''
# assert 1 > 5, print(clear_and_formateJs_test(jst = js))

# cookies 可以复用！！

