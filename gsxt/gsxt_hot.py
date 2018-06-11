#-*- coding:utf-8 -*-
from lxml import etree
from gevent.pool import Pool, monkey;monkey.patch_socket()
from retrying import retry

import gevent
import requests
import _pickle as cp
import json
import execjs
import re


class gsxt_hot(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
				'Connection' : 'keep-alive',				
				}
		self.sess = requests.Session()
		self.useful_url = { 	
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
		self.mainContent_url = {
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
		self.useful_url_list = ['spotCheckInfoUrl', 'insInvinfoUrl', 'assistUrl', 'mortRegInfoUrl','insAlterstockinfoUrl','keyPersonUrl', 'IllInfoUrl', 'entBusExcepUrl', 'punishmentDetailInfoUrl',
							 'otherLicenceDetailInfoUrl', 'simpleCancelUrl', 'insProPledgeRegInfoUrl', 'insPunishmentinfoUrl', 'insLicenceInfoNull', 'anCheYearInfo', 'trademarkInfoUrl', 'proPledgeRegInfoUrl', 
							 'branchUrl', 'alterInfoUrl', 'liquidationUrl', 'shareholderUrl', 'insLicenceinfoUrl', 'getDrRaninsResUrl', 'allTrademarkUrl']

		self.mainContent_url_list = ['allAlterInfoUrl', 'allShareHolderDetailInfoUrl', 'allPunishmentInfoUrl', 'allOtherLicenceInfoUrl', 'allMortRegInfoUrl', 'allStakQualitInfoUrl', 'allGtAlterInfoUrl', 'branchUrl']
		self.companys = []

	def parser_page(self, html=None):
		'''
			get api from page
		'''
		html = etree.HTML(html.text)
		if html is not None:
			script = html.xpath('.//div[@id="url"]/script')[0]

			for i in script.xpath('text()')[0].replace('\r', '').replace('\n', '').replace(' ', '').replace(';', '').split('var'):
				# print(i.split('=')[0])
				for url in self.useful_url_list:
					if url == i.split('=')[0]:
						self.useful_url[url] = re.search(r'/%7B.*%7D', i.strip()).group(0)
		else:
			print('html 为空值')

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

	def get_maincontent_url(self, province = 'www', times = 0):
		'''
			return no page website
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['allTrademarkUrl']
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout = 15)
		# response = requests.get(url, headers = headers, cookies = cookies)
		html = etree.HTML(response.text)
		if html is not None:
			script = html.xpath('.//div[@id="url"]/script')[0]
			for i in script.xpath('text()')[0].replace('\r', '').replace('\n', '').replace(' ', '').replace(';', '').split('var'):
				for url in self.mainContent_url_list:
					if url == i.split('=')[0]:
						self.mainContent_url[url] = re.search(r'/%7B.*%7D', i.strip()).group(0)
		else:
			if times < 20:
				times = times + 1
				print('尝试 %d 次' %(times))
				self.get_maincontent_url(cookies, province, times)
			else:
				return
			
	def get_branchUrl(self, company, province='www', times = 0):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['branchUrl']
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout = 15)
		# response = requests.get(url, headers = headers, cookies = cookies)
		try:
			if self.is_json(response.text):
				print('分支机构信息')
				json_data = json.loads(response.text)
				datas = json_data['data']
				if datas is not None:
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
					# print(branch_infos)	
					# self.insert_into_db('branch_info', branch_infos)
					branch = {'tablename' : 'branch_info', 'data' : branch_infos}
					return branch
			else:    
				if times < 20:
					times+= 1
					return self.get_branchUrl(company, province, times)
				else:
					print('%s---超过限定次数----.' %(company))
		except Exception as e:
			print('%s---分支机构信息----%s.' %(e, company))
			# print('---分支机构信息----Error.')
			# print(e)
			# return	
	
	def get_allStakQualitInfoUrl(self, company, province='www', times=0):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['allStakQualitInfoUrl']
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout = 15)
		try:
			if self.is_json(response.text):
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
					# print(stakQualit_infos)
					# self.insert_into_db('stakQualit_infos', stakQualit_infos)
					stakQualit = {'tablename' : 'stakQualit_infos', 'data' : stakQualit_infos}
					return stakQualit
			else:
				if times < 20:
					times+= 1
					return self.get_allStakQualitInfoUrl(company. province, times)
				else:
					print('%s---超过限定次数---' %(company))
		except Exception as e:
			print('%s---股权出质登记信息---%s' %(e, company))
			# print('----股权出质登记信息----Error.')
			# print(e)
			# return
			
	def get_getDrRaninsResUrl(self, company, province='www', times = 0):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['getDrRaninsResUrl']
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout = 15)	
		try:
			if self.is_json(response.text):
				print('双随机抽查结果信息')
				json_data = json.loads(response.text)
				datas = json_data['data']
				if datas is not None:
					# 分页查询
					if json_data['totalPage'] > 1:
						for i in range(i, int(json_data['totalPage'])):
							# new_url = 'http://%s.gsxt.gov.cn' %(province)+detail_url+'?draw=%s&start=%s&length=%s&_=%s' %(i+1, i*5, 5, time.time()*1000)
							form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
							response2 = self.session.get(url, headers = self.headers, data = form_data, proxies = self.proxy, timeout = 15)
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
						getDrRanins_info['details'] = self.get_getDrRanins_details(data['url'], province)
						getDrRanins_info['full_name'] = company
						getDrRanins_infos.append(getDrRanins_info)
					# print(getDrRanins_infos)
					# self.insert_into_db('getDrRanins_info', getDrRanins_infos)
					DrRanins = {'tablename' : 'getDrRanins_info', getDrRanins_infos}
					return 	DrRanins					
		except Exception as e:
			print('%s---双随机抽查结果信息---%s' %(company, e))
			# print('---双随机抽查结果信息----Error.')
			# print(e)
			# return

	def get_getDrRanins_details(self, detail_url, province='www', times = 0):
		url = 'http://%s.gsxt.gov.cn' %(province)+detail_url
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		# response = requests.get(url, headers = headers, cookies = cookies)
		try:
			# 检查json格式
			if self.is_json(response.text):
				print('---双随机抽查结果信息详情---')
				json_data = json.loads(response.text)
				datas = json_data['data']
				if datas is not None:
					# 分页查询
					if json_data['totalPage'] > 1:
						for i in range(i, int(json_data['totalPage'])):
							new_url = 'http://%s.gsxt.gov.cn' %(province)+detail_url+'?draw=%s&start=%s&length=%s&_=%s' %(i+1, i*5, 5, time.time()*1000)
							response2 = self.session.get(new_url, headers = self.headers, proxies = self.proxy, timeout=15)
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
			print('---双随机抽查结果信息---%s' %(e))
			# print('---双随机抽查结果信息详情----Error.')
			# print(e)
			# return
			
	def get_insAlterstockinfoUrl(self, company, province='www', times = 0):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['insAlterstockinfoUrl']
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		try:
			if self.is_json(response.text):
				print('股权变更信息')
				json_data = json.loads(response.text)
				datas = json_data['data']
				if datas is not None:
					if json_data['totalPage'] > 1:
						for i in range(1, int(json_data['totalPage'])):
							form_data = {'draw' : i+1, 'start' : i*5, 'length' : 5}
							response2 = self.session.post(url, headers = self.headers, data = form_data, proxies = self.proxy, timeout=15)
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
					# print(insAlterstock_infos)
					# self.insert_into_db('insAlterstock_info', insAlterstock_infos)
					insAlter = {'tablename' : 'insAlterstock_info', 'data' : insAlterstock_infos}
					return insAlter
			else:
				if times < 30:
					times = times + 1
					print('try : %s ' %(times))
					return self.get_insAlterstockinfoUrl(company, province, times)
				else:
					print('%s---超过限定次数---' %(company))	
		except Exception as e:
			print('%s---股权变更信息---%s' %(e, company))	
			# print('---股权变更信息----Error.')
			# print(e)
			# return
			
	def get_anCheYearInfo(self, company, province='www', times = 0):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['anCheYearInfo']
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
					anCheYear_Info['details'] = self.get_anCheYearInfo_detail(data['anCheId'], province)
					anCheYear_Info['full_name'] = company
					anCheYear_Infos.append(anCheYear_Info)				
				# print(anCheYear_Infos)
				# self.insert_into_db('anCheYear_info', anCheYear_Infos)
				ancheYear = {'tablename' : 'anCheYear_info', 'data' : anCheYear_Infos}
				return ancheYear
		except Exception as e:
				if times < 30:
					times = times + 1
					print('try : %s ' %(times))
					return self.get_anCheYearInfo(company, province, times)		
				else:
					print('%s---超过限定次数---%s' %(e, company))
				# print('---年报信息---, 爬取失败..')
	
	def get_anCheYearInfo_detail(self, anCheId, province='www'):
		info_type = ['corp-query-entprise-info-annualAlter-', 'corp-query-entprise-info-AnnSocsecinfo-',
					'corp-query-entprise-info-baseinfo-', 'corp-query-entprise-info-sponsor-', 'corp-query-entprise-info-vAnnualReportBranchProduction-',
					'corp-query-entprise-info-webSiteInfo-', 'corp-query-entprise-info-forGuaranteeinfo-']
		all_details = []
		try:
			all_details.append(self.get_anCheYearInfo_sponsor(anCheId, province))
			all_details.append(self.get_anCheYearInfo_baseinfo(anCheId, province))
			all_details.append(self.get_anCheYearInfo_AnnSocsecinfo(anCheId, province))
			all_details.append(self.get_vAnnualReportBranchProduction(anCheId, province))
			return all_details	
		except Exception as e:
			print('%s---年报信息详情---%s' %(e, company))

	def get_anCheYearInfo_baseinfo(self, anCheId, province='www'):
		ty = 'corp-query-entprise-info-baseinfo-'
		url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
		details = {}
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
			print('年报-基本信息 %s' %(e))

	def get_anCheYearInfo_sponsor(self, anCheId, province='www'):
		ty = 'corp-query-entprise-info-sponsor-'
		url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
		details = {}
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
			print('年报-股东及出资信息 %s' %(e))

	def get_anCheYearInfo_AnnSocsecinfo(self, anCheId, province='www'):
		ty = 'corp-query-entprise-info-AnnSocsecinfo-'
		url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
		details = {}
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
			print('年报-社保信息 %s' %(e))

	def get_vAnnualReportBranchProduction(self, anCheId, province='www'):
		ty = 'corp-query-entprise-info-vAnnualReportBranchProduction-'
		url = 'http://%s.gsxt.gov.cn/' %(province)+ty+anCheId+'.html'
		details = {}
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
			if response.text is not None:
				json_data = json.loads(response.text)
				if json_data['data'] is not None and len(json_data['data']) > 0:
					datas = json_data['data'][0]
					details['title'] = '企业资产状况信息'
					# 资产总额
					details['assGro'] = datas['assGro']
					# 资产总额是否公示  公示：1 不公示：！1
					details['assGroDis'] = datas['assGroDis']
					# 负债总额
					details['liaGro'] = datas['liaGro']
					# 负债总额是否公示 
					details['liaGroDis'] = datas['liaGroDis']
					# 主营业务
					details['maiBusInc'] = datas['maiBusInc']
					# 主营业务是否公示
					details['maiBusIncDis'] = datas['maiBusIncDis']
					# 净利润
					details['netInc'] = datas['netInc']
					# 净利润是否公示
					details['netIncDis'] = datas['netIncDis']
					# 利润总额
					details['proGro'] = datas['proGro']
					# 利润总额是否公示
					details['proGroDis'] = datas['proGroDis']
					# 纳税总额
					details['ratGro'] = datas['ratGro']
					# 纳税总额是否公示
					details['ratGroDis'] = datas['ratGroDis']
					# 所有者权益合计
					details['totEqu'] = datas['totEqu']
					# 营业总收入
					details['vendInc'] = datas['vendInc']
					# 营业总收入是否公示
					details['vendIncDis'] = datas['vendIncDis']
					return details
		except Exception as e:
			print('企业资产状况信息 %s' %(e))	
			
	def get_entBusExcepUrl(self, company, province='www', times = 0):
		maxtimes = 30
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['entBusExcepUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		try:
			print('列入经营异常名录信息：')
			if self.is_json(response.text):
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
					# print(entBusExcep_infos)
					# self.insert_into_db('entBusExcep_info', entBusExcep_infos)
					entBus = {'tablename' : 'entBusExcep_info', 'data' : entBusExcep_infos}
					return entBus
				else:
					if times < maxtimes:
						times = times + 1
						time.sleep(0.2)
						return self.get_entBusExcepUrl(company, province, times)
					else:
						print('数据为None---经营异常名录信息---超过尝试次数--%s' %(company))
			else:
				if times < maxtimes:
					times = times + 1
					time.sleep(0.2)
					print('非json ---经营异常名录信息--- trying %d..%s' %(times, company))
					return self.get_entBusExcepUrl(company, province, times)
				else:
					print('访问失败---超过尝试次数---%s' %(company))
					# print('访问失败,次数：%d！！' %(times))
		except Exception as e:
			print('%s---列入经营异常名录信息---%s' %(e, company))
			# print('---列入经营异常名录信息---')
			# print(e)
	
	def get_mortRegInfoUrl(self, company, province='www'):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['allMortRegInfoUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
					mort_reg_info['details'] = self.mortreg_detail_info(data['morReg_Id'])
					mort_reg_info['full_name'] = company
					mort_reg_infos.append(mort_reg_info)
				# self.insert_into_db('mort_reg_info', mort_reg_infos)
				# print(mort_reg_infos)
				mort = {'tablename' : 'mort_reg_info', 'data' : mort_reg_infos}
				return mort
		except Exception as e:
			print('%s---动产抵押登记信息---%s' %(e, company))
			# print('---动产抵押登记信息---')
			# print(e)

	def mortreg_detail_info(self, morReg_Id, province='www'):
		info_type = ['corp-query-entprise-info-mortregpersoninfo-', 'corp-query-entprise-info-mortCreditorRightInfo-',
					'corp-query-entprise-info-mortGuaranteeInfo-', 'corp-query-entprise-info-getMortAltItemInfo-',
					'corp-query-entprise-info-getMortRegCancelInfo-']
		details = {}
		try:
			for ty in info_type:
				url = 'http://%s.gsxt.gov.cn/' %(province)+ty+morReg_Id+'.html' 
				response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)	
				if response.text is not None:
					print('details . . . . ')
					json_data = json.loads(response.text)
					details[ty[25:-1]] = json_data['data']
			return details
		except Exception as e:
			print('%s---动产抵押详情---%s' %(e))
			# print('动产抵押详情, 爬取失败.....')
		
	def get_insInvinfoUrl(self, company, province='www'):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['insInvinfoUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		json_data = json.loads(response.text)
		ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
		try:
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
				# print(insInv_infos)
				# self.insert_into_db('insInv_info', insInv_infos)
				insInv = {'tablename' : 'insInv_info', 'data' : insInv_infos}
				return insInv
		except Exception as e:
			print('%s--股东及出资信息--%s' %(e, company))
		
	def get_insLicenceinfoUrl(self, company, province='www'):
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['insLicenceinfoUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
			# print(insLicenceinfos)
			# self.insert_into_db('insLicence_info', insLicenceinfos)
			insLicence = {'tablename' : 'insLicence_info', 'data' : insLicenceinfos}
			return insLicence
		except Exception as e:
			print('%s---基本信息中的—行政许可信息---%s' %(e, company))
			# print(e)
	
	def get_spotCheck_info(self, company, province='www'):

		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['spotCheckInfoUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		try:
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
			# print(spotChecks)
			# self.insert_into_db('spotCheck_info', spotChecks)
			spotCheck = {'tablename' : 'spotCheck_info', 'data' : spotChecks}
			return spotCheck
		except Exception as e:
			print('%s---抽查抽检信息---%s' %(e, company))
		
	def get_shareHolder_info(self, company, province='www', times=0):
		'''
			get shareHolder_info from shareHolderUrl
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['allShareHolderDetailInfoUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		try:
			if self.is_json(response.text):
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
				# print(shareholders)
				# self.insert_into_db('shareholder_info', shareholders)
				shareholder = {'tablename' :'shareholder_info', 'data' : shareholders}
				return shareholder
			else:
				if times < 20:
					times+= 1
					time.sleep(0.5)
					return self.get_shareHolder_info(company, province, times)
				else:
					print('---股东---尝试次数过多！%s' %(company))
		except Exception as e:
			print('%s---股东---%s' %(e,company))
		
	def get_key_person_info(self, company, province='www'):
		'''
			parser key_person_info
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['keyPersonUrl'] 
		# assert 1>5, 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		try:
			if self.is_json(response.text):
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
				# self.insert_into_db('keyperson_info', names)
				keyperson = {'tablename' : 'keyperson_info', 'data' : names}
				return keyperson
		except Exception as e:
			print('%s---关键人物--- %s' %(e, company))
		
	def get_otherLicenceDetailInfoUrl(self, company, province='www'):
		'''
			parser otherLicenceDetailInfo
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['allOtherLicenceInfoUrl']
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
			json_data = json.loads(response.text)
			datas = json_data['data']
			ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
			print('行政许可信息:')
			if json_data['data'] is not None:

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
				# print(other_licence_infos)
				# self.insert_into_db('other_licence_info', other_licence_infos)	
				otherLicence = {'tablename' : 'other_licence_info', 'data' : other_licence_infos}
				return otherLicence
		except Exception as e:
			print('%s---行政许可信息---%s' %(e, company))
	
	def get_liquidationUrl(self, company, province='www'):
		'''
			parser liquidation
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['liquidationUrl'] 
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
			# print(liqs)
			# self.insert_into_db('liquidation_info', liqs)
			liquidation = {'tablename' : 'liquidation_info', 'data' : liqs}
			return liquidation
		except Exception as e:
			print('%s---清算信息---%s' %(e, company))

	def get_alterInfoUrl(self, company, province='www', times = 0):
		'''
			parser alterInfo
		'''

		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['allAlterInfoUrl'] 
		response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
		try:
			total_data = response.text
			if self.is_json(total_data):
				total_data = json.loads(total_data)
				datas = total_data['data']
				if datas is not None:
					print('变更信息 :')
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
					# print(altDatas)
					# self.insert_into_db('alter_info', altDatas)
					alterinfo = {'tablename' : 'alter_info'}
					return alterinfo
				else:
					if times < maxtimes:
						times = times + 1
						time.sleep(0.2)
						print('变更信息 :trying %d..' %(times))
						return self.get_alterInfoUrl(cookies, company, province, times)
					else:
						print('--变更信息--尝试次数过多--%s' %(company))
						# print('访问失败,次数：%d！！' %(times))
			else:
				if times < 30:
					times = times + 1
					time.sleep(0.2)
					print('非json 变更信息 :trying %d..' %(times))
					return self.get_alterInfoUrl(cookies, company, province, times)
				else:
					print('非json--变更信息--尝试次数过多')		
		except Exception as e:
			print('--变更信息--%s' %(e))
	
	def get_trademarkInfoUrl(self, company, province='www'):
		'''
			parser trademark
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['trademarkInfoUrl']
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
			total_data = response.json()
			datas = total_data['data']
			ctx = re.compile(r'<(span|div) class="dp">(.*?)</(span|div)>')
			if  datas is not None:
				print('商标信息:')
				for i in range(1, total_data['totalPage']):
					responses = self.session.get(url+'?start=%d' %(i*4), headers = self.headers, proxies = self.proxy, timeout=15)
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
				# print(trade_marks)
				# self.insert_into_db('trademark_info', trade_marks)
				trademark = {'tablename':'trademark_info', 'data': trade_marks}
				return trademark
		except Exception as e:
			print('%s---商标信息--- %s' %(e, company))

			
	def get_punishmentDetailInfoUrl(self, company, province='www'):
		'''
			parser punishmentDetailInfoUrl
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.mainContent_url['allPunishmentInfoUrl']
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
			if self.is_json(response.text):
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
					# print(punishment_infos)
					# self.insert_into_db('punishment_info', punishment_infos)
					punishment = {'tablename' : 'punishment_info', 'data' : punishment_infos}
					return punishment
		except Exception as e:
			print('%s---行政处罚信息---%s' %(e, company))
		
	def get_assistUrl(self, company, province='www'):
		'''
			parser assistUrl
		'''
		url = 'http://%s.gsxt.gov.cn' %(province)+self.useful_url['assistUrl'] 
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
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
				assist['details'] = get_assistUrl_details(data['parent_Id'], province)
				assist['full_name'] = company
				assists.append(assist)
				# print(assist)
			# self.insert_into_db('assist_info', assists)
			assist_info = {'tablename' : 'assist_info', 'data' : assist}
			return assist_info
		except Exception as e:
			print('%s---司法协助信息--- %s' %(e, company))
		
	def get_assistUrl_details(self, parent_Id, province='www'):
		'''
			details of assistUrl
		'''
		url = 'http://%s.gsxt.gov.cn/corp-query-entprise-info-judiciaryStockfreeze-%s.html' %(province, parent_Id)
		try:
			response = self.session.get(url, headers = self.headers, proxies = self.proxy, timeout=15)
			if self.is_json(response.text):
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
		except Exception as e:
			print('%s---司法协助详细信息---%s' %(e, company))

	def parser_business_license_info(self, html = None):
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
				data = []
				data.append(business_license_info)
				base_info = {'tablename' : 'business_license_info', 'data' : data}
				return base_info
				# self.insert_into_db('business_license_info', data)
				# print(business_license_info)
			else:
				print('---基本信息---')

	def clear_and_formateJs(self, jst, times = 0):
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
				rex = re.compile(r'setTimeout.*\d{1,4}\);')
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

				rex8 = re.compile(r"return cookie};(.*)", flags = re.MULTILINE)
				rex9 = re.compile(r"return cookie};\n.*", flags = re.MULTILINE)
				# 清理未定义的Windows
				s = s.replace("window['__p' + 'hantom' + 'as']", "undefined")
				s = s.replace("window['_p' + 'hantom']", "undefined")
				s = s.replace('window.headless', 'undefined')
				s = s.replace(r"window['callP' + 'hantom']", "undefined")

				s = s.replace("window['__p'+'hantom'+'as']", "undefined")
				s = s.replace("window['_p'+'hantom']", "undefined")
				s = s.replace('window.headless', 'undefined')
				s = s.replace(r"window['callP'+'hantom']", "undefined")

				s = s.replace("D.headless", "undefined")
				s = re.sub(rex8, 'return cookie};', s)
				s = re.sub(rex9, 'return cookie};', s)
				s = s + '\n function ssss(){ return %s() }' %(functionName)
				ctx_2 = execjs.compile(s)
				cookies = ctx_2.call('ssss')
				return cookies
			else:
				if times < 20:
					times = times + 1
					return self.clear_and_formateJs(jst=jst, times=times)
		except Exception as e:
			# with open('../512Error/%s.html' %(time.time()), 'w', encoding='utf-8') as f:
			# 	f.write(js.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			# 	f.write(cat.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			# 	f.write(s.encode('utf-8', 'ignore').decode('utf-8', 'ignore')+'\n')
			if times < 5:
				times = times + 1
				return self.clear_and_formateJs(jst=jst, times=times)
			else:
				print('---整理Js---%s' %(e))		

	def set_sess(self):
		url = 'http://www.gsxt.gov.cn/corp-query-entprise-info-hot-search-list.html?province=100000'
		response = self.sess.get(url, headers = self.headers)
		encry_cookies = self.clear_and_formateJs(response.text).split(';')

		name, value = encry_cookies[0].split('=', 1)
		self.sess.cookies[name] = value
		response2 = self.sess.get(url, headers = self.headers)
		if response2.status_code == 200:

			html = etree.HTML(response2.text)
			ul = html.xpath('.//div[@id="day_div"]/ul')[0]
			for li in ul.xpath('.//li'):
				a = li.xpath('a/@href')[0]
				company = li.xpath('a/div/text()')[0]
				company_dict = {}
				company_dict['href'] = a
				company_dict['company'] = company
				self.companys.append(company_dict)

	def scrapy_list(self):
		self.set_sess()
		p = Pool(10)
		thread = [p.spawn(self.get_allinfo, dic) for dic in companys]
		gevent.joinall(thread)

	@retry(stop_max_attemp_number = 5, retry_on_result = len_is_zero)
	def get_allinfo(self, dic):
		print('start: %s' %(dic['company']))
		url = 'http://www.gsxt.gov.cn' + tail

		try:
			response = self.sess.get(url, headers = self.headers, timeout = 20)
			if response.status_code == 200:
				html = etree.HTML(response.text)
				if len(html.xpath('.//div[@id="url"]/script')) > 0:
					return 
				# 取得大量Url	
				self.parser_page(response)
				# 取得免分页的信息
				self.get_maincontent_url()
				# 基本信息
				self.parser_business_license_info(response)
				# 股东
				self.get_shareHolder_info(business, province)
				# 关键人物
				self.get_key_person_info(business, province)
				# 司法协助
				self.get_assistUrl(business, province)
				# 商标
				self.get_trademarkInfoUrl(business, province)
				# 清算信息
				self.get_liquidationUrl(business, province)
				# 抽查抽检信息
				self.get_spotCheck_info(business, province)
				# 行政许可信息
				self.get_otherLicenceDetailInfoUrl(business, province)
				# 分支机构信息
				self.get_branchUrl(business, province)
				# 股东及出资信息
				self.get_insInvinfoUrl(business, province)
				# 基本信息中的—行政许可信息
				self.get_insLicenceinfoUrl(business, province)
				# 股权变更信息
				self.get_insAlterstockinfoUrl(business, province)
				# 行政处罚信息
				self.get_punishmentDetailInfoUrl(business, province)
				# 双随机抽查结果信息
				self.get_getDrRaninsResUrl(business, province)
				# 动产抵押登记信息
				self.get_mortRegInfoUrl(business, province)
				# 全部股权出质登记信息
				self.get_allStakQualitInfoUrl(business, province)
				# 变更信息
				self.get_alterInfoUrl(business, province)
				# 列入经营异常名录信息
				self.get_entBusExcepUrl(business, province)
				# 年报信息
				self.get_anCheYearInfo(business, province)
		except Exception as e:
			raise e

	def len_is_zero(self, result):
		return result is None

	def progress_dump(self, company, status):
		l = []
		try:
			with open('progress.txt', 'rb') as f:
				l = cp.load(f)
		except Exception as e:
			print(e)
		dit = {'company' : company, 'status' : status}
		l.append(dit)
		with open('progress.txt', 'wb+') as f:
			cp.dump(l, f)

	def progress_load(self):
		with open('progress.txt', 'rb') as f:
			print(cp.load(f))


if __name__ == '__main__':
	hot = gsxt_hot()
	hot.progress_dump('bbbb', 'error')
	hot.progress_load()




