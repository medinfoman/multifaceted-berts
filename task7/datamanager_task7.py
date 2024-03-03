import os
import glob
import time

# 00001 -> 1
def recover_to_int(strnumber):
    for z in range(len(strnumber)):
        if strnumber[z]!=0:
            return int(strnumber[z:])
    return 0

# entitie map
def make_ent_map(targetdir, filename, ent_map):
    
    ent_mode = False
    file = open(targetdir, "r")
    lines = file.readlines()
    file.close()
    
    for l in range(len(lines)):
        line = lines[l].strip()
#         print("line: ", line)
        
        if "#### entities" in line:
            ent_mode=True
        
        if len(line.split("\t"))<3:
            continue
        
        if ent_mode==True:
            if line.lower()=="none":
                break
                
            key = line.split("\t")[0]
            cui = line.split("\t")[1]
            sem = line.split("\t")[2]
            term = line.split("\t")[3]
            
            doc_id = key.split("/")[0]
            sent_id = key.split("/")[1]
            begin = key.split("/")[2]
            end = key.split("/")[3]
            
            if cui in ent_map:
                valtmp = ent_map[cui]
                #print("cui", cui, ", valtmp: ", valtmp)
                valtmp.append(filename+"/"+doc_id+"/"+sent_id+"/"+\
                                            begin+"/"+end+"/"+sem+"/"+term)
                ent_map[cui] = valtmp
            
            else:
                ent_map[cui] = [filename+"/"+doc_id+"/"+sent_id+"/"+\
                                            begin+"/"+end+"/"+sem+"/"+term]
    
    return ent_map
    

def make_corpus_map(targetdir, filename, corpus_map):
    
    ent_mode = False
    file = open(targetdir, "r")
    lines = file.readlines()
    file.close()
    
    for l in range(len(lines)):
        line = lines[l].strip()
        #print("line: ", line)
        
        if "#### entities" in line:
            break
        
        doc_id = line.split("\t")[0]
        sent_id = line.split("\t")[1]

        dockey = str(filename)+"/"+str(doc_id)
        if dockey in corpus_map:
            corpustmp = corpus_map[dockey]
            corpustmp.append(line)
            corpus_map[dockey] = corpustmp            
        else:
            corpus_map[dockey] = [line]

    return corpus_map


def get_map_data(department="감염내과", mode="train"):
    start_time = time.time()
    
    ent_map = {}

    corpus_map = {}
    
    cui_to_term = {}
    cui_to_sem = {}
    ent_count = {}
    
    files_input = glob.glob("./data/03_entities_task7_fixed/"+str(mode)+"/"+str(department)+"/*_data.txt")
    files_input.sort()

    for f in range(0, len(files_input)):
        filename = files_input[f].split("/")[-1]

        
        ent_map = make_ent_map(files_input[f], filename, ent_map)
        corpus_map = make_corpus_map(files_input[f], filename, corpus_map)
    
    return ent_map, corpus_map


def orgarnize_document(target_doc):
    date = ""
    doctype = ""
    section2content = {}
    for t in range(len(target_doc)):
        if t==0:
            date = target_doc[t].split("\t")[4]
            continue
            
        section = target_doc[t].split("\t")[3]
        content = target_doc[t].split("\t")[4]
        
        # DOCTYPE [ 감염내과 _ 외래경과 ] SECTION [ Subjective [ Symptoms ] <- 소견 ]
        doctype = section.split("] SECTION [")[0]
        doctype = doctype.replace("DOCTYPE [", "").strip()
        
        section = section.split("] SECTION [")[1].strip()
        section = section[:-1].strip()
        
        if section in section2content:
            tmpcontent = section2content[section]
            tmpcontent.append(content)
            section2content[section] = tmpcontent
        else:
            section2content[section] = [content]
    
    or_document = []
    or_document.append(date)
    or_document.append(doctype)
    
    for section in section2content:
        or_document.append(section)
        contents = section2content[section]
        or_document = or_document + contents
    
    return or_document
    
    
    
