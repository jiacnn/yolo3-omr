#2019.4.29 11:24
#将Core的文字label转为编码label


from lxml import etree
from zipfile import ZipFile
import os,shutil
import glob
from collections import Counter

#之前的映射，有错误且顺序需要更改，废弃
#type_map = {'sharp':0, 'flat':1, 'natural':2, 'G':3, 'F':4, 'C':5, 'BarLine':6, 'TimeSig':7, 'Note':8, 'Rest':9, 'others':10}
#note_type_map = {'eighth':0, 'quarter':1, '16th':2, 'half':3, 'quarter-dot':4, 'eighth':5, 'half-dot':6, 'whole':7, '32nd':8, 'others':9}
#rest_type_map = {'eighth':0, 'quarter':1, '16th':2, 'half':3, 'quarter-dot':4, 'eighth':5, 'half-dot':6, 'whole':7, '32nd':8, 'others':9}

#2019.5.16更改为
type_map = {'others':0, 'sharp':1, 'flat':2, 'natural':3, 'G':4, 'F':5, 'C':6, 'BarLine':7, 'TimeSig':8, 'Note':9, 'Rest':10}
note_type_map = {'others':0, '32th':1, '16th':2, 'eighth':3, 'eighth-dot':4, 'quarter':5, 'quarter-dot':6, 'half':7, 'half-dot':8, 'whole':9}
rest_type_map = {'others':0, '32th':1, '16th':2, 'eighth':3, 'eighth-dot':4, 'quarter':5, 'quarter-dot':6, 'half':7, 'half-dot':8, 'whole':9}


def decodeLabel():
	labeltxt_path_list = glob.glob('../Dataset/Core/LABEL/*.txt')
	if(not os.path.exists('../Dataset/Core/CODED_LABEL')): os.mkdir('../Dataset/Core/CODED_LABEL')
	
	type_map_counter, note_type_map_counter, rest_type_map_counter = Counter(),Counter(),Counter()
	sample = 0
	for labeltxt in labeltxt_path_list:
		lable_split_path, label_split_name = os.path.split(labeltxt)

		with open(lable_split_path.replace('LABEL','CODED_LABEL/') + label_split_name.replace('label','coded_label'), 'w') as f_w:
			isBegin = True
			with open(labeltxt,'r') as f_r:
				labeltxt_lines = f_r.readlines()
				for labeltxt_line in labeltxt_lines:
					labeltxt_line_split = labeltxt_line.strip('\n').split(',')
					tmp_line = ""
					
					#1 变音记号 或 谱号 或 调号
					if(labeltxt_line_split[0]=='Accidental' or labeltxt_line_split[0]=='Clef' or labeltxt_line_split[0]=='KeySig'):
						if(labeltxt_line_split[5] in type_map.keys()):
							labeltxt_line_split[0] = str(type_map[labeltxt_line_split[5]])
						else:
							labeltxt_line_split[0] = str(type_map['others'])
							
						type_map_counter[labeltxt_line_split[0]] += 1 #统计标签数量
						
						labeltxt_line_split[5] = '100' #用100表示None，即没有值
						labeltxt_line_split.append('100') #用100表示None，即没有值
						tmp_line = ','.join(labeltxt_line_split)
						
						###################################################################要添加counter！！！！！！
					#2 小节线 (要把第三个坐标从0改为0.005)
					elif(labeltxt_line_split[0]=='BarLine'):
						labeltxt_line_split[0] = str(type_map[labeltxt_line_split[0]])
						labeltxt_line_split[3] = str(0.005) #此数值原本为0，即小节线的宽度，由于0不好识别，于是改为0.005
						labeltxt_line_split.append('100') #用100表示None，即没有值
						labeltxt_line_split.append('100') #用100表示None，即没有值
						
						type_map_counter[labeltxt_line_split[0]] += 1 #统计标签数量
						
						tmp_line = ','.join(labeltxt_line_split) 
					
					#3 拍号
					elif(labeltxt_line_split[0]=='TimeSig'):
						labeltxt_line_split[0] = str(type_map[labeltxt_line_split[0]])
						labeltxt_line_split.append('100') #用100表示None，即没有值
						labeltxt_line_split.append('100') #用100表示None，即没有值
						
						type_map_counter[labeltxt_line_split[0]] += 1 #统计标签数量
						
						tmp_line = ','.join(labeltxt_line_split)
					
					#4 音符类 第六个和第七个值分别是音符的 时值 和 音高相对位置
					elif(labeltxt_line_split[0]=='Note'):
						labeltxt_line_split[0] = str(type_map[labeltxt_line_split[0]])
						if(labeltxt_line_split[5] in note_type_map.keys()):
							labeltxt_line_split[5] = str(note_type_map[labeltxt_line_split[5]])
						else:
							labeltxt_line_split[5] = str(note_type_map['others'])
						
						type_map_counter[labeltxt_line_split[0]] += 1 #统计标签数量
						note_type_map_counter[labeltxt_line_split[5]] += 1 #统计标签数量
						
						
						tmp_line = ','.join(labeltxt_line_split) 
					
					#5 休止符类
					elif(labeltxt_line_split[0]=='Rest' and len(labeltxt_line_split)==6): #判断长度是否等于6，目的是判断此行记录的是否为Rest本体
						labeltxt_line_split[0] = str(type_map[labeltxt_line_split[0]])
						if(labeltxt_line_split[5] in note_type_map.keys()):
							labeltxt_line_split[5] = str(note_type_map[labeltxt_line_split[5]])
						else:
							labeltxt_line_split[5] = str(note_type_map['others'])
						
						labeltxt_line_split.append('100') #用100表示None，即没有值
						
						type_map_counter[labeltxt_line_split[0]] += 1 #统计标签数量
						rest_type_map_counter[labeltxt_line_split[5]] += 1 #统计标签数量
						
						tmp_line = ','.join(labeltxt_line_split)
					
					#写入
					if(tmp_line != ""):
						if(isBegin): isBegin = False
						else: tmp_line = '\n' + tmp_line
						f_w.write(tmp_line)
		
		
		sample += 1
		if(sample%1000==0):
			print("Sample:",sample)	
	print("========================Result========================")
	print("成功编码:",sample)
	
	print('\ntype_map_counter:\n',type_map_counter)
	print('\ntype_map_counter:\n',note_type_map_counter)
	print('\ntype_map_counter:\n',rest_type_map_counter)
		




if __name__ == '__main__':
	decodeLabel()
	
