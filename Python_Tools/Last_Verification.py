#Last_Verification

from lxml import etree
from zipfile import ZipFile
import os,shutil
import glob
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

#svg和xml文件复制函数（封装）
#开始检查用
def copy_svg_xml(fileNum):
	svg_SrcPath = '../Primary_Dataset/svg/'+str(fileNum)+'.svg'
	svg_DstPath = '../Dataset/Core/ErrorFiles/'+str(fileNum)+'.svg'
	xml_SrcPath = '../Primary_Dataset/MusicXML(converted_by_MXL)/' + str(fileNum) + '.xml'
	xml_DstPath = '../Dataset/Core/ErrorFiles/'+str(fileNum)+'.xml'
	mycopyfile(svg_SrcPath, svg_DstPath)
	mycopyfile(xml_SrcPath, xml_DstPath)



#1 简单的获取每个集合的类别（废弃)
def get_type():
	mxl_list = glob.glob('../Dataset/Core/mxl/*.mxl')

	fifths_type, mode_type, beats_type, beattype_type, clef_type, line_type,notestep_type, notetype_type, resttype_type, accidental_type = set(),set(),set(),set(),set(),set(),set(),set(),set(),set()
	sample, chord_num, error = 0,0,0


	for mxl in mxl_list:
		root = parse(mxl)
		if(len(root.xpath('.//chord'))!=0):
			chord_num+=1
			error+=1
		fifths_type |= set(root.xpath('//fifths/text()'))
		mode_type |= set(root.xpath('//mode/text()'))
		beats_type |= set(root.xpath('//beats/text()'))
		beattype_type |= set(root.xpath('//beat-type/text()'))
		clef_type |= set(root.xpath('//sign/text()'))
		line_type |= set(root.xpath('//line/text()'))
		notestep_type |= set(root.xpath('//note/pitch/step/text()'))
		notetype_type |= set(root.xpath('//note/pitch/../type/text()'))
		resttype_type |= set(root.xpath('//note/rest/../type/text()'))
		accidental_type |= set(root.xpath('//accidental/text()'))
		
		sample+=1
		if(sample%1000==0):
			print('Sample:',sample,'  error:',error)

	print('\n================Result================')
	print('Sample:',sample)
	print('调号:', fifths_type)
	print('调性:', mode_type)
	print('节拍(上):', beats_type)
	print('节拍(下):', beattype_type)
	print('谱号:', clef_type)
	print('谱号位置:', line_type)
	print('音高:', notestep_type)
	print('音符:', notetype_type)
	print('休止符:', resttype_type)
	print('临时变音符:', accidental_type)

#	Sample: 1000   error: 0
#	Sample: 2000   error: 0
#	Sample: 3000   error: 0
#	Sample: 4000   error: 0
#	Sample: 5000   error: 0
#
#	================Result================
#	Sample: 5964
#	调号: {'-6', '-5', '1', '0', '3', '-1', '-4', '-2', '5', '2', '4', '6', '-3', '-7', '7'}
#	调性: {'major', 'none', 'minor'}
#	节拍(上): {'24', '12', '19', '2', '4', '18', '9', '11', '1', '8', '7', '3', '20', '5', '10', '3+3+2', '15', '6', '28'}
#	节拍(下): {'2', '4', '1', '8', '16'}
#	谱号: {'F', 'C', 'G'}
#	谱号位置: {'2', '4', '3'}
#	音高: {'B', 'E', 'F', 'D', 'A', 'C', 'G'}
#	音符: {'32nd', 'half', '64th', 'breve', '16th', '128th', 'eighth', 'quarter', 'whole'}
#	休止符: {'32nd', 'half', '64th', 'breve', '16th', '128th', 'eighth', 'quarter', 'whole'}
#	临时变音符: {'sharp', 'flat-flat', 'natural', 'flat-down', 'quarter-sharp', 'three-quarters-sharp', 'natural-down', 'flat', 'slash-sharp', 'double-sharp'}



#2 获取每个类别的数量，用Counter方法获取（主要!!!）
def get_type_num():
	mxl_list = glob.glob('../Dataset/Core/mxl/*.mxl')
	
	clef_type, clef_line_type, note_type, rest_type, accidental_type, musescore_version, octave_type, clef_octave_change_type = Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter()
	
	note_dot_error, rest_dot_error = Counter(),Counter() #note_dot_error和rest_dot_error分别是检测音符和休止符有没有双附点的错误（此情况目前不作处理）
	sample,rest_hasNoType,rest_hasNoType_Total = 0,0,0
	for mxl in mxl_list:
		root = parse(mxl)
		#更新clef_type的Count类
		tmp_clef = str(root.xpath('.//sign/text()')[0])
		clef_type[tmp_clef] += len(root.xpath('//print[@new-system="yes"]'))
		
		#更新clef_line_type的Count类（是把clef和line结合成一体）
		tmp_line = str(root.xpath('.//line/text()')[0])
		tmp_clef_line_list = [tmp_clef + tmp_line]
		clef_line_type.update(tmp_clef_line_list)
		
		#更新accidental_type的Count类
		accidental_type.update(root.xpath('//accidental/text()'))
		
		#更新note_type的Count类
		xml_note_list = root.xpath('//note/pitch/..')
		tmp_note_list = []
		for element in xml_note_list:
			tmp_note_type = str(element.xpath('./type/text()')[0]) #获取此音符的类型
			dotNum = len(element.xpath('./dot'))
			if(dotNum == 1): tmp_note_type += '-dot'
			elif(dotNum != 0):
				note_dot_error.update(str(dotNum)) #错误
				continue
			tmp_note_list.append(tmp_note_type)
		note_type.update(tmp_note_list)
		
		#更新rest_type的Count类
		xml_rest_list = root.xpath('//note/rest/..')
		tmp_rest_list = []
		hasNoTypeBool = False
		for element in xml_rest_list:
			type_text = element.xpath('./type/text()')
			if(len(type_text)==0):
				rest_hasNoType+=1
				hasNoTypeBool = True
				continue
			tmp_rest_type = str(type_text[0])
			dotNum = len(element.xpath('./dot'))
			if(dotNum == 1): tmp_rest_type += '-dot'
			elif(dotNum != 0):
				rest_dot_error.update(str(dotNum)) #错误
				continue
			
			#2019.4.26 14:30
#			if(tmp_rest_type=='whole'): #把rest类型是whole的copy到一个目录下
#				fileNum = str(mxl.split('/')[8].strip('.mxl')) #！！！！！！！！！！变更目录后index的值要改变！！！！！！！！！！！！！
#				copy_svg_xml(fileNum)
			
			tmp_rest_list.append(tmp_rest_type)
			
		rest_type.update(tmp_rest_list)
		
		#2019.4.26 14:20
		if(hasNoTypeBool): #要把休止符没有写类别的xml文件连同svg文件一并写入到'../Dataset/Core/ErrorFiles/'目录下
			rest_hasNoType_Total+=1
#			fileNum = str(mxl.split('/')[8].strip('.mxl')) #！！！！！！！！！！变更目录后index的值要改变！！！！！！！！！！！！！
#			copy_svg_xml(fileNum)
		
		
		#2019.4.26 14:41
		#要统计一下MuseScore的版本!!!!!!
		musescore_version.update(root.xpath('//software/text()'))
		
		#2019.4.26 19:50
		#统计一下octave的分布
		tmp_octave_list = root.xpath('//octave/text()')
		octave_type.update(tmp_octave_list)
#		if('7' in tmp_octave_list):
#			fileNum = str(mxl.split('/')[8].strip('.mxl')) #！！！！！！！！！！变更目录后index的值要改变！！！！！！！！！！！！！
#			copy_svg_xml(fileNum)
		
		#2019.4.26 22:01
		#统计谱号的自带八度变化
		tmp_clef_octave_change_list = root.xpath('//clef-octave-change/text()')
		if(tmp_clef_octave_change_list==[]):
			clef_octave_change_type.update(['0'])
		clef_octave_change_type.update(tmp_clef_octave_change_list)
#		if('2' in tmp_clef_octave_change_list):
#			fileNum = str(mxl.split('/')[8].strip('.mxl')) #！！！！！！！！！！变更目录后index的值要改变！！！！！！！！！！！！！
#			copy_svg_xml(fileNum)
		

		#样本累计
		sample+=1
		if(sample%1000==0):
			print('Sample:',sample)
			
	
	
	print('\n================================================================Result================================================================')	
	print('谱号类别\n',clef_type,'\n')
	print('谱号+谱号位置类别\n',clef_line_type,'\n')
	print('谱号自带八度变化类别\n',clef_octave_change_type,'\n')
	print('音符类别\n',note_type,'\n')
	print('音符八度类别\n',octave_type,'\n')
	print('休止符类别\n',rest_type,'\n')
	print('临时变化符号类别\n',accidental_type,'\n')
	print('音符附点错误:',note_dot_error,'\n休止符附点错误:',rest_dot_error,'\n')
	print('(已解决)无类别休止符错误个数:',rest_hasNoType,'  无类别休止符乐谱数字:',rest_hasNoType_Total)
	print('MuseScore_Version:',musescore_version)


#	结果
#	Sample: 1000
#	Sample: 2000
#	Sample: 3000
#	Sample: 4000
#	Sample: 5000
#
#	================================================================Result================================================================
#	谱号类别
#	 Counter({'G': 17265, 'F': 2899, 'C': 368}) 
#
#	谱号+谱号位置类别
#	 Counter({'G2': 5098, 'F4': 773, 'C3': 93}) 
#
#	谱号自带八度变化类别
#	 Counter({'0': 5459, '-1': 343, '1': 159, '2': 3}) 
#
#	音符类别
#	 Counter({'eighth': 229140, 'quarter': 152522, '16th': 56998, 'half': 36100, 'quarter-dot': 17032, 'half-dot': 9532, 'eighth-dot': 9261, 'whole': 8026, '32nd': 2911, '64th': 365, '16th-dot': 244, 'whole-dot': 80, '128th': 52, 'breve': 24, '32nd-dot': 13}) 
#
#	音符八度类别
#	 Counter({'4': 266347, '5': 153800, '3': 69634, '2': 20151, '6': 9431, '1': 3261}) 
#
#	休止符类别
#	 Counter({'eighth': 16339, 'quarter': 16041, 'half': 4613, '16th': 2416, 'whole': 531, 'quarter-dot': 367, 'half-dot': 206, 'eighth-dot': 155, '32nd': 145, '64th': 31, '16th-dot': 7, '128th': 2, 'breve': 1}) 
#
#	临时变化符号类别
#	 Counter({'sharp': 10307, 'flat': 6903, 'natural': 5693, 'quarter-sharp': 38, 'double-sharp': 31, 'flat-flat': 23, 'natural-down': 5, 'flat-down': 4, 'three-quarters-sharp': 4, 'slash-sharp': 1}) 
#
#	音符附点错误: Counter({'2': 324}) 
#	休止符附点错误: Counter() 
#
#	(已解决)无类别休止符错误个数: 20617   无类别休止符乐谱数字: 1813
#	MuseScore_Version: Counter({'MuseScore 1.3': 2513, 'MuseScore 2.0.2': 1866, 'MuseScore 1.2': 692, 'MuseScore 1.1': 277, 'MuseScore 2.0.1': 256, 'MuseScore 1.0': 117, 'MuseScore 2.0.3': 95, 'MuseScore 2.0.0': 85, 'MuseScore 0.9.6.2': 44, 'MuseScore 2.1.0': 15, 'MuseScore 2.2.1': 1, 'MuseScore 2.2.0': 1, 'MuseScore 2.3.1': 1, 'MuseScore 0.9.6.1': 1})




	
if __name__ == '__main__':
	if(not os.path.exists('../Dataset/Core/ErrorFiles')): os.mkdir('../Dataset/Core/ErrorFiles')
#	get_type()
	get_type_num()
	