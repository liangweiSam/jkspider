# -*- coding:utf-8 -*-
import csv
import xlrd, xlwt
import re

def getDataFromEx():
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

def getshixin_data():
	workBook = xlrd.open_workbook('rmfygg_spider/rmfy_backup.xlsx')
	sheet1_name = workBook.sheet_names()[0]
	sheet1 = workBook.sheet_by_name(sheet1_name)
	rows = sheet1.col_values(8)[2:]
	s = set(rows)
	s = list(s)
	return s

def count():
	total_data = getDataFromEx()
	shixin_data = getshixin_data()
	shixin_dict = {}
	for i in total_data:
		for a in shixin_data:
			if a == i:
				shixin_dict[i] = '有'
				break
			else:
				shixin_dict[i] = '无'
	with open('shixin_file/shixin_count.csv', 'w') as f:
		f_csv = csv.writer(f)
		for k,v in shixin_dict.items():
			f_csv.writerow([k,v])		

if __name__ == '__main__':
	print(len(getshixin_data()))