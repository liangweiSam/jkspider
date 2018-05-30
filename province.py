#-*- coding:utf-8-*-
from concurrent import futures

province = {
			'北京' : 'bj', '上海' : 'sh', '天津' : 'tj', '重庆' : 'cq',
			'河北' : 'he', '山西' : 'sx', '内蒙' : 'nm', '黑龙江' : 'hl',
			'吉林' : 'jl', '辽宁' : 'ln', '陕西' : 'sn', '甘肃' : 'gs',
			'青海' : 'qh', '新疆' : 'xj', '宁夏' : 'nx', '山东' : 'sd',
			'河南' : 'ha', '江苏' : 'js', '浙江' : 'zj', '安徽' : 'ah',
			'江西' : 'jx', '福建' : 'fj', '台湾' : 'tw', '湖北' : 'hb',
			'湖南' : 'hn', '广东' : 'gd', '广西' : 'gx', '海南' : 'hi',
			'四川' : 'sc', '云南' : 'yn'	, '贵州' : 'gz', '西藏' : 'xz'
			}

# 广东
gd_city = ['广州', '深圳','珠海','汕头','佛山','韶关','湛江','肇庆','江门','茂名','惠州','梅州','汕尾','河源','阳江','清远','东莞','中山','潮州','揭阳','云浮', 'gd']

# 河北
he_city = ['石家庄', '唐山', '秦皇岛', '邯郸', '邢台', '保定', '张家口', '承德', '沧州', '廊坊', '衡水', 'he']

# 山西
sx_city = ['太原', '大同', '阳泉', '长治', '晋城', '朔州', '忻州', '吕梁', '晋中', '临汾', '运城', 'sx']

# 内蒙
nm_city = ['呼和浩特', '包头', '乌海', '赤峰', '呼伦贝尔', '通辽', '乌兰察布', '鄂尔多斯', '巴彦淖尔', 'nm']

# 辽宁
ln_city = ['沈阳', '大连', '鞍山', '抚顺', '本溪', '丹东', '锦州', '营口', '阜新', '辽阳', '盘锦', '铁岭', '朝阳', '葫芦岛', 'ln']

# 吉林
jl_city = ['长春', '吉林', '四平', '辽源', '通化', '白山', '白城', '松原', 'jl']

# 黑龙江
hl_city = ['哈尔滨', '齐齐哈尔', '牡丹江', '佳木斯', '大庆', '伊春', '鸡西', '鹤岗', '双鸭山', '七台河', '绥化', '黑河', 'hl']

# 江苏
js_city = ['南京', '无锡', '徐州', '常州', '苏州', '南通', '连云港', '淮安', '盐城', '扬州', '镇江', '泰州', '宿迁', 'js']

# 浙江
zj_city = ['杭州', '宁波', '温州', '绍兴', '湖州', '嘉兴', '金华', '衢州', '台州', '丽水', '舟山', 'zj']

# 安徽
ah_city = ['合肥', '芜湖', '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '阜阳', '宿州', '滁州', '六安', '宣城', '池州', '亳州', 'ah']

# 福建
fj_city = ['福州', '莆田', '泉州', '厦门', '漳州', '龙岩', '三明', '南平', '宁德', 'fj']

# 江西
jx_city = ['南昌', '赣州', '宜春', '吉安', '上饶', '抚州', '九江', '景德镇', '萍乡', '新余', '鹰潭', 'jx']

# 山东
sd_city = ['济南', '青岛', '淄博', '枣庄', '东营', '烟台', '潍坊', '济宁', '泰安', '威海', '日照', '滨州', '德州', '聊城', '临沂', '菏泽', '莱芜', 'sd']

# 河南
hi_city = ['郑州', '开封', '洛阳', '平顶山', '安阳', '鹤壁', '新乡', '焦作', '濮阳', '许昌', '漯河', '三门峡', '商丘', '周口', '驻马店', '南阳', '信阳', 'hi']

# 湖北
hb_city = ['武汉', '黄石', '十堰', '荆州', '宜昌', '襄阳', '鄂州', '荆门', '黄冈', '孝感', '咸宁', '随州', 'hb']

# 湖南
hn_city = ['长沙', '株洲', '湘潭', '衡阳', '邵阳', '岳阳', '张家界', '益阳', '常德', '娄底', '郴州', '永州', '怀化', 'hn']

# 广西
gx_city = ['南宁', '柳州', '桂林', '梧州', '北海', '崇左', '来宾', '贺州', '玉林', '百色', '河池', '钦州', '防城港', '贵港', 'gx']

# 海南
hi_city = ['海口', '三亚', '三沙', '儋州', 'hi']

# 四川
sc_city = ['成都', '绵阳', '自贡', '攀枝花', '泸州', '德阳', '广元', '遂宁', '内江', '乐山', '资阳', '宜宾', '南充', '达州', '雅安', '广安', '巴中', '眉山', 'sc']

# 贵州
gz_city = ['贵阳', '六盘水', '遵义', '铜仁', '毕节', '安顺', 'gz']

# 云南
yn_city = ['昆明', '昭通', '曲靖', '玉溪', '普洱', '保山', '丽江', '临沧', 'yn']

# 西藏
xz_city = ['拉萨', '日喀则', '昌都', '林芝', '山南', '那曲', 'xz']

# 陕西
sn_city = ['西安', '铜川', '宝鸡', '咸阳', '渭南', '汉中', '安康', '商洛', '延安', '榆林', 'sn']

# 甘肃
gs_city = ['兰州', '嘉峪关', '金昌', '白银', '天水', '酒泉', '张掖', '武威', '定西', '陇南', '平凉', '庆阳', 'gs']

# 青海
qh_city = ['西宁', '海东', 'qh']

# 宁夏
nx_city = ['银川', '石嘴山', '吴忠', '固原', '中卫', 'nx']

# 新疆
xj_city = ['乌鲁木齐', '克拉玛依', '吐鲁番', '哈密', 'xj']

city_collections = [gd_city, he_city, sx_city, nm_city, ln_city, jl_city, 
					hl_city, js_city, zj_city, ah_city, fj_city, jx_city, 
					sd_city, hi_city, hb_city, hn_city, gx_city, hi_city, 
					sc_city, gz_city, yn_city, xz_city, sn_city, sn_city,
					gs_city, qh_city, nx_city, xj_city]


# sss = '''
# 乌鲁木齐市	
# 克拉玛依市
# 吐鲁番市	哈密市	
# '''
# print(sss.replace('\n', '').replace('\t', '').split('市')[:-1])

def search_city(searchword, city_collection):
	for city in city_collection:
		if city in searchword:
			province_is = city_collection[-1]
			return province_is

def get_spell(searchword):
	result = ''
	for i in list(province.keys()):
		if i in searchword:
			result = province[i]

	if result is None or result.strip() is '':
		with futures.ThreadPoolExecutor(max_workers = 5) as executor:
			citys = [executor.submit(search_city, searchword, c) for c in city_collections]
			# citys = dict((executor.submit(search_city, searchword, c), c) for c in city_collections)
			for future in futures.as_completed(citys):
				if future.result() is not None:
					result = future.result()

	if result.strip() is '' or result is None:
		result = 'www'
		return result
	else:
		return result
	# if result is None or result.strip() is '':
	# 	print('CITY')
	# 	p = pool.Pool(5)
	# 	threads = [p.spawn(search_city(searchword, i)) for i in city_collections]
	# 	gevent.joinall(threads)
			

sss = '''佛山市维格家具制造有限公司
加特可（广州）自动变速箱有限公司
重庆益弘工程塑料制品有限公司
北京首钢冷轧薄板有限公司
无锡三吉精工有限公司
汉升五金塑胶制品（苏州）有限公司高新区分公司
苏州佳宫精密机电有限公司
昆山拓宝五金塑胶有限公司
无锡诹访拓新精机有限公司
昆山维开安电子科技有限公司
艾来得科技（苏州）有限公司
茂森精艺金属(苏州)有限公司
苏州格鼎精密电子有限公司
苏州奥塞德精密科技有限公司
苏州大喜金属制品有限公司
爱三（佛山）汽车部件有限公司
东莞一化精密注塑模具有限公司
北京中美成信国际贸易有限公司
龙铁纵横(北京)轨道交通科技股份有限公司
理光（中国）投资有限公司
欧力士融资租赁(中国)有限公司
拉赫兰顿融资租赁(中国)有限公司
美联信金融租赁有限公司
广东粤运朗日股份有限公司
常州市国宇环保科技有限公司
中山市宏城实业有限公司
合肥会通新材料有限公司
科聚孚（重庆）工程塑料有限公司
上海永巧塑料制品有限公司'
'''


# li = sss.replace('\n', '').replace('\t', '').split('有限公司')[:-1]

# for i in li:
# 	print(get_spell(i))
# print(1)