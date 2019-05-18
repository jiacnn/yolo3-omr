#此文件的目的是对比所有 mxl文件中的note标签数量和对应的已经解析好svglabel的txt文件中的note标签与rest标签之和 是否相等；
#发现有1424个文件不等，于是第二步将mxl文件标签比svglabel的txt文件标签多的和少的归为两类，将对应的svg和解析出来的xml分类放置，以查找到底漏掉了哪些标签
from lxml import etree
from zipfile import ZipFile
import os,shutil

#convert .mxl to etree via xml
def parse(filename: str) -> etree._ElementTree: #解析mxl文件，将其转换为etree的元素树类型
	mxlfile = ZipFile(filename)
	for info in mxlfile.filelist:
		if not info.filename.startswith('META_INF'):
			xml = mxlfile.read(info.filename)
			doc = etree.fromstring(xml)
	return doc

#MusicXML文件的etree共有三个root节点：<identification>, <part-list>, <part>


#文件复制函数
def mycopyfile(srcfile,dstfile):
	if not os.path.isfile(srcfile):
		return
	else:
		fpath,fname=os.path.split(dstfile)    #分离文件名和路径
		if not os.path.exists(fpath):
			os.makedirs(fpath)                #创建路径
		shutil.copyfile(srcfile,dstfile)      #复制文件


def Verification():
	# 先通过txtlist.txt获取labeltxt文件的地址，并打开统计noteNum和restNum；
	# 然后获取对应编号的mxl文件解析出xml文件，统计note的数量；
	# 最后判断note和noteNum+restNum是否相等
	Error,Sample,Loss = 0,0,0 #无实际用途
	xml_greater, xml_less = 0,0 #记录xml中的note比svglabel中的note+rest多的情况和少的情况的数量
	errorFile = open("../ErrorFiles/ErrorFilesNumber_Output.txt",'w')
	
	#创建目录，用于存放不满足验证条件的文件
	if(not os.path.exists('../ErrorFiles/xml_greater')):
		os.mkdir('../ErrorFiles/xml_greater')
	if(not os.path.exists('../ErrorFiles/xml_less')):
		os.mkdir('../ErrorFiles/xml_less')

	with open('../txtlist.txt','r') as txtListFile: #此txt记录的是所有labeltxt文件的文件名（例如 977.txt等）
		txtListFile_Lines = txtListFile.readlines()
		for txtListFile_Line in txtListFile_Lines :
			fileNum = txtListFile_Line.strip('.txt\n') #去掉后缀，获取最纯正的编号（例如977），以方便接下来获取mxl文件
			txtFile_Path = '../Primary_Dataset/txt/' + txtListFile_Line.strip('\n')
			
			#此步是先打开svg文件，读取当前fileNum对应的svg文件中全图的宽高信息，以方便下面分割Rest类使用
			width, height = 0, 0
			if(os.path.exists('../Primary_Dataset/svg/'+str(fileNum)+'.svg')==False): #如果对应的svg文件不存在则直接跳过
				Loss += 1
				continue
			with open('../Primary_Dataset/svg/'+str(fileNum)+'.svg', 'r') as svgFile:
				svgFile.readline() #第一行没用
				info = svgFile.readline() #此行有宽高信息
				#info的一个示例：<svg width="595.276px" height="841.89px" viewBox="0 0 595.276 841.89"
				width = info[info.find('width=')+7 : info.find('px')]
				height = info[info.find('height=')+8 : info.find('px', info.find('px')+2, len(info))]
				width, height = float(width), float(height)
			
			noteNum, restNum = 0, 0 #目的是获取labeltxt（svg）中Note（音符）的数量和Rest（休止符）的数量
			with open(txtFile_Path, 'r') as txtFile: #打开对应的一个labeltxt文件（例如打开977.txt）
				txtFile_Lines = txtFile.readlines()
				#此步需要加入判断，因为在labeltxt文件（解析的svg）中，音符的符头和附点分别记录在Note类和NoteDot类中，但休止符的本体和附点都记录在Rest类中！！！
				#需要通过附点的特性，即长宽相等，对Rest进行分离
				#具体操作：
				#1 需要打开svg文件获取图像整体的width和height
				#2 如果当前行txtFile_Lines中是Rest类，则需要获取此行的最后两个数字，即Rest实体的长和宽对于整体图像的width和height的比例关系
				#3 进行判断，只有附点的长宽比等于1
				for txtFile_Line in txtFile_Lines:
					if(txtFile_Line.find('Note,') > -1): noteNum += 1 #必须加逗号！！！不然会加上NoteDot类
					elif(txtFile_Line.find('Rest,') > -1): #要判断是Rest本体还是Rest附点，如果是附点，则restNum此轮不加1
						#txtFile_Line的一个示例： Rest,0.5229932797835177,0.2584144972848779,0.008946309953727978,0.017026126526313835
						width_ratio = float(txtFile_Line.split(',')[3])
						height_ratio = float(txtFile_Line.split(',')[4])
						if(round(width_ratio*width,0) != round(height_ratio*height,0)): restNum+=1 #判断不是正方形，即不是附点
		
			
			mxlFile_Path = '../Primary_Dataset/mxl/' + str(fileNum) + '.mxl'
			if(os.path.exists(mxlFile_Path)==False): #判断svglabel中获取的编号在mxl文件中是否存在；如果该编号的mxl文件不存在，则直接跳过
				Loss += 1
				continue 
			
			
			root = parse(mxlFile_Path) #将mxl转换为xml文件，再转化为etree形式
			#以下为验证阶段:
			if(len(root.findall('.//step')) + len(root.findall('.//rest')) != noteNum+restNum): 
				errorFile.write(str(fileNum)+'\n') #将错误的文件记录在txt文件中
				Error += 1
				
				#要将svg文件和xml文件输出到同一目录下，以方便弄清楚为什么两个数字不相等！！！
				svg_src_path = '../Primary_Dataset/svg/' + str(fileNum) + '.svg'
				if(os.path.exists(svg_src_path)) : #不存在表示找不到对应xml文件编号的svg文件，小概率事件：0.33%
					if(len(root.findall('.//note')) > noteNum+restNum): #证明xml文件中的note数量比svglabel文件中的note+rest数量要多
						xml_greater += 1
						xmlFile = str(etree.tostring(root))
						if '\\n' in xmlFile: xmlFile = xmlFile.replace("\\n","\n") #换行排版美化
						#xml创建
						with open('../ErrorFiles/xml_greater/'+str(fileNum)+'.xml','w') as f:
							f.write(xmlFile)
						#svg拷贝
						mycopyfile(svg_src_path, '../ErrorFiles/xml_greater/'+str(fileNum)+'.svg')
								
					else : #证明xml文件中的note数量比svglabel文件中的note+rest数量要少
						xml_less += 1
						xmlFile = str(etree.tostring(root))
						if '\\n' in xmlFile: xmlFile = xmlFile.replace("\\n","\n") #换行排版美化
						#xml创建
						with open('../ErrorFiles/xml_less/'+str(fileNum)+'.xml','w') as f:
							f.write(xmlFile)
						#svg拷贝
						mycopyfile(svg_src_path, '../ErrorFiles/xml_less/'+str(fileNum)+'.svg')

						
			#输出验证
			Sample += 1
			if(Sample%1000==0):
				print("Sample:",Sample,"  Error:",Error,"  Loss:",Loss)	
			
	errorFile.close()
	print("\n\nTotal Error:",Error,"  Total Sample:",Sample,"  Total Loss:",Loss,"  Total xml_greater:",xml_greater,"  Total xml_less:",xml_less)
	print("Error Percent:", round(Error/Sample*100,2), '%')


if __name__ == '__main__':
	Verification()

