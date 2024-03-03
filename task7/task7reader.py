def read_patient_documents(filepath):
    file = open(filepath, "r")
    lines = file.readlines()
    file.close()
    
    documents = []
    doctype = ""
    content = []
    doc = {}
    
    for l in range(len(lines)):
        line = lines[l].strip("\n")
        if "DOCTYPE [" in line:
            doctype = line
        
        elif "SECTION [" in line:
            if len(content)>0:
                doc[key] = content
            
            key = doctype+" "+line
            content = []
        
        elif line == "":
            if len(content)>0:
                doc[key] = content
            
            documents.append(doc)
            
            content = []
            doc = {}
            
        elif "DATE [ " in line:
            doc["date"] = line
        
        else:
            content.append(line)
    
    if len(content)>0:
        doc[key] = content
        documents.append(doc)
        
    return documents
