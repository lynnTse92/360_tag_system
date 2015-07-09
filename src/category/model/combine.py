#encoding=utf-8
import sys
sys.path.append('../../common/')
import text_process
import file_utils
import pickle

data_path = '../../../data/'

def readData(category_id):
	category_set = set([])
	category_wrapper_dict = {}
	infile = open('result_pointwise_'+str(category_id)+'.txt')
	for row in infile:
		items = row.strip().split(',')
		category = items[0].decode('utf-8')
		label = int(items[1])
		if label == 1:
			category_wrapper_dict.setdefault(category,[])
		category_set.add(category)
	infile.close()
	return list(category_set),category_wrapper_dict

def getCategoryEditorTag(category_id):
	print 'getting category editor tag'
	tag_fre_dict = {}
	tag_set = set([])
	app_tag_dict = pickle.load(open(data_path+'app_tag.dict','rb'))
	app_category_dict = pickle.load(open(data_path+'app_category.dict','rb'))
	infile = open(data_path+'all_cn_seg_nwi_clean.txt','rb')
	for row in infile:
		items = row.strip().split("<@>")
		try:
			app_id = int(items[0])
			app_name = items[1].decode('utf-8')
			seg_brief_list = items[2].decode('utf-8').split()
		except:
			continue
		if app_category_dict[app_id][1] != category_id:
			continue
		tags = app_tag_dict[app_id]
		for tag in tags:
			tag_fre_dict.setdefault(tag,0)
			tag_fre_dict[tag] += 1
	for app_tag in tag_fre_dict.keys():
		if tag_fre_dict[app_tag] >= 10:
			tag_set.add(app_tag)
	return tag_set

def combine(category_id,category_list,category_wrapper_dict):
	print 'combing'
	tag_set = set([])
	editor_tag_set = getCategoryEditorTag(category_id)
	outfile = open('combine/'+str(category_id)+'.txt','wb')
	outfile2 = open('final/'+str(category_id)+'.txt','wb')
	for i in range(len(category_list)):
		for j in range(len(category_list)):
			if i != j :
				category_i = category_list[i]
				category_j = category_list[j]
				if len(category_i) < len(category_j):
					if text_process.isSubset(category_i,category_j) or len(set(category_i)&set(category_j)) == len(category_i):
						if category_i in category_wrapper_dict.keys():
							category_wrapper_dict[category_i].append(category_j)
	for category in category_wrapper_dict.keys():
		tag_set.add(category)
		for wrapper in category_wrapper_dict[category]:
			tag_set.add(wrapper)
		outfile.write(category+'@'+','.join(category_wrapper_dict[category])+'\r\n')
	tag_set = tag_set | editor_tag_set
	for tag in tag_set:
		outfile2.write(tag+'\r\n')


def main(category_id):
	reload(sys)
	sys.setdefaultencoding('utf-8')

	file_utils.createDirs(['combine','final'])
	category_list,category_wrapper_dict = readData(category_id)
	combine(category_id,category_list,category_wrapper_dict)

if __name__ == '__main__':
	main(54)