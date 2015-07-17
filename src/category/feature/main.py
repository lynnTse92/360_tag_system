#encoding=utf-8
import os
import sys

def getCategoryPathList():
	category_path_list = [u'102232_考试']
	return category_path_list

def main(category_path):
	print category_path
	category_id = int(category_path.split('_')[0])
	print 'extracting 360 feature'
	os.system("python feature_extraction_360.py "+str(category_path))
	print 'extracting baidu baike feature'
	os.system("python feature_extraction_baidu.py "+str(category_path))
	print 'extracting baidu baike hierarchy feature'
	os.system("python feature_extraction_baidu_hierarchy.py "+str(category_path))
	print 'extracting wikipedia feature'
	os.system("python feature_extraction_wiki.py "+str(category_path))
	print 'extracting internal feature'
	os.system("python feature_extraction_internal.py "+str(category_id))
	print 'combining all feature'
	os.system("python combine_feature.py "+str(category_path))

if __name__ == '__main__':
	reload(sys)
	sys.setdefaultencoding('utf-8')

	for category_path in getCategoryPathList():
		main(category_path)