#####################################################################
# This code was written at the Seoul National University Medical Information Laboratory.
# This code preprocesses the text before inputting medical records into BERT.
# Please cite the source (https://github.com/medinfoman/multifaceted-berts) when you use this code.
# by Kyungmo Kim
# 
# 이 코드는 서울대학교 의료정보 연구실에서 작성되었습니다. 
# 의료기록지를 BERT 에 입력하여 학습시키기 전에 텍스트를 전처리하는 코드입니다.
# 활용시 출처(https://github.com/medinfoman/multifaceted-berts)를 남겨주시기 바랍니다. 
# By 김경모
#####################################################################

import re
import pandas as pd
import os, sys
import numpy as np
import re
import six
import glob
from openpyxl import Workbook

def convert_to_unicode(text):
    """Converts `text` to Unicode (if it's not already), assuming utf-8 input."""
    if six.PY3:
        if isinstance(text, str):
            return text
        elif isinstance(text, bytes):
            return text.decode("utf-8", "ignore")
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    elif six.PY2:
        if isinstance(text, str):
            return text.decode("utf-8", "ignore")
        elif isinstance(text, unicode):
            return text
        else:
            raise ValueError("Unsupported string type: %s" % (type(text)))
    else:
        raise ValueError("Not running on Python2 or Python 3?")
        
        

def getKoreanOnly(text):
    hangulonly = re.compile('[^ ㄱ-ㅣ가-힣]+')
    result = hangulonly.sub('', text)
    return result

def getEnglishOnly(text):
    enonly = re.compile('[^ a-zA-Z]+')
    result = enonly.sub('', text)
    return result

def parseRule1(lines):
    lines = lines.split('\n')
    
    regexp_rear = re.compile('(니다\.?|었음\.?|였음\.?|있음\.?(?!\)|없음\.?|'\
                        '행함\.?|렸다(\.|,)?)|옴\.|받음\.|호전(됨)?\.|임\.|짐\.|았음\.|퇴원함\.|'\
                        '다고 함\.|발생함\.|함\.|됨\.)')
    regexp_front = re.compile('\*검사')
    
    newlines = []
    linestack = ""
    for line in lines:

        korOnlyTmp = getKoreanOnly(line).strip()
        engOnlyTmp = getEnglishOnly(line).strip()

        if len(korOnlyTmp)<2 and len(engOnlyTmp)<2:
            newlines.append(line.strip())
            continue
        
        
        if len(korOnlyTmp)>2:            
            if (('안녕' in line) and ('선생님' in line)):
                if linestack!='':
                    iter = re.finditer(regexp_rear, linestack)
                    indices_r = [m.end(0) for m in iter]
                    iter = re.finditer(regexp_front, linestack)
                    indices_f = [m.start(0) for m in iter]
                    indices = []
                    for i in range(len(indices_r)):
                        indices.append(indices_r[i])
                    for i in range(len(indices_f)):
                        indices.append(indices_f[i])
                    indices = np.array(indices)
                    indices.sort()
                    indices = np.unique(indices)
                    
                    lastidx = 0
                    for i in range(len(indices)):
                        linetmp = textsep(linestack[lastidx:indices[i]].strip())
                        if linetmp!="":
                            newlines.append(linetmp)
                        lastidx=indices[i]
    
                    if lastidx!=len(linestack):
                        linetmp = textsep(linestack[lastidx:].strip())
                        if linetmp!="":
                            newlines.append(linetmp)
                        
                    linestack=""
                linetmp = textsep(line.strip())
                newlines.append(linetmp)
                
                continue
            
            else:  
                linestack = linestack.strip() + ' ' + line.strip()
                
        else:
            if linestack!='':
                iter = re.finditer(regexp_rear, linestack)
                indices_r = [m.end(0) for m in iter]
                iter = re.finditer(regexp_front, linestack)
                indices_f = [m.start(0) for m in iter]
                indices = []
                for i in range(len(indices_r)):
                    indices.append(indices_r[i])
                for i in range(len(indices_f)):
                    indices.append(indices_f[i])
                indices = np.array(indices)
                indices.sort()
                indices = np.unique(indices)
                
                lastidx = 0
                for i in range(len(indices)):
                    linetmp = textsep(linestack[lastidx:indices[i]].strip())        
                    if linetmp!="":
                        newlines.append(linetmp)
                    lastidx=indices[i]
                if lastidx!=len(linestack):
                    linetmp = textsep(linestack[lastidx:].strip())
                    if linetmp!="":
                        newlines.append(linetmp)
                linestack=""

            linetmp = textsep(line.strip())
            newlines.append(linetmp)
    

    if linestack!='':
        iter = re.finditer(regexp_rear, linestack)
        indices_r = [m.end(0) for m in iter]
        iter = re.finditer(regexp_front, linestack)
        indices_f = [m.start(0) for m in iter]
        indices = []
        for i in range(len(indices_r)):
            indices.append(indices_r[i])
        for i in range(len(indices_f)):
            indices.append(indices_f[i])
        indices = np.array(indices)
        indices.sort()
        indices = np.unique(indices)
                
        lastidx = 0
        for i in range(len(indices)):
            linetmp = textsep(linestack[lastidx:indices[i]].strip())
            if linetmp!="":
                newlines.append(linetmp)
            lastidx=indices[i]
    
        if lastidx!=len(linestack):
            linetmp = textsep(linestack[lastidx:].strip())
            if linetmp!="":
                newlines.append(linetmp)
        linestack=""
        
    return '\n'.join(newlines)



def whitespace_en_ko(text):
    sep_en_ko = re.compile('[a-zA-Z][가-힇]') 
    iter = re.finditer(sep_en_ko, text)
    indices = [m.end(0) for m in iter]
    
#     print("indices: ", indices)
    
    lastidx = 0
    seperatedtext=[]
    if len(indices) >= 1:
        lastidx = 0
        for i in range(len(indices)):
            seperatedtext.append(text[lastidx:indices[i]-1].strip())
            lastidx=indices[i]-1
        seperatedtext.append(text[lastidx:len(text)].strip())
        
        text = " ".join(seperatedtext)

    sep_ko_en = re.compile('[가-힇][a-zA-Z]') 
    iter = re.finditer(sep_ko_en, text)
    indices = [m.end(0) for m in iter]

    lastidx = 0
    seperatedtext=[]
    if len(indices) >= 1:
        lastidx = 0
        for i in range(len(indices)):
            seperatedtext.append(text[lastidx:indices[i]-1].strip())
            lastidx=indices[i]-1
        seperatedtext.append(text[lastidx:len(text)].strip())
        
        text = " ".join(seperatedtext)
        
    return text




def whitespace_number_spchar_char(text):
    sep_en_ko = re.compile('[a-zA-Z가-힇][.0-9 \(\{\[\-_\]\}\]\\\/]') 
    iter = re.finditer(sep_en_ko, text)
    indices = [m.end(0) for m in iter]
        
    lastidx = 0
    seperatedtext=[]
    if len(indices) >= 1:
        lastidx = 0
        for i in range(len(indices)):
            seperatedtext.append(text[lastidx:indices[i]-1].strip())
            lastidx=indices[i]-1
        seperatedtext.append(text[lastidx:len(text)].strip())        
        text = " ".join(seperatedtext)

    sep_ko_en = re.compile('[.0-9 \(\{\[\-_\]\}\]\\\/][a-zA-Z가-힇]') 
    iter = re.finditer(sep_ko_en, text)
    indices = [m.end(0) for m in iter]

    lastidx = 0
    seperatedtext=[]
    if len(indices) >= 1:
        lastidx = 0
        for i in range(len(indices)):
            seperatedtext.append(text[lastidx:indices[i]-1].strip())
            lastidx=indices[i]-1
        seperatedtext.append(text[lastidx:len(text)].strip())
        
        text = " ".join(seperatedtext)
        
    return text


def whitespace_num_day(text):
    days_sep = re.compile('[ 0-9]+일\s+[ 0-9]+회\s+\*\s+[ 0-9]+일') 
    
    iter = re.finditer(days_sep, text)
    indices = [m.end(0) for m in iter]    
    
    seperatedtext=[]
    if len(indices) >= 1:
        lastidx = 0
        for i in range(len(indices)):
            seperatedtext.append(text[lastidx:indices[i]].strip())
            lastidx=indices[i]
    else:
        return text
    
    return '\n'.join(seperatedtext)
    
import re
def textsep(text):
    text = re.sub(r'(?<=\()\+', ' + ', text)
    text = re.sub(r'\+(?=\))', ' + ', text)
    text = re.sub(r'(?<=/)\+(?=/)', ' + ', text)
    text = re.sub(r'\(\+\)', ' ( + ) ', text)
    text = re.sub(r'(?<=/)\+', ' + ', text)
    text = re.sub(r'\+(?=/)', ' + ', text)
    text = re.sub(r'\s+\+\s+', ' + ', text)
    text = re.sub(r'(?<=\()\-', ' - ', text)
    text = re.sub(r'\-(?=\))', ' - ', text)
    text = re.sub(r'(?<=/)\-(?=/)', ' - ', text)
    text = re.sub(r'\(\-\)', ' ( - ) ', text)
    text = re.sub(r'(?<=/)\-', ' - ', text)
    text = re.sub(r'\-(?=/)', ' - ', text)
    text = re.sub(r'\s+\-\s+', ' - ', text)
    text = re.sub(r'\s?\(\s?', ' ( ', text)
    text = re.sub(r'\s?\)\s?', ' ) ', text)
    text = re.sub(r'(?<=\d)\-(?=\d)', ' - ', text)
    text = re.sub(r'(?<=\d)\/(?=\d)', ' / ', text)
    text = re.sub(r'(?<=\d)\.(?=\d)', ' . ', text)
    text = re.sub(r'x ray', 'x-ray ', text)
    text = re.sub(r'X ray', 'X-ray ', text)
    text = re.sub(r'(?<=[.,a-zA-Z])\>', ' > ', text)
    text = re.sub(r'\,', ' , ', text)
    text = re.sub(r'\s+,\s+', ' , ', text)
    text = re.sub(r'(?<=[a-zA-Z])\:', ' : ', text)
    text = re.sub(r'\s+\:\s+', ' : ', text)
    text = re.sub(r'#\s?[0-9]+\.\s+', '', text)
    text = re.sub(r'\-{5,}', '', text) # ---------, ========== -> ''
    text = re.sub(r'\={5,}', '', text)
    text = re.sub(r'\(', ' ( ', text)
    text = re.sub(r'\s+\(\s+', ' ( ', text) #'(' -> ' ( '     
    text = re.sub(r'\)', ' ) ', text)
    text = re.sub(r'\s+\)\s+', ' ) ', text) #)  ' ) ' 
    text = re.sub(r'\:', ' : ', text)
    text = re.sub(r'\s+\:\s+', ' : ', text) #: ' : ' 
    text = re.sub(r';', ' ; ', text)
    text = re.sub(r'\s+;\s+', ' ; ', text) #; ' ; ' 
    text = re.sub(r'(?<=[0-9])일', ' 일', text)
    text = re.sub(r'(?<=[0-9])회', ' 회', text)
    text = re.sub(r'tab', ' tab ', text)    
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\t+', '\t', text)
    
    return text

# 간단한 비식별화 알고리즘이지만 완벽한 비식별화를 위해서는 모든 데이터를 직접 수정해야 합니다.
# This is simple deidentification rules, however, you should curate your data manually in the end.
def deidentificaiton(text):
    text = re.sub(r'([가-힇])+(\s+)?배상', 'OOO 배상', text)
    text = re.sub(r'([가-힇])+(\s+)?교수', 'OOO 교수', text)
    text = re.sub(r'([가-힇])+(\s+)?선생님', 'OOO 선생님', text)
    text = re.sub(r'pf(\s+)?([가-힇])+', 'pf OOO', text)
    text = re.sub(r'pf\.(\s+)?([가-힇])+', 'pf. OOO', text)
    text = re.sub(r'Pf\.(\s+)?([가-힇])+', 'pf. OOO', text)
    text = re.sub(r'PA(\s+)?([가-힇])+', 'PA OOO', text)
    return text


def delete_enter(lines):
    del_entered = []
    lines = str(lines).split("\n")
    for l in range(len(lines)):
        line = lines[l].strip("\n")
        line = lines[l].strip()
        if line=="":
            continue
        else:
            del_entered.append(line)
    
    newlines = "\n".join(del_entered)
    
    return newlines
    

def tab_to_spaces(line):
    line = line.replace("\t", "    ")
    return line
    
def text_preprocessing(lines):
    if len(str(lines).strip("\n").strip())==0:
        return []
    data = []
    lines = str(lines).split("\n")
    for l in range(len(lines)):
        line = lines[l].strip()
        line = tab_to_spaces(line)
        line = delete_enter(line)
        line = parseRule1(line)
        line = textsep(line)

        line = deidentificaiton(line)
        line = whitespace_en_ko(line)
        line = whitespace_number_spchar_char(line)        
        line = delete_enter(line)
        line = line.strip()
        if line=="":
            continue
        data.append(line)
        
    return data
    
    

