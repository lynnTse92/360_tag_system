import os

def createDirs(dir_path_list):
	for dir_path in dir_path_list:
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)

def getFilePathList(dir_path):
	file_path_list = []
	files = os.listdir(dir_path)
	for f in files:
		file_path_list.append(dir_path+f)
	return file_path_list