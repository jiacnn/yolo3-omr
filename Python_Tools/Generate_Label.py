#Generate_Label
#准备根据svglabeltxt和mxl生成label的5964张乐谱，均满足如下条件：
#1 都是Monophonic的单谱表，不含和弦及复调(mxl中没有<chord>标签)
#2 都不含谱号(Clef)的变化（mxl中<sign>标签只有1个）
#3 都不含调性(Key)的变化（mxl中<key>标签只有1个）
#4 都不含长休止符（mxl中<multiple-rest>标签有0个）
#5 svg文件的Note类与mxl文件的<pitch>一一对应；svg文件的Rest类与mxl文件的<rest>与<rest>中的<dot>标签数量之和一一对应（对应的顺序相反）rest中的<dot>只能有0或1个
#6 svg与mxl的<accidental>标签一一对应

#在svglabeltxt中，需要标记如下内容：（此代码的功能）
#1 Clef: Type
#2 Note: Type and Relative_Position
#3 Rest: Type
#4 Accidential: Type
#5 KeySig: Type


from lxml import etree
from zipfile import ZipFile
import os,shutil
from copy import deepcopy
from collections import Counter

#解析函数
def parse(filename: str) -> etree._ElementTree: #解析mxl文件，将其转换为etree的元素树类型
	mxlfile = ZipFile(filename)
	for info in mxlfile.filelist:
		if not info.filename.startswith('META_INF'):
			xml = mxlfile.read(info.filename)
			doc = etree.fromstring(xml)
	return doc
	
#文件复制基本函数
def mycopyfile(srcfile,dstfile):
	if not os.path.isfile(srcfile):
		return
	else:
		fpath,fname=os.path.split(dstfile)    #分离文件名和路径
		if not os.path.exists(fpath):
			os.makedirs(fpath)                #创建路径
		shutil.copyfile(srcfile,dstfile)      #复制文件
		
#简单检查函数(初期用,生成时不用)
def Check(root: etree._ElementTree) -> int:
	if(len(root.xpath('.//sign/text()')) != 1): return 1
	if(len(root.xpath('.//clef-octave-change/text()')) > 1): return 2
	if(len(root.xpath('.//fifths/text()')) != 1): return 3
	return 0
	

#元映射常量 (0对应的五线谱中最下面的线)
G2_Meta = {'C':-2, 'D':-1, 'E':0, 'F':1, 'G':2, 'A':3, 'B':4} #高音谱号:C4 - B4
F4_Meta = {'C':-4, 'D':-3, 'E':-2, 'F':-1, 'G':0, 'A':1, 'B':2} #低音谱号:C2 - B2
C3_Meta = {'C':-3, 'D':-2, 'E':-1, 'F':0, 'G':1, 'A':2, 'B':3} #中音谱号:C3 - B3
Meta = {'G2':G2_Meta, 'F4':F4_Meta, 'C3':C3_Meta}
Octave_Meta = {'G2':4, 'F4':2, 'C3':3}

def Generate_Label():
	sample, loss_svgtxt = 0,0
	note_type_Counter, note_relative_position_Counter, rest_type_Counter, clef_type_Counter, accidental_type_Counter = Counter(),Counter(),Counter(),Counter(),Counter()
	with open('../Dataset/Core/Core_List.txt','r') as core_list_file: #7123个fileNum
		core_list = core_list_file.readlines()
		for core_item in core_list: #针对每一个fileNum的乐谱
			fileNum = core_item.strip('\n')
			
			#以下是几个必要文件的path
			svgtxt_path = '../Primary_Dataset/txt/' + str(fileNum) + '.txt'
			mxl_path = '../Dataset/Core/mxl/' + str(fileNum) + '.mxl'
			
			#开始从xml中获取重要基本信息
			root = parse(mxl_path)
			#1 sign,line -- 谱号信息(高音谱号G，低音谱号F，中音谱号C),谱号位置信息(已经确定好了只有G2,F4,C3)
			sign = str(root.xpath('.//sign/text()')[0]) #Core数据集中的乐谱xml文件中均只含有一个<sign>标签
			line = str(root.xpath('.//line/text()')[0])
			#2 clef_octave_change -- 谱号八度信息(无 或 +1 或 -1 或 2)
			tmp_list = root.xpath('.//clef-octave-change/text()') #如果是0则没有此标签
			if(tmp_list==[]): clef_octave_change = '0'
			else: clef_octave_change = str(tmp_list[0])
			#4 fifths -- 乐谱的调号信息(-7至7，负数代表降号，正数代表升号)
			fifths = str(root.xpath('.//fifths/text()')[0]) #Core数据集中的乐谱xml文件中均只含有一个<fifths>标签
			#5 accidental_list -- 临时变化音的list (注意list中的每个元素是lxml.etree._ElementUnicodeResult类型，使用时要转成str类型!!!)
			accidental_list = root.xpath('.//accidental/text()')
			#6 note_element_list -- 音符节点的list (即含有<pitch>标签的note节点)
			note_element_list = root.xpath('.//note/pitch/..')
			#7 rest_element_list -- 休止符节点的list (即含有<rest/>标签的note节点)
			rest_element_list = root.xpath('.//note/rest/..')
			
			
			#2019.4.27 9:40
			#从重要基本信息中推导出一些即将用到的量
			#1 音高的相对位置（要加上谱号的八度信息）
			pitch_Meta = deepcopy(Meta[sign+line]) #要用深拷贝
			for key,value in pitch_Meta.items(): pitch_Meta[key] = value - int(clef_octave_change)*7
			#2 根据fifths推导出keysig是升还是降
			if(int(fifths)>0): keysig = 'sharp'
			elif(int(fifths)<0): keysig = 'flat'
			else: keysig = 'natural'
			
			
			#2019.4.27 9:55
			#正式开始工作
			dotRest = 0 #非常重要的变量，标记rest是否有附点
			isBegin = True
			if(not os.path.exists('../Dataset/Core/LABEL')): os.mkdir('../Dataset/Core/LABEL')
			with open('../Dataset/Core/LABEL/' + str(fileNum) + '_label.txt','w') as label_file:
				with open(svgtxt_path) as svgtxt_file:
					svgtxt_file_lines = svgtxt_file.readlines()
					for svgtxt_file_line in svgtxt_file_lines:
						line_list = svgtxt_file_line.strip('\n').split(',')
						
						tmp_line = svgtxt_file_line.strip('\n') #准备写入的一行
						
						#1 音符
						if(line_list[0]=='Note'):
							note_element = note_element_list.pop()
							#推算音符的相对位置(核心）
							note_step = str(note_element.xpath('./pitch/step/text()')[0])
							note_octave = int(note_element.xpath('./pitch/octave/text()')[0])
							note_relative_position = pitch_Meta[note_step] + (note_octave - Octave_Meta[sign+line])*7
							note_relative_position = str(note_relative_position)
							#推断音符的类型(注意有dot)
							note_type = str(note_element.xpath('./type/text()')[0])
							note_dotNum = len(note_element.xpath('./dot'))
							for i in range(note_dotNum): note_type += '-dot'
							tmp_line += ',' + note_type + ',' + note_relative_position
							#统计类别数量
							note_type_Counter[note_type] += 1
							note_relative_position_Counter[note_relative_position] += 1
							
						#2 休止符
						elif(line_list[0]=='Rest'):
							if(dotRest > 0): dotRest -= 1 #把附点消耗完,svg中此Rest标记的是休止符的附点，需要跳过。需要记录，但是不标记Rest类型标签
							else:
								rest_element = rest_element_list.pop()
								dotRest = len(rest_element.xpath('./dot'))
								tmp = rest_element.xpath('./type/text()')
								if(tmp == []): rest_type = 'whole' #老版本全音休止符没有<type>标签
								else: rest_type = str(tmp[0])
								for i in range(dotRest): rest_type += '-dot'
								tmp_line += ',' + rest_type	
								#统计类别数量
								rest_type_Counter[rest_type] += 1	
								
						#3 临时变化音记号
						elif(line_list[0]=='Accidental'): #直接pop，不用检查列表是否为空，因为在生成数据集时已经满足了数量相等的条件
							accidental_type = str(accidental_list.pop())
							tmp_line += ',' + accidental_type
							#统计类别数量
							accidental_type_Counter[accidental_type] += 1
							
						#4 谱号
						elif(line_list[0]=='Clef'):
							clef_type = str(sign)
							tmp_line += ',' + clef_type
							#统计类别数量
							clef_type_Counter[clef_type] += 1
							
						#5 调号
						elif(line_list[0]=='KeySig'):
							tmp_line += ',' + keysig
							#统计类别数量
							accidental_type_Counter[keysig] += 1
							
						
						#写入，isBegin作用是第一行不加换行符
						if(isBegin):
							label_file.write(tmp_line)
							isBegin = False
						else:
							label_file.write('\n'+tmp_line)
			
			sample += 1
			if(sample%1000==0):
				print('Sample:',sample)
	
	
	print("================================================Result================================================")
	print('Sample:',sample)
	print('\n谱号类别分布:\n', clef_type_Counter)
	print('\n音符时值类别分布:\n', note_type_Counter)
	print('\n音符相对位置类别分布:\n', note_relative_position_Counter)
	print('\n休止符时值类比分布:\n', rest_type_Counter)
	print('\n变音记号类别分布:\n', accidental_type_Counter)


#	结果
#	================================================Result================================================
#	Sample: 7123
#
#	谱号类别分布:
#	 Counter({'G': 38113, 'F': 7419, 'C': 1257})
#
#	音符时值类别分布:
#	 Counter({'eighth': 402064, 'quarter': 231184, '16th': 129053, 'half': 53443, 'quarter-dot': 28451, 'eighth-dot': 16921, 'half-dot': 14885, 'whole': 12267, '32nd': 7606, '64th': 770, '16th-dot': 360, 'half-dot-dot': 237, 'quarter-dot-dot': 174, 'whole-dot': 131, '32nd-dot': 69, '128th': 52, 'eighth-dot-dot': 36, 'breve': 27, '16th-dot-dot': 23, 'whole-dot-dot': 1})
#
#	音符相对位置类别分布:
#	 Counter({'3': 97774, '2': 92591, '4': 91756, '5': 87194, '6': 73805, '1': 73524, '7': 60857, '0': 59780, '8': 47748, '-1': 46710, '9': 40143, '-2': 29037, '10': 26867, '11': 18068, '-3': 13569, '12': 11263, '-4': 7291, '13': 6624, '-5': 3793, '14': 3563, '15': 1993, '-7': 871, '-6': 851, '16': 805, '17': 401, '-8': 249, '18': 206, '-9': 156, '19': 75, '-11': 61, '-10': 44, '20': 23, '21': 14, '-12': 7, '-13': 6, '-16': 5, '23': 5, '24': 5, '-17': 4, '-15': 4, '-14': 4, '-18': 3, '-22': 1, '-20': 1, '-19': 1, '25': 1, '22': 1})
#
#	休止符时值类比分布:
#	 Counter({'eighth': 34015, 'whole': 31336, 'quarter': 27962, 'half': 8546, '16th': 5846, 'quarter-dot': 2048, 'eighth-dot': 840, 'half-dot': 754, '32nd': 417, '64th': 374, '16th-dot': 20, 'breve': 8, '128th': 2, 'long': 1})
#
#	变音记号类别分布:
#	 Counter({'sharp': 50699, 'flat': 43331, 'natural': 10777, 'double-sharp': 197, 'flat-flat': 57, 'quarter-sharp': 38, 'natural-down': 5, 'flat-down': 4, 'three-quarters-sharp': 4, 'slash-sharp': 1})


#2019.4.29 11:20
#去掉了多页的乐谱
#================================================Result================================================
#Sample: 5964
#
#谱号类别分布:
# Counter({'G': 23120, 'F': 3905, 'C': 500})
#
#音符时值类别分布:
# Counter({'eighth': 229140, 'quarter': 152522, '16th': 56998, 'half': 36100, 'quarter-dot': 17032, 'half-dot': 9532, 'eighth-dot': 9261, 'whole': 8026, '32nd': 2911, '64th': 365, '16th-dot': 244, 'half-dot-dot': 154, 'quarter-dot-dot': 112, 'whole-dot': 80, '128th': 52, 'eighth-dot-dot': 34, 'breve': 24, '16th-dot-dot': 23, '32nd-dot': 13, 'whole-dot-dot': 1})
#
#音符相对位置类别分布:
# Counter({'3': 59753, '2': 57159, '4': 56885, '5': 51854, '6': 44899, '1': 40786, '7': 36732, '0': 34665, '8': 27061, '-1': 25826, '9': 22301, '-2': 15391, '10': 15120, '11': 9483, '-3': 6116, '12': 5909, '-4': 3584, '13': 3211, '-5': 1871, '14': 1720, '15': 801, '-6': 420, '16': 307, '-7': 256, '17': 180, '18': 82, '-8': 68, '19': 50, '-9': 39, '20': 17, '-11': 14, '21': 10, '-10': 10, '-12': 7, '-13': 6, '-16': 5, '23': 5, '-17': 4, '-15': 4, '-14': 4, '-18': 3, '-22': 1, '-20': 1, '-19': 1, '24': 1, '25': 1, '22': 1})
#
#休止符时值类比分布:
# Counter({'whole': 21148, 'eighth': 16339, 'quarter': 16041, 'half': 4613, '16th': 2416, 'quarter-dot': 734, 'half-dot': 412, 'eighth-dot': 310, '32nd': 145, '64th': 31, '16th-dot': 14, '128th': 2, 'breve': 1})
#
#变音记号类别分布:
# Counter({'sharp': 27524, 'flat': 23329, 'natural': 5693, 'quarter-sharp': 38, 'double-sharp': 31, 'flat-flat': 23, 'natural-down': 5, 'flat-down': 4, 'three-quarters-sharp': 4, 'slash-sharp': 1})




if __name__ == '__main__':
	Generate_Label()



#184078，4208