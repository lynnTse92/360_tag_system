import os
import sys

def main(category_id):
	# print 'extracting 360 feature'
	# os.system("python feature_extraction_360.py "+str(category_id))
	# print 'extracting baidu baike feature'
	# os.system("python feature_extraction_baidu.py "+str(category_id))
	# print 'extracting baidu baike hierarchy feature'
	# os.system("python feature_extraction_baidu_hierarchy.py "+str(category_id))
	# print 'extracting wikipedia feature'
	# os.system("python feature_extraction_wiki.py "+str(category_id))
	# print 'extracting internal feature'
	# os.system("python feature_extraction_internal.py "+str(category_id))
	print 'combining all feature'
	os.system("python combine_feature.py "+str(category_id))
	
if __name__ == '__main__':
	main(54)