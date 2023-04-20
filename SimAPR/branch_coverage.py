from typing import Dict


class BranchCoverage:
    def __init__(self):
        self.branch_coverage:Dict[int,int]=dict()

    def increment(self, line:int):
        if line in self.branch_coverage:
            self.branch_coverage[line]+=1
        else:
            self.branch_coverage[line]=1
    
    def diff(self,other:'BranchCoverage')->Dict[int,int]:
        diff:Dict[int,int]=dict()
        for line in self.branch_coverage:
            if line in other.branch_coverage:
                diff[line]=self.branch_coverage[line]-other.branch_coverage[line]
            else:
                diff[line]=self.branch_coverage[line]
        
        for line in other.branch_coverage:
            if line not in self.branch_coverage:
                diff[line]=-other.branch_coverage[line]
        return diff
    
def parse_cov(cov_file: str):
    """
    :param cov_file: branch coverage file
    :return: branch coverage vector
    """
    cov=BranchCoverage()
    with open(cov_file, 'r') as f:
        for line in f:
            branch=int(line.strip())
            cov.increment(branch)

    return cov
