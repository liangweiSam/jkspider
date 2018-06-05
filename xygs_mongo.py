#-*-coding:utf-8-*-
from pymongo import MongoClient
import pandas as pd
import json
import csv
import os


class xygs_mongo(object):

	def __init__(self):
		self.conn = MongoClient('127.0.0.1', 27017)
		self.flag = 0

	def get_data(self,  company):
		db = self.conn.jkspider
		# 变更信息
		alter_info = []
		for a in db['alter_info'].find({'full_name' : company}, {'_id' : 0}):
			alter_info.append(a)	
		# 司法协助
		assist_info = []
		for a in db['assist_info'].find({'full_name' : company}, {'_id' : 0}):
			assist_info.append(a)
		# 基本信息
		business_license_info = []
		for a in db['business_license_info'].find({'full_name' : company}, {'_id' : 0}):
			business_license_info.append(a)
		# 列入经营异常名录信息
		entBusExcep_info = []
		for a in db['entBusExcep_info'].find({'full_name' : company}, {'_id' : 0}):
			entBusExcep_info.append(a)
		# 双随机抽查结果信息
		getDrRanins_info = []
		for a in db['getDrRanins_info'].find({'full_name' : company}, {'_id' : 0}):
			getDrRanins_info.append(a)
		# 股权变更信息
		insAlterstock_info = []
		for a in db['insAlterstock_info'].find({'full_name' : company}, {'_id' : 0}):
			insAlterstock_info.append(a)
		# 股东及出资信息
		insInv_info = []
		for a in db['insInv_info'].find({'full_name' : company}, {'_id' : 0}):
			insInv_info.append(a)
		# 基本信息中的—行政许可信息
		insLicence_info = []
		for a in db['insLicence_info'].find({'full_name' : company}, {'_id' : 0}):
			insLicence_info.append(a)
		# 关键人物
		keyperson_info = []
		for a in db['keyperson_info'].find({'full_name' : company}, {'_id' : 0}):	
			keyperson_info.append(a)
		# 动产抵押登记信息
		mort_reg_info =[]
		for a in db['mort_reg_info'].find({'full_name' : company}, {'_id' : 0}):
			mort_reg_info.append(a)
		# 行政许可信息
		other_licence_info = []
		for a in db['other_licence_info'].find({'full_name' : company}, {'_id' : 0}):
			other_licence_info.append(a)
		# 行政处罚信息
		punishment_info = []
		for a in db['punishment_info'].find({'full_name' : company}, {'_id' : 0}):
			punishment_info.append(a)
		# 股东
		shareholder_info = []
		for a in db['shareholder_info'].find({'full_name' : company}, {'_id' : 0}):
			shareholder_info.append(a)
		# 抽查抽检信息
		spotCheck_info = []
		for a in db['spotCheck_info'].find({'full_name' : company}, {'_id' : 0}):
			spotCheck_info.append(a)
		# 股权出质登记信息
		stakQualit_infos = []
		for a in db['stakQualit_infos'].find({'full_name' : company}, {'_id' : 0}):
			stakQualit_infos.append(a)
		# 商标信息	
		trademark_info = []
		for a in db['trademark_info'].find({'full_name' : company}, {'_id' : 0}):
			trademark_info.append(a)
		return {'变更信息':alter_info, '司法协助':assist_info, '基本信息':business_license_info, '列入经营异常名录信息':entBusExcep_info,
				'双随机抽查结果信息':getDrRanins_info, '股权变更信息':insAlterstock_info,'股东及出资信息':insInv_info,'基本信息中的—行政许可信息':insLicence_info,
				'关键人物':keyperson_info,'动产抵押登记信息':mort_reg_info,'行政许可信息':other_licence_info,'行政处罚信息':punishment_info,
				'股东':shareholder_info,'抽查抽检信息':spotCheck_info,'股权出质登记信息':stakQualit_infos,'商标信息':trademark_info}

	def get_totalC(self):
		totalC = self.conn.jkspider['business_license_info'].find({}, {'full_name':1, '_id':0})
		company_l = []
		for i in totalC:
			company_l.append(i['full_name'])
		return company_l

	def parse_data(self, company):
		print(company)
		companys = self.get_data(company)
		company_name = company
		alter_count = len(companys['变更信息'])
		assist_count = len(companys['司法协助'])
		businsess_info_count = len(companys['基本信息'])
		entBusExcep_count = len(companys['列入经营异常名录信息'])
		getDrRanins_count = len(companys['双随机抽查结果信息'])
		insAlterstock_count = len(companys['股权变更信息'])
		insInv_count = len(companys['股东及出资信息'])
		insLicense_count = len(companys['基本信息中的—行政许可信息'])
		keyperson_count = len(companys['关键人物'])
		mort_reg_count = len(companys['动产抵押登记信息'])
		other_licence_count = len(companys['行政许可信息'])
		punishment_count = len(companys['行政处罚信息'])
		shareholder_count = len(companys['股东'])
		spotCheck_count = len(companys['抽查抽检信息'])
		stakQualit_count = len(companys['股权出质登记信息'])
		trademake = len(companys['商标信息'])


		data = [company_name, alter_count,assist_count, businsess_info_count, entBusExcep_count, getDrRanins_count,
				insAlterstock_count, insInv_count, insLicense_count, keyperson_count, mort_reg_count, other_licence_count, punishment_count,
				shareholder_count, spotCheck_count, stakQualit_count, trademake]
		headers = ['公司名称', '变更信息', '司法协助', '基本信息', '列入经营异常名录信息', '双随机抽查结果信息', '股权变更信息', '股东及出资信息',
					'基本信息中的—行政许可信息', '关键人物', '动产抵押登记信息', '行政许可信息', '行政处罚信息', '股东', '抽查抽检信息',
					'股权出质登记信息', '商标信息']
		if os.path.exists('xygs_file') is False:
			os.mkdir('xygs_file')					
		with open('xygs_file/parse_data.csv', 'a+') as f:
			f_csv = csv.writer(f)
			if self.flag == 0:
				f_csv.writerow(headers)
				self.flag+=1
			f_csv.writerow(data)

	def json2csv(self, company):
		print(company)
		data = self.get_data(company)
		if os.path.exists('xygs_file') is False:
			os.mkdir('xygs_file')
		with open('xygs_file/%s.csv' %(company), "w") as csvFile:
			csvWriter = csv.writer(csvFile)
			for k,v in data.items():
				csvWriter.writerow([k,v])
		# data = json.loads(str(data))
		# df = pd.read_json(data)
		# df.to_csv('%s.csv' %(company))



					


if __name__ == '__main__':
	xy = xygs_mongo()
	for i in xy.get_totalC():
		xy.parse_data(i) 	

	# xy.json2csv('哈尔滨泰富电气有限公司')
