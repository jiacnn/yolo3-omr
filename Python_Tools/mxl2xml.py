# 将mxl转换为MusicXML格式，批量
from lxml import etree
from zipfile import ZipFile
import os
import glob

def parse(filename: str) -> str: #解析mxl文件，将其转换为etree的元素树类型
	mxlfile = ZipFile(filename) #解压
	for info in mxlfile.filelist:
		if not info.filename.startswith('META_INF'):
			xml = mxlfile.read(info.filename)
	return xml


def convertAll(): #全部转换
	cnt = 0
	ls = glob.glob('../Primary_Dataset/mxl/*.mxl')
	for line in ls:
		path, name = os.path.split(line)
		fileNum = name.strip('.mxl')
		#输出到目标路径
		with open('../Primary_Dataset/MusicXML(converted_by_MXL)/' + str(fileNum) + '.xml', 'w', encoding="utf-8") as f2:
			xml_line = parse(line.strip('\n'))
			xml_line = str(xml_line)
			if "\\n" in xml_line:
				xml_line = xml_line.replace("\\n","\n") #换行美化
			f2.write(xml_line)
		
		cnt+=1
		if(cnt%1000==0):
			print("Sample:",cnt)
	
	print("Total Sample:",cnt)



if __name__ == '__main__':
	convertAll()