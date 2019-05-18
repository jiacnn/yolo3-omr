#筛选出Core乐谱文件，条件如下：
#1 svglabeltxt文件中的TimeSig标签只有2个									（此项未选，占比15%）
#2 xml文件中的<sign>标签只有1个	，并且只有G2，F4，C3(2019.4.26)				（只有一种clef）
#3 xml文件中没有<multiple-rest>标签										（不含长休止符）
#4 xml文件中的<pitch>或<step>标签与svg中的Note类相等							（这是关键）
#5 xml文件中的<rest>标签与svg中的rest类相等
#6 xml文件中的<accidental>标签与svg中的Accidental类相等						（有少部分不符，占比13.168%，直接忽略）
#7 xml文件中的<key>标签只有1个												（多次变调的换行还处理不了）
#8 xml文件中没有<chord>标签												（不含和弦及复调）
#9 xml文件中的每个休止符的<dot>标签最多有1个（note的dot可能有多个）				（不含多重附点）
#10 svg文件中的Clef坐标的横坐标只有一个										（将多页的排除）

#运行结果如下：

#=================================Result=================================
#成功写入: 7241
#
#Sample: 9351 	TotalError: 2110 	Error Percent: 22.564 %
#TimeSig: 0   Clef: 134   MultipleRest: 563   Note: 39   Rest: 669   Accidental: 658   Key: 958
#Rest_Error_Ratio: 8.693 %   Accidental_Error_Ratio: 13.168 %


from lxml import etree
from zipfile import ZipFile
import os,shutil

#解析函数
def parse(filename: str) -> etree._ElementTree: #解析mxl文件，将其转换为etree的元素树类型
	mxlfile = ZipFile(filename)
	for info in mxlfile.filelist:
		if not info.filename.startswith('META_INF'):
			xml = mxlfile.read(info.filename)
			doc = etree.fromstring(xml)
	return doc

#文件复制函数
def mycopyfile(srcfile,dstfile):
	if not os.path.isfile(srcfile):
		return
	else:
		fpath,fname=os.path.split(dstfile)    #分离文件名和路径
		if not os.path.exists(fpath):
			os.makedirs(fpath)                #创建路径
		shutil.copyfile(srcfile,dstfile)      #复制文件



#创建需要用到的目录
if(not os.path.exists('../Dataset')): os.mkdir('../Dataset')
if(not os.path.exists('../Dataset/Core')): os.mkdir('../Dataset/Core')
if(not os.path.exists('../Dataset/Core/mxl')): os.mkdir('../Dataset/Core/mxl')
if(not os.path.exists('../Dataset/Core/svg')): os.mkdir('../Dataset/Core/svg')
if(not os.path.exists('../Dataset/Core/MusicXML')): os.mkdir('../Dataset/Core/MusicXML')


clef_line_type = ['G2','F4','C3']
#各种Error，以便记录每一种Error的占比是多少
sample, loss, total_error, timesig_error, clef_error, multiple_rest_error, note_error, rest_error, accidental_error, key_error, chord_error, rest_double_dot_error, octave_error, multi_page_error = 0,0,0,0,0,0,0,0,0,0,0,0,0,0
hasRest, hasAccidental = 0, 0
write_success = 0
f_output = open('../Dataset/Core/Core_List.txt', 'w')
with open('../txtlist.txt','r') as f1: #此txt记录的是所有labeltxt文件的文件名（例如 977.txt等）
		f1_lines = f1.readlines()
		for f1_line in f1_lines:
			fileNum = f1_line.strip('.txt\n') #去掉后缀，获取最纯正的编号（例如977），以方便接下来获取mxl文件
			txtFile_Path = '../Primary_Dataset/txt/' + f1_line.strip('\n')
			
			if(not os.path.exists('../Primary_Dataset/svg/'+str(fileNum)+'.svg')): #如果对应的svg文件不存在则直接跳过
				loss += 1
				continue
				
#			此段有了更好的替代方案
#			width, height = 0, 0				
#			with open('../Primary_Dataset/svg/'+str(fileNum)+'.svg', 'r') as svgFile:
#				svgFile.readline() #第一行没用
#				info = svgFile.readline() #此行有宽高信息
#				#info的一个示例：<svg width="595.276px" height="841.89px" viewBox="0 0 595.276 841.89"
#				width = info[info.find('width=')+7 : info.find('px')]
#				height = info[info.find('height=')+8 : info.find('px', info.find('px')+2, len(info))]
#				width, height = float(width), float(height)
			
			noteNum, restNum = 0, 0 #目的是获取labeltxt（svg）中Note（音符）的数量和Rest（休止符）的数量
			timesigNum, accidentalNum, current_clef_x, page_total_num = 0, 0, 0, 0
			with open(txtFile_Path, 'r') as txtFile: #打开对应的一个labeltxt文件（例如打开977.txt）
				txtFile_Lines = txtFile.readlines()
				#此步有了更好的替代方案
				#此步需要加入判断，因为在labeltxt文件（解析的svg）中，音符的符头和附点分别记录在Note类和NoteDot类中，但休止符的本体和附点都记录在Rest类中！！！
				#需要通过附点的特性，即长宽相等，对Rest进行分离
				#具体操作：
				#1 需要打开svg文件获取图像整体的width和height
				#2 如果当前行txtFile_Lines中是Rest类，则需要获取此行的最后两个数字，即Rest实体的长和宽对于整体图像的width和height的比例关系
				#3 进行判断，只有附点的长宽比等于1
				for txtFile_Line in txtFile_Lines:
					if(txtFile_Line.find('Note,') > -1): noteNum += 1 #必须加逗号！！！不然会加上NoteDot类
					
					#此段有了更好的替代方案
#					elif(txtFile_Line.find('Rest,') > -1): #要判断是Rest本体还是Rest附点，如果是附点，则restNum此轮不加1
#						#txtFile_Line的一个示例： Rest,0.5229932797835177,0.2584144972848779,0.008946309953727978,0.017026126526313835
#						width_ratio = float(txtFile_Line.split(',')[3])
#						height_ratio = float(txtFile_Line.split(',')[4])
#						if(round(width_ratio*width,1) != round(height_ratio*height,1)): restNum+=1 #判断不是正方形，即不是附点
					
					elif(txtFile_Line.find('Rest,') > -1): restNum+=1
					elif(txtFile_Line.find('TimeSig,') > -1): timesigNum+=1
					elif(txtFile_Line.find('Accidental,') > -1): accidentalNum+=1
					
					#2019.4.29 10:50
					#要读取svg中的clef的横坐标，从而排除双页的乐谱
					#如果svg中clef的横坐标多于一种，即判断此乐谱是多页乐谱
					elif(txtFile_Line.find('Clef') > -1):
						tmp_clef_x = round(float(txtFile_Line.split(',')[1]), 2)
						if(current_clef_x != tmp_clef_x):
							current_clef_x = tmp_clef_x
							page_total_num += 1
						
						
			
			
			mxlFile_Path = '../Primary_Dataset/mxl/' + str(fileNum) + '.mxl'
			if(not os.path.exists(mxlFile_Path)): #判断svglabel中获取的编号在mxl文件中是否存在；如果该编号的mxl文件不存在，则直接跳过
				loss += 1
				continue 
			
			if(restNum>0): hasRest+=1
			if(accidentalNum>0): hasAccidental+=1
			
			
			#通过以上步骤，获取到了svg文件中Note和真实的Rest标签的数量
			root = parse(mxlFile_Path) #将mxl转换为xml文件，再转化为etree形式
			error_flag = False
			#以下为验证阶段:
#			if(timesigNum!=2): 
#				timesig_error+=1
#				error_flag = True
				
			#谱号验证：必须是一个谱号，而且必须是G2 or F4 or C3
			clef_type = root.xpath('.//sign/text()') #list类型
			line_type = root.xpath('.//line/text()') #list类型
			if(len(clef_type)!=1 or len(line_type)!=1): 
				clef_error+=1
				error_flag = True
			elif(str(clef_type[0])+str(line_type[0]) not in clef_line_type):
				clef_error+=1
				error_flag = True
			
				
			if(len(root.findall('.//multiple-rest')) != 0):
				multiple_rest_error+=1
				error_flag = True
			if(len(root.findall('.//pitch')) != noteNum):
				note_error+=1
				error_flag = True
				
			
			#休止符:遍历xml中所有含rest标签的note，如果此note下的dot数量多于1个，则直接error并break
			#若第一步遍历完成后没有报error，那么xml中rest的总数(附点也算一个rest数量)与svg中的rest类的总数匹配，如果不相等则报error
			xml_rest_list = root.xpath('.//note/rest/..')
			tmp_restNum = len(xml_rest_list)
			for element in xml_rest_list:
				dotNum = len(element.xpath('./dot'))
				if(dotNum > 1): #去除多附点的休止符
					rest_double_dot_error += 1
					error_flag = True
					break
				if(dotNum==1):
					tmp_restNum+=1
			if(tmp_restNum!=restNum): #rest_error涵盖了rest_double_dot_error
				rest_error+=1
				error_flag = True
				
			#2019.4.26 20:40
			#八度类别:遍历xml中所有的octave标签，将octave为0,7,8,9的去掉
			xml_octave_list = root.xpath('.//pitch/octave/text()')
			if('0' in xml_octave_list or '7' in xml_octave_list or '8' in xml_octave_list or '9' in xml_octave_list):
				octave_error+=1
				error_flag = True
			
			
			if(len(root.findall('.//accidental')) != accidentalNum):
				accidental_error+=1
				error_flag = True
			if(len(root.findall('.//key')) != 1):
				key_error+=1
				error_flag = True
			if(len(root.findall('.//chord')) > 0):
				chord_error+=1
				error_flag = True
				
			#2019.4.29 10:50
			#要读取svg中的clef的横坐标，从而排除多页的乐谱
			if(page_total_num > 1):
				multi_page_error+=1
				error_flag = True
				
			
			
			
			if(error_flag):
				total_error+=1
			
			#如果没有error，就要copy了（放入CoreScore中）
			if(not error_flag):
#				要将svg、xml和MusicXML文件导出到指定位置(Copy)
				xml_SrcPath = '../Primary_Dataset/MusicXML(converted_by_MXL)/'+str(fileNum)+'.xml'
				xml_DstPath = '../Dataset/Core/MusicXML/'+str(fileNum)+'.xml'
				svg_SrcPath = '../Primary_Dataset/svg/'+str(fileNum)+'.svg'
				svg_DstPath = '../Dataset/Core/svg/'+str(fileNum)+'.svg'
				mxl_SrcPath = '../Primary_Dataset/mxl/' + str(fileNum) + '.mxl'
				mxl_DstPath = '../Dataset/Core/mxl/'+str(fileNum)+'.mxl'
				
				mycopyfile(xml_SrcPath, xml_DstPath)
				mycopyfile(svg_SrcPath, svg_DstPath)
				mycopyfile(mxl_SrcPath, mxl_DstPath)
				
				#ouput列表写入
				f_output.write(str(fileNum)+'\n')
				
				write_success += 1
				
			
			sample+=1
			if(sample%1000==0):	print('Sample:',sample,'  TotalError:',total_error,'  TimeSig:',timesig_error,'  Clef:',clef_error,'  MultipleRest:',multiple_rest_error,'  Note:',note_error,'  Rest:',rest_error,'  Accidental:',accidental_error,'  Key:',key_error,'  Chord:',chord_error,'  RestDoubleDot:',rest_double_dot_error,'  Octave:',octave_error,'  MultiPages:',multi_page_error)


f_output.close()
print('\n\n=================================Result=================================')
print('成功写入:',write_success)
print('\nSample:',sample,'\tTotalError:',total_error,"\tError Percent:", round(total_error/sample*100,3), '%' )
print('TimeSig:',timesig_error,'  Clef:',clef_error,'  MultipleRest:',multiple_rest_error,'  Note:',note_error,'  Rest:',rest_error,'  Accidental:',accidental_error,'  Key:',key_error,'  Chord:',chord_error,'  RestDoubleDot:',rest_double_dot_error,'  Octave:',octave_error,'  MultiPages:',multi_page_error)
print('Rest_Error_Ratio:',round(rest_error/hasRest*100,3),'%', '  Accidental_Error_Ratio:',round(accidental_error/hasAccidental*100,3),'%')


#结果
#=================================Result=================================
#成功写入: 5964
#
#Sample: 9351 	TotalError: 3387 	Error Percent: 36.221 %
#TimeSig: 0   Clef: 150   MultipleRest: 563   Note: 39   Rest: 700   Accidental: 658   Key: 958   Chord: 113   RestDoubleDot: 36   Octave: 71   MultiPages: 2096
#Rest_Error_Ratio: 9.096 %   Accidental_Error_Ratio: 13.168 %






#lxml试验
#root = parse('/Users/evasi0n/Desktop/xml文件label处理/mxl/2204.mxl')
#print(len(root.xpath('.//note/pitch')))
#print(len(root.findall('.//note')))

#print(root.xpath('.//note/text()'))
#print(len(root.findall('.//rest')))
#print(len(root.xpath('.//sign')))






