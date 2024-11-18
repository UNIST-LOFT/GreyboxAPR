from logging import Logger
from typing import Dict, Tuple, List

def toNumeric(v: str):
    if v.lower() == 'true':
        return 1
    if v.lower() == 'false':
        return 0
    return float(v)

class FieldChange:
    def __init__(self):
        self.field_change:Dict[str,float]=dict() # key: field_name, value: history

    def append(self, field:str, value):
        if field in self.field_change:
            self.field_change[field].append(value)
        else:
            self.field_change[field]=[value]
    
    def diff(self,other:'FieldChange')->List[Tuple[str,float]]:
        diff:List[Tuple[str,float]]=[]
        for field in self.field_change:
            if field in other.field_change:
                if self.field_change[field]!=other.field_change[field]:
                    diff.append((field,self.field_change[field]-other.field_change[field]))
            else:
                diff.append((field,self.field_change[field]))
        
        for field in other.field_change:
            if field not in self.field_change:
                diff.append((field,-other.field_change[field]))
        return diff
    
def parse_change(logger:Logger, change_file: str):
    """
    :param change_file: field change file
    :return: field change vector
    """
    change=FieldChange()
    logger.info(f"i want to open {change_file}")
    
    # try:
    #     root = ET.parse(change_file)
    #     fieldTags = root.findall("field")
    #     for fieldTag in fieldTags:
    #         id = fieldTag.get("id")
    #         history = List()
    #         for value in fieldTag:
    #             if (value.text != None):
    #                 history.append(int(value.text))
    #         change.field_change[id] = history
    # except:
    #     logger.warning(f"Error parsing field change file: {change_file}")
    
    with open(change_file, 'r') as f:
        for line in f:
            try:
                field_name,value = line.strip().split(":")
                change.field_change[field_name] = toNumeric(value)
            except:
                logger.warning(f"Error parsing field change: {line.strip()}")
        
    return change

# def is_good_patch(cov_patch_diff:Set[Tuple[int,int]],cov_orig_diff:Set[Tuple[int,int]])->bool:
#     for cov_element in cov_patch_diff:
#         if cov_element in cov_orig_diff:
#             return True
#     return False