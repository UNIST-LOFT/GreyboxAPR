from logging import Logger
from typing import Dict, Set, Tuple


class BranchCoverage:
    def __init__(self):
        self.branch_coverage:Dict[int,int]=dict()

    def increment(self, line:int):
        if line in self.branch_coverage:
            self.branch_coverage[line]+=1
        else:
            self.branch_coverage[line]=1
    
    def diff(self,other:'BranchCoverage')->Set[Tuple[int,int]]:
        diff:Set[Tuple[int,int]]=set()
        for line in self.branch_coverage:
            if line in other.branch_coverage:
                if self.branch_coverage[line]!=other.branch_coverage[line]:
                    diff.add((line,self.branch_coverage[line]-other.branch_coverage[line]))
            else:
                diff.add((line,self.branch_coverage[line]))
        
        for line in other.branch_coverage:
            if line not in self.branch_coverage:
                diff.add((line,other.branch_coverage[line]))
        return diff
    
def parse_cov(logger:Logger, cov_file: str):
    """
    :param cov_file: branch coverage file
    :return: branch coverage vector
    """
    cov=BranchCoverage()
    with open(cov_file, 'r') as f:
        for line in f:
            try:
                branch_id,count=line.strip().split(":")
                cov.branch_coverage[int(branch_id)]=int(count)
            except:
                logger.warning(f"Error parsing branch ID: {line.strip()}")

    return cov

def is_good_patch(cov_patch_diff:Set[Tuple[int,int]],cov_orig_diff:Set[Tuple[int,int]])->bool:
    for cov_element in cov_patch_diff:
        if cov_element in cov_orig_diff:
            return True
    return False