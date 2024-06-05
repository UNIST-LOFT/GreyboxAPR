#!/usr/bin/env python3
import os
import time
from dataclasses import dataclass
import logging
import numpy as np
from enum import Enum
from typing import List, Dict, Tuple, Set, Union
import uuid
import math

import branch_coverage


class Mode(Enum):
  casino = 1
  seapr = 2
  orig = 3
  genprog = 4

  greybox=5

class ToolType(Enum):
  TEMPLATE=1
  LEARNING=2

# Parameters
class PT():
  ALPHA_INCREASE=1
  BETA_INCREASE=0
  ALPHA_INIT=2
  BETA_INIT=2
  EPSILON_THRESHOLD=0.05
  FL_WEIGHT=0.25
  EPSILON_A=10
  EPSILON_B=3

class SeAPRMode(Enum):
  FILE=0,
  FUNCTION=1,
  LINE=2,
  TYPE=4

class PassFail:
  def __init__(self, p: float = 0., f: float = 0.) -> None:
    self.pass_count = p
    self.fail_count = f
    
  def __exp_alpha(self, exp_alpha:bool) -> float:
    if exp_alpha:
      if self.pass_count==0:
        return 1.
      else:
        return min(1024.,self.pass_count)
    else:
      return 1.
    
  def beta_mode(self, alpha_init: float=1.0, beta_init: float=1.0) -> float:
    if self.pass_count+alpha_init+self.fail_count+beta_init==2.0:
      return 1.0
    return (self.pass_count+alpha_init - 1.0) / (self.pass_count+alpha_init+self.fail_count + beta_init - 2.0)
  
  def update(self, result: bool, n: float,b_n:float=1.0, exp_alpha: bool = False) -> None:
    if result:
      self.pass_count += n * self.__exp_alpha(exp_alpha)
    else:
      self.fail_count+=b_n
            
  def select_value(self,a_init:float=1.0,b_init:float=1.0) -> float: # select a value randomly from the beta distribution
    return np.random.beta(self.pass_count + a_init, self.fail_count + b_init)
    
  @staticmethod
  def normalize(x: List[float]) -> List[float]:
    npx = np.array(x)
    x_max = np.max(npx)
    x_min = np.min(npx)
    x_diff = x_max - x_min
    if (x_diff < 1e-6):
      x_norm = npx - x_min
    else:
      x_norm = (npx - x_min) / x_diff
    return x_norm.tolist()
    
  @staticmethod
  def select_by_probability(probability: List[float]) -> int:   # pf_list: list of PassFail
    total = 0
    for p in probability:
      if p > 0:
        total += p
    rand=np.random.random()*total
    for i in range(len(probability)):
      if probability[i] < 0:
        continue
      rand -= probability[i]
      if rand <= 0:
        return i
    return 0
  
  @staticmethod
  def concave_up(x: float, base: float = math.e) -> float:
    # unique function
    return x * x
    
  # fail function
  @staticmethod
  def log_func(x: float, half: float = 51) -> float:
    a=half
    if a-x<=0:
      return 0.
    else:
      return max(np.log(a - x) / np.log(a), 0.)

class CriticalBranchUpDown:
  """
  used for GreyBox approach
  multiple of instances are stored in CriticalBranches as the value of the dictionary, with the branch indexes as a key.
  saves and handle the data that are related to the fitness score of one branch

  Returns:
      _type_: _description_
  """
  def __init__(self, branchUpInit: float = 1., branchDownInit: float = 1.) -> None:
    """_summary_

    Args:
        branchUpInit (float, optional): _description_. Defaults to 0..
        branchDownInit (float, optional): _description_. Defaults to 0..
    """
    self.branchUpInit=branchUpInit # a constant value. saves the initial value of the branchUpScore.
    self.branchUpScore=branchUpInit # it will be increase with some kinds of value (increasing amount depends on the update method)
    self.branchDownInit=branchDownInit # a constant value. saves the initial value of the branchDownScore.
    self.branchDownScore=branchDownInit # it will be increase with some kinds of value (increasing amount depends on the update method)
    
  def update(self, branch_difference:int):
    """
    Compare the original_branch_count and the patched_branch_count to update the scores.
    - if original_branch_count > patched_branch_count then self.branchDownScore increases.
    - if original_branch_count < patched_branch_count then self.branchUpScore increases.
    - the amount of increasement can be modified in this source code.

    Args:
        original_branch_count (int): _description_
        patched_branch_count (int): _description_
    """
    print('grey-box alpha updated')
    if branch_difference<0:
      self.branchDownScore+=1 # increase the score with some value.
    elif branch_difference>0:
      self.branchUpScore+=1 # increase the score with some value.

  def mode(self,isUp):
    if isUp:
      if self.branchUpScore+self.branchUpInit+self.branchUpInit==2.0:
        return 1.0
      return (self.branchUpScore+self.branchUpInit - 1.0) / (self.branchUpScore+self.branchUpInit*2 - 2.0)
    else:
      if self.branchDownScore+self.branchDownInit+self.branchDownInit==2.0:
        return 1.0
      return (self.branchDownScore+self.branchDownInit - 1.0) / (self.branchDownScore+self.branchDownInit*2 - 2.0)

  def select_value(self,isUp:bool) -> float: # select a value randomly from the beta distribution
    """
    select a value randomly from the beta distribution.
    The distribution for selecting varies depending on the 'isUp'.

    Args:
        isUp (bool): true if the branch count increases in patched one then the buggy one, otherwise false.

    Returns:
        float: _description_
    """
    if isUp:
      return np.random.beta(self.branchUpScore, self.branchUpInit)
    else:
      return np.random.beta(self.branchDownScore, self.branchDownInit)
    
  
class CriticalBranchesUpDownManager:
  """
  This class is used not only for the critical branch data but also for the branch difference data of each node in the patch tree 
  although the name of the class is still "CriticalBranchUpDownManager"
  
  This class has a dictionary that saves the branch indexes as key and CriticalBranchUpDown as value.
  It helps you to call CriticalBranchUpDown with an specific index when calling 'update' and 'select_value'.
  this class also can be used when there are some jobs that have to deal with multiple of CriticalBranchUpDown.
  
  This class will be instanciated when initiaing the GlobalState and it is used for the ~~~...
  Also it is instantiated in each PatchTreeNode. it is for ~~~
  """
  def __init__(self, is_this_critical_branches = False):
    self.upDownDict:Dict[int, CriticalBranchUpDown]=dict()
    self.is_this_critical_branches=is_this_critical_branches
    
  def update(self, state:'GlobalState', branch_index:int, branch_difference:int):
    if branch_index not in self.upDownDict:
      self.upDownDict[branch_index]=CriticalBranchUpDown()
      if self.is_this_critical_branches:
        state.new_critical_list.append(branch_index)

    self.upDownDict[branch_index].update(branch_difference)
  
  def is_empty(self):
    return not bool(self.upDownDict)
    
  def select_value(self, branch_index:int, isUp:bool)->float:
    if branch_index not in self.upDownDict:
      self.upDownDict[branch_index]=CriticalBranchUpDown()
    return self.upDownDict[branch_index].select_value(isUp)
  
  def get_isUp(self, branch_index:int):
    """
    TODO: more description
    IMPORTANT: it return False when up score == down score

    Args:
        branch_index (int): _description_

    Returns:
        _type_: _description_
    """
    the_branch=self.upDownDict[branch_index]
    if the_branch.branchUpScore>the_branch.branchDownScore:
      return True
    else:
      return False

class PatchTreeNode:
  def __init__(self):
    self.parent=None
    self.pf = PassFail()
    self.positive_pf = PassFail()
    self.total_case_info: int = 0 # the number of cases that the node itself originally had. It increases only when reading the file and building the patch tree, and never decreases.
    self.case_update_count: int = 0 # increases with 1 each time a patch under the node itself is removed.
    self.update_count: int = 0 # never used??
    self.children_basic_patches:int=0 # the number of patches that passed
    self.children_plausible_patches:int=0
    self.consecutive_fail_count:int=0
    self.consecutive_fail_plausible_count:int=0
    self.patches_by_score:Dict[float,List[TbarCaseInfo]]=dict()
    self.remain_patches_by_score:Dict[float,List[TbarCaseInfo]]=dict()
    self.remain_lines_by_score:Dict[float,List[LineInfo]]=dict()

    # greybox things
    self.coverage_info=PassFail()
    self.patches_template_type:List[str] = []
    self.critical_branch_up_down_manager:CriticalBranchesUpDownManager=CriticalBranchesUpDownManager()

class LocationNode(PatchTreeNode):
  def __init__(self):
    super().__init__()
    self.fl_score=-1
    self.fl_score_list: List[float] = list()
    self.score_list: List[float] = list()

class FileInfo(LocationNode):
  def __init__(self, file_name: str) -> None:
    super().__init__()
    self.file_name = file_name
    self.func_info_map: Dict[str, FuncInfo] = dict() # f"{func_name}:{func_line_begin}-{func_line_end}"
    self.class_name: str = ""
    
  def __hash__(self) -> int:
    return hash(self.file_name)
  def __eq__(self, other) -> bool:
    return self.file_name == other.file_name
  
  def __str__(self) -> str:
    return self.file_name

class FuncInfo(LocationNode):
  def __init__(self, parent: FileInfo, func_name: str) -> None:
    super().__init__()
    self.parent = parent
    self.func_name = func_name
    self.id = self.func_name
    self.line_info_map: Dict[uuid.UUID, LineInfo] = dict()
    self.func_rank: int = -1

    self.total_patches_by_score:Dict[float,int]=dict() # Total patches grouped by score
    self.searched_patches_by_score:Dict[float,int]=dict() # Total searched patches grouped by score
    self.same_seapr_pf = PassFail(1, 1)
    self.diff_seapr_pf = PassFail(1, 1)
    self.case_rank_list: List[str] = list()    
  
  def __hash__(self) -> int:
    return hash(self.id)
  def __eq__(self, other) -> bool:
    return self.id == other.id and self.parent.file_name == other.parent.file_name
  
  def __str__(self) -> str:
    return f'{self.parent}-{self.func_name}'

class LineInfo(LocationNode):
  def __init__(self, parent: FuncInfo, line_number: int) -> None:
    super().__init__()
    self.uuid = uuid.uuid4()
    self.line_number = line_number
    self.parent = parent
    self.tbar_type_info_map: Dict[str, TbarTypeInfo] = dict()
    self.line_id = -1
    self.recoder_case_info_map: Dict[int, RecoderCaseInfo] = dict()
  
  def __hash__(self) -> int:
    return hash(self.uuid)
  def __eq__(self, other) -> bool:
    return self.uuid == other.uuid
  
  def __str__(self) -> str:
    return f'{self.parent}-{self.line_number}'

class TbarTypeInfo(PatchTreeNode):
  def __init__(self, parent: LineInfo, mutation: str) -> None:
    super().__init__()
    self.parent = parent
    self.mutation = mutation
    self.tbar_case_info_map: Dict[str, TbarCaseInfo] = dict()
  def __hash__(self) -> int:
    return hash(self.mutation)
  def __eq__(self, other) -> bool:
    return self.mutation == other.mutation and self.parent==other.parent
  
  def __str__(self) -> str:
    return f'{self.parent}-{self.mutation}'

class TbarCaseInfo(PatchTreeNode):
  def __init__(self, parent: TbarTypeInfo, location: str) -> None:
    super().__init__()
    self.parent = parent
    self.location = location
    self.same_seapr_pf = PassFail(1, 1)
    self.diff_seapr_pf = PassFail(1, 1)
    self.patch_rank: int = -1
  def __hash__(self) -> int:
    return hash(self.location)
  def __eq__(self, other) -> bool:
    return self.location == other.location
  
  def __str__(self) -> str:
    return self.location

class RecoderCaseInfo(PatchTreeNode):
  def __init__(self, parent: LineInfo, location: str, case_id: int) -> None:
    super().__init__()
    self.parent = parent
    self.location = location
    self.case_id = case_id
    self.prob: float = 0
    self.same_seapr_pf = PassFail(1, 1)
    self.diff_seapr_pf = PassFail(1, 1)
    self.patch_rank: int = -1
  def __hash__(self) -> int:
    return hash(self.location)
  def __eq__(self, other) -> bool:
    return self.location == other.location
  
  def __str__(self) -> str:
    return self.location

class BranchInfo:
  def __init__(self, id: int, c_i: int, c_u: int, n_i: int, n_u:int) -> None:
    self.id = id
    self.c_i = c_i # the number of interesting paths that change the counts of the given critical branch
    self.c_u = c_u # the number of uninteresting paths that change the counts of the given critical branch
    self.n_i = n_i # the number of interesting paths that does not change the counts of the given critical branch
    self.n_u = n_u # the number of uninteresting paths that does not change the counts of the given critical branch
    self.ochiai = self.calculate_ochiai()    
    self.patch_list = []
    self.interesting_patch_list = []
    self.intPatch_probability = self.calculate_prob() 
    self.plausible_pass_count=0
    self.interesting_pass_count=0
      
  def calculate_prob(self):
    if len(self.patch_list) != 0:
      prob = float(len(self.interesting_patch_list))/float(len(self.patch_list))
      return prob
    else:
      return 0.
  
  def add_patch(self, patch):
    self.patch_list.append(patch)
    self.calculate_prob()
    
  def add_interesting_patch(self, patch):
    self.interesting_patch_list.append(patch)
    self.calculate_prob()
  
  def calculate_ochiai(self):
    denominator = math.sqrt((self.c_i + self.n_i ) * (self.c_i + self.c_u))
    if denominator == 0:
        return -1.  # Handle division by zero error
    result = float(self.c_i)/float(denominator)
    return result
  
  def update_ci(self, c_i: int):
    self.c_i = c_i
    self.ochiai = self.calculate_ochiai()    
    
  def update_cu(self, c_u: int):
    self.c_u = c_u
    self.ochiai = self.calculate_ochiai()   
    
  def update_ni(self, n_i: int):
    self.n_i = n_i
    self.ochiai = self.calculate_ochiai()   
    
  def update_nu(self, n_u: int):
    self.n_u = n_u
    self.ochiai = self.calculate_ochiai()   

class EnvGenerator:
  def __init__(self) -> None:
    pass
  @staticmethod
  def get_new_env_tbar(state: 'GlobalState', patch: 'TbarPatchInfo', test: str,instrument:bool=False) -> Dict[str, str]:
    """
    TODO: need more description
    generates new dictionary of environment variables

    Args:
        state (GlobalState): _description_
        patch (TbarPatchInfo): _description_
        test (str): _description_

    Returns:
        Dict[str, str]: _description_
    """
    new_env = os.environ.copy()
    new_env["SIMAPR_UUID"] = str(state.uuid)
    new_env["SIMAPR_TEST"] = str(test)
    new_env["SIMAPR_LOCATION"] = str(patch.tbar_case_info.location)
    new_env["SIMAPR_WORKDIR"] = state.work_dir
    new_env["SIMAPR_BUGGY_LOCATION"] = patch.file_info.file_name
    new_env["SIMAPR_BUGGY_PROJECT"] = state.d4j_buggy_project
    new_env["SIMAPR_TIMEOUT"] = str(state.timeout)
    if patch.file_info.class_name != "":
      new_env["SIMAPR_CLASS_NAME"] = patch.file_info.class_name

    if state.mode==Mode.greybox and (instrument or state.only_get_test_time_data_mode):
      new_env['GREYBOX_BRANCH']='1'
      new_env['GREYBOX_RESULT']=f'/tmp/{state.d4j_buggy_project}-{test.replace("::","#")}.txt'
      new_env['GREYBOX_INSTR_ROOT']=state.instrumenter_classpath
      new_env['CLASSPATH']=state.instrumenter_classpath
    else:
      new_env['GREYBOX_BRANCH']='0'
      new_env['CLASSPATH']=state.instrumenter_classpath
    return new_env
  
  @staticmethod
  def get_new_env_recoder(state: 'GlobalState', patch: 'RecoderPatchInfo', test: str,instrument:bool=False) -> Dict[str, str]:
    new_env = os.environ.copy()
    new_env["SIMAPR_UUID"] = str(state.uuid)
    new_env["SIMAPR_TEST"] = str(test)
    new_env["SIMAPR_LOCATION"] = str(patch.recoder_case_info.location)
    new_env["SIMAPR_WORKDIR"] = state.work_dir
    new_env["SIMAPR_BUGGY_LOCATION"] = patch.file_info.file_name
    new_env["SIMAPR_BUGGY_PROJECT"] = state.d4j_buggy_project
    new_env["SIMAPR_TIMEOUT"] = str(state.timeout)

    if state.mode==Mode.greybox and (instrument or state.only_get_test_time_data_mode):
      new_env['GREYBOX_BRANCH']='1'
      new_env['GREYBOX_RESULT']=f'/tmp/{state.d4j_buggy_project}-{test.replace("::","#")}.txt'
      new_env['GREYBOX_INSTR_ROOT']=state.instrumenter_classpath
      new_env['CLASSPATH']=state.instrumenter_classpath
    else:
      new_env['GREYBOX_BRANCH']='0'
      new_env['CLASSPATH']=state.instrumenter_classpath
    return new_env
  
  @staticmethod
  def get_new_env_d4j_positive_tests(state: 'GlobalState', tests: List[str], new_env: Dict[str, str]) -> Dict[str, str]:
    new_env["SIMAPR_TEST"] = "ALL"
    new_env['CLASSPATH']=state.instrumenter_classpath
    new_env['GREYBOX_BRANCH']='0'
    return new_env

class TbarPatchInfo:
  """
  This class has methods related to a TbarCaseInfo, which is given in __init__ as an argument.
  The instance can do the following jobs.
  - update the data(such as the beta distributions(== PassFail)) in each nodes in the path from root to the patch
  - remove the patch from the
  """
  def __init__(self, tbar_case_info: TbarCaseInfo) -> None:
    self.tbar_case_info = tbar_case_info
    self.tbar_type_info = tbar_case_info.parent
    self.line_info = self.tbar_type_info.parent
    self.func_info = self.line_info.parent
    self.file_info = self.func_info.parent
    self.out_dist = -1.0
    self.out_diff = False    
    
  def update_result(self, result: bool, n: float, b_n:float,exp_alpha: bool) -> None:
    self.tbar_case_info.pf.update(result, n,b_n, exp_alpha)
    self.tbar_type_info.pf.update(result, n,b_n, exp_alpha)
    self.line_info.pf.update(result, n,b_n, exp_alpha)
    self.func_info.pf.update(result, n,b_n,exp_alpha)
    self.file_info.pf.update(result, n,b_n, exp_alpha)
    
  def update_result_positive(self, result: bool, n: float, b_n:float,exp_alpha: bool) -> None:
    self.tbar_case_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.tbar_type_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.line_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.func_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.file_info.positive_pf.update(result, n,b_n, exp_alpha)
    
  def update_branch_result(self, state:'GlobalState', branch_index:int, branch_difference:int) -> None:
    """
    Used for the GreyBox Approach.
    
    This function updates the CriticalBranchUpDown in every node in path to the patch

    Args:
        branch_index (int): _description_
        branch_difference (int): _description_
    """
    self.tbar_case_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.tbar_type_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.line_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.func_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.file_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    
  def remove_patch(self, state: 'GlobalState') -> None:
    """
    This funciton is called only at the end of each loop iteration. i.e. when the selecting patch, running tests, update the results have end.
    This function removes self.tbar_case_info from the self.tbar_type_info.tbar_case_info_map, and handle all the additional jobs needed to remove it.
    - ex) When self.tbar_type_info.tbar_case_info_map is empty after removing self.tbar_case_info, then remove the self.tbar_type_info.tbar_case_info_map from the self.line_info.tbar_type_info_map

    Args:
        state (GlobalState): _description_
    """
    if self.tbar_case_info.location not in self.tbar_type_info.tbar_case_info_map:
      state.logger.critical(f"{self.tbar_case_info.location} not in {self.tbar_type_info.tbar_case_info_map}")
      
    del self.tbar_type_info.tbar_case_info_map[self.tbar_case_info.location]
    
    if len(self.tbar_type_info.tbar_case_info_map) == 0:
      del self.line_info.tbar_type_info_map[self.tbar_type_info.mutation]
      
    if len(self.line_info.tbar_type_info_map) == 0:
      score = self.line_info.fl_score
      self.func_info.fl_score_list.remove(score)
      self.file_info.fl_score_list.remove(score)
      del self.func_info.line_info_map[self.line_info.uuid]
      state.score_remain_line_map[self.line_info.fl_score].remove(self.line_info)
      if len(state.score_remain_line_map[self.line_info.fl_score])==0:
        state.score_remain_line_map.pop(self.line_info.fl_score)
      self.func_info.remain_lines_by_score[self.line_info.fl_score].remove(self.line_info)
      if len(self.func_info.remain_lines_by_score[self.line_info.fl_score])==0:
        self.func_info.remain_lines_by_score.pop(self.line_info.fl_score)
      self.file_info.remain_lines_by_score[self.line_info.fl_score].remove(self.line_info)
      if len(self.file_info.remain_lines_by_score[self.line_info.fl_score])==0:
        self.file_info.remain_lines_by_score.pop(self.line_info.fl_score)
        
    if len(self.func_info.line_info_map) == 0:
      del self.file_info.func_info_map[self.func_info.id]
      state.func_list.remove(self.func_info)
      
    if len(self.file_info.func_info_map) == 0:
      del state.file_info_map[self.file_info.file_name]
      
    self.tbar_case_info.case_update_count += 1
    self.tbar_type_info.case_update_count += 1
    self.tbar_type_info.remain_patches_by_score[self.line_info.fl_score].remove(self.tbar_case_info)
    self.line_info.case_update_count += 1
    self.line_info.remain_patches_by_score[self.line_info.fl_score].remove(self.tbar_case_info)
    self.func_info.case_update_count += 1
    self.func_info.remain_patches_by_score[self.line_info.fl_score].remove(self.tbar_case_info)
    self.file_info.case_update_count += 1
    self.file_info.remain_patches_by_score[self.line_info.fl_score].remove(self.tbar_case_info)
    state.java_remain_patch_ranking[self.line_info.fl_score].remove(self.tbar_case_info)
    
    if len(state.java_remain_patch_ranking[self.line_info.fl_score])==0:
      state.java_remain_patch_ranking.pop(self.line_info.fl_score)
      
    self.func_info.searched_patches_by_score[self.line_info.fl_score]+=1

  def to_json_object(self) -> dict:
    conf = dict()
    conf["location"] = self.tbar_case_info.location
    return conf
  
  def to_str(self) -> str:
    return f"{self.tbar_case_info.location}"
  
  def __str__(self) -> str:
    return self.to_str()
  
  def to_str_sw_cs(self) -> str:
    return self.to_str()
  
  @staticmethod
  def list_to_str(selected_patch: list) -> str:
    result = list()
    for patch in selected_patch:
      result.append(patch.to_str())
    return ",".join(result)
  
class RecoderPatchInfo:
  def __init__(self, recoder_case_info: RecoderCaseInfo) -> None:
    self.recoder_case_info = recoder_case_info
    self.line_info = self.recoder_case_info.parent
    self.func_info = self.line_info.parent
    self.file_info = self.func_info.parent
    self.out_dist = -1.0
    self.out_diff = False

  def update_result(self, result: bool, n: float, b_n:float,exp_alpha: bool) -> None:
    self.recoder_case_info.pf.update(result, n,b_n, exp_alpha)
    self.line_info.pf.update(result, n,b_n, exp_alpha)
    self.func_info.pf.update(result, n,b_n, exp_alpha)
    self.file_info.pf.update(result, n,b_n, exp_alpha)

  def update_result_positive(self, result: bool, n: float, b_n:float,exp_alpha: bool) -> None:
    self.recoder_case_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.line_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.func_info.positive_pf.update(result, n,b_n, exp_alpha)
    self.file_info.positive_pf.update(result, n,b_n, exp_alpha)

  def update_branch_result(self, state:'GlobalState', branch_index:int, branch_difference:int) -> None:
    """
    Used for the GreyBox Approach.
    
    This function updates the CriticalBranchUpDown in every node in path to the patch

    Args:
        branch_index (int): _description_
        branch_difference (int): _description_
    """
    self.recoder_case_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.line_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.func_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
    self.file_info.critical_branch_up_down_manager.update(state,branch_index, branch_difference)

  def remove_patch(self, state: 'GlobalState') -> None:
    if self.recoder_case_info.location not in self.line_info.recoder_case_info_map:
      state.logger.critical(f"{self.recoder_case_info.location} not in {self.line_info.recoder_case_info_map}")
    del self.line_info.recoder_case_info_map[self.recoder_case_info.location]

    if len(self.line_info.recoder_case_info_map) == 0:
      score = self.line_info.fl_score
      self.func_info.fl_score_list.remove(score)
      self.file_info.fl_score_list.remove(score)
      del self.func_info.line_info_map[self.line_info.uuid]
      state.score_remain_line_map[self.line_info.fl_score].remove(self.line_info)
      if len(state.score_remain_line_map[self.line_info.fl_score])==0:
        state.score_remain_line_map.pop(self.line_info.fl_score)
      self.func_info.remain_lines_by_score[self.line_info.fl_score].remove(self.line_info)
      if len(self.func_info.remain_lines_by_score[self.line_info.fl_score])==0:
        self.func_info.remain_lines_by_score.pop(self.line_info.fl_score)
      self.file_info.remain_lines_by_score[self.line_info.fl_score].remove(self.line_info)
      if len(self.file_info.remain_lines_by_score[self.line_info.fl_score])==0:
        self.file_info.remain_lines_by_score.pop(self.line_info.fl_score)
    if len(self.func_info.line_info_map) == 0:
      del self.file_info.func_info_map[self.func_info.id]
      state.func_list.remove(self.func_info)
    if len(self.file_info.func_info_map) == 0:
      del state.file_info_map[self.file_info.file_name]
    prob = self.recoder_case_info.prob

    self.line_info.score_list.remove(prob)
    self.func_info.score_list.remove(prob)
    self.file_info.score_list.remove(prob)

    self.recoder_case_info.case_update_count += 1
    self.line_info.case_update_count += 1
    fl_score = self.line_info.fl_score
    self.line_info.remain_patches_by_score[fl_score].remove(self.recoder_case_info)
    self.func_info.case_update_count += 1
    self.func_info.remain_patches_by_score[fl_score].remove(self.recoder_case_info)
    self.file_info.case_update_count += 1
    self.file_info.remain_patches_by_score[fl_score].remove(self.recoder_case_info)
    state.java_remain_patch_ranking[fl_score].remove(self.recoder_case_info)
    if len(state.java_remain_patch_ranking[self.line_info.fl_score])==0:
      state.java_remain_patch_ranking.pop(self.line_info.fl_score)
    self.func_info.searched_patches_by_score[fl_score] += 1

  def to_json_object(self) -> dict:
    conf = dict()
    conf["location"] = self.recoder_case_info.location
    conf["id"] = self.line_info.line_id
    conf["case_id"] = self.recoder_case_info.case_id
    return conf
  
  def to_str(self) -> str:
    return f"{self.recoder_case_info.location}"
  
  def __str__(self) -> str:
    return self.to_str()
  
  def to_str_sw_cs(self) -> str:
    return self.to_str()
  
  @staticmethod
  def list_to_str(selected_patch: list) -> str:
    result = list()
    for patch in selected_patch:
      result.append(patch.to_str())
    return ",".join(result)

@dataclass
class Result:
  iteration: int
  time: float
  config: List[Union[TbarPatchInfo,RecoderPatchInfo]]
  result: bool
  pass_result: bool
  pass_all_neg_test: bool
  def __init__(self, execution: int, iteration:int,time: float, config: List[Union[TbarPatchInfo,RecoderPatchInfo]], result: bool,
               pass_test_result:bool=False, pass_all_neg_test: bool = False, compilable: bool = True) -> None:
    self.execution = execution
    self.iteration=iteration
    self.time = time
    self.config = config
    self.result = result
    self.pass_result=pass_test_result
    self.pass_all_neg_test = pass_all_neg_test
    self.compilable = compilable
    self.out_diff = config[0].out_diff

  def to_json_object(self,total_searched_patch:int=0,total_passed_patch:int=0,total_plausible_patch:int=0, new_critical_branch:List[int]=[]) -> dict:
    object = dict()
    object["execution"] = self.execution
    object['iteration']=self.iteration
    object["time"] = self.time
    object["result"] = self.result
    object['pass_result']=self.pass_result
    object["pass_all_neg_test"] = self.pass_all_neg_test
    object["compilable"] = self.compilable

    # This total counts include this result
    object['total_searched']=total_searched_patch
    object['total_passed']=total_passed_patch
    object['total_plausible']=total_plausible_patch
    conf_list = list()

    # for optimized greybox
    object['new_critical_branch']=new_critical_branch

    for patch in self.config:
      conf = patch.to_json_object()
      conf_list.append(conf)
    object["config"] = conf_list
    return object

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

@dataclass()
class GlobalState(metaclass=SingletonMeta):
  logger: logging.Logger
  original_args: List[str]
  args: List[str] # The arguments passed when the program is executed.
  work_dir: str
  out_dir: str
  def __init__(self) -> None:
    self.simapr_version = "1.1.0"
    self.mode = Mode.casino
    self.cycle = 0
    self.total_basic_patch = 0
    self.start_time = time.time()
    self.last_save_time = self.start_time
    self.is_alive = True
    self.use_pass_test = True
    self.skip_valid=False
    self.time_limit = -1
    self.cycle_limit = -1
    self.switch_case_map: Dict[str, Union[TbarCaseInfo, RecoderCaseInfo]] = dict()
    self.file_info_map: Dict[str, FileInfo] = dict()
    self.d4j_negative_test:List[str] = list()
    self.d4j_positive_test:List[str] = list()
    self.d4j_failed_passing_tests:Set[str] = set()
    self.d4j_buggy_project: str = ""
    self.patch_location_map: Dict[str, Union[TbarCaseInfo, RecoderCaseInfo]] = dict()
    self.priority_list: List[Tuple[str, int, float]] = list()
    self.line_list:List[LineInfo]=list()
    self.simapr_result:List[dict] = list()
    self.failed_positive_test:Set[str] = set()
    self.used_patch:List[Result] = list()
    self.timeout = 60000
    self.uuid=uuid.uuid1()
    self.tmp_dir = "/tmp"
    self.function_to_location_map: Dict[str, Tuple[str, int, int]] = dict()
    self.use_pattern = False
    self.use_simulation_mode = False
    self.prev_data = ""
    self.ignore_compile_error = True
    self.simulation_data: Dict[str, dict] = dict()
    self.correct_patch_str: str = ""
    self.correct_case_info: Union[TbarCaseInfo,RecoderCaseInfo] = None
    self.total_searched_patch=0
    self.total_passed_patch=0
    self.total_plausible_patch=0
    self.iteration=0 # To count how many times it has been repeated. It increments by 1 each time a big loop in simapr.run() iterates.
    self.use_partial_validation = True
    self.tool_type=ToolType.TEMPLATE
    self.use_exp_alpha = True
    self.top_fl=0
    self.patch_ranking:List[str] = list()
    self.finish_at_correct_patch=False
    self.func_list: List[FuncInfo] = list()
    self.count_compile_fail=True # If False, state.iteration doesn't increases when the patch is not compilable.
    self.finish_top_method=False  # Finish if every patches in top-30 methods are searched. Should turn on for default SeAPR
    self.debug_mode=False  # Set logger to debug mode

    self.seapr_layer:SeAPRMode=SeAPRMode.FUNCTION

    self.java_patch_ranking:Dict[float,List[TbarCaseInfo]]=dict()
    self.java_remain_patch_ranking:Dict[float,List[TbarCaseInfo]]=dict()
    self.score_remain_line_map:Dict[float,List[LineInfo]]=dict()  # Remaining lines by each scores(FL, prophet score, ...)

    self.previous_score:float=0.0
    self.same_consecutive_score:Dict[float,int]=dict()
    self.max_epsilon_group_size=0  # Maximum size of group for epsilon-greedy

    self.not_use_guided_search=False  # Use only epsilon-greedy search
    self.not_use_epsilon_search=False  # Use only guided search and original
    self.test_time=0.  # Sum of total compile and test time
    self.select_time=0.  # Total select time
    self.total_methods=0  # Total methods

    self.correct_patch_list:List[str]=[]  # List of correct patch ids

    # Added in greybox-APR
    self.instrumenter_classpath=''
    self.branch_output=''
    self.diff_patch_num=0  # # of patches that has diff coverage with orig
    self.original_branch_cov:Dict[str,branch_coverage.BranchCoverage]=dict()  # [test, coverage]
    self.hq_patch_diff_coverage_set:Set[branch_coverage.BranchCoverage]=set()  # Every (cov_patch - cov_original) coverage of HQ patches
    self.branchInfoDataPath=''
    self.branchInfoData:List[dict]=[]
    self.have_branch_info=False
    self.branch_map_ochiai:Dict[int, BranchInfo] = dict() #map each branch to each Branch object
    self.min_ochiai=0. #to maintain the min ochiai score to use when Patches(e) is empty 
    self.visited_tbar_patch:List[str] = list() 
    self.patch_to_branches_map:Dict[str, List[BranchInfo]] = dict() 
    self.patch_to_ochiai_map:Dict[str, float] = dict() 
    
    # 2nd vertical search things in greybox-APR
    # self.critical_branches:list[Tuple[int,int]] = [] #saves every single data of critical branches. list of tuple (branch index, branch count difference)
    self.use_fl_score_in_greybox = False
    self.weight_critical_branch = False
    self.critical_branch_up_down_manager:CriticalBranchesUpDownManager = None # It is for the saving the branch count difference regardless of test cases.Initialized right after GlobalState is initialized, because critical_branch_up_down_manager initializes GlobalState in it.
    self.optimized_instrumentation = False
    self.new_critical_list:List[int]=[] # get empty when each iteration begins
    self.no_instrumentation_time_data_output = "" # the directory path where the data is going to be saved.
    # self.no_instrumentation_time_data = {} # the data that will be referenced and modified during the experiment

    # only_get_test_time_data_mode
    self.only_get_test_time_data_mode = False
    self.test_time_data_location = ""
    
def patch_ochiai_calculator(state:GlobalState, str):
  valid_branches=0
  total = 0.
  for branch_info in state.patch_to_branches_map[str]:
    if branch_info.ochiai != -1.:
      total += branch_info.ochiai
      valid_branches+=1
  if valid_branches != 0:
    return float(total)/float(valid_branches)
  else:
    return -1.0
      
def remove_file_or_pass(file:str):
  try:
    if os.path.exists(file):
      os.remove(file)
  except:
    pass

def append_java_cache_result(state:GlobalState,case:Union[TbarCaseInfo,RecoderCaseInfo],fail_result:Dict[str,bool],pass_result:bool,compilable:bool,
      fail_time:float, pass_time:float,is_greybox=False):
  """
    Append result to cache file, if not exist. Otherwise, do nothing.
    
    state: GlobalState
    case: current patch
    fail_result: result of fail test (bool)
    pass_result: result of pass test (bool)
    fail_time: fail time (second)
    pass_time: pass time (second)
  """
  id=case.location
  if id not in state.simulation_data:
    current=dict()
    current['basic']=fail_result
    current['plausible']=pass_result
    current['pass_all_fail']=False not in fail_result.values()
    current['compilable']=compilable
    current['fail_time']=fail_time
    current['pass_time']=pass_time
    current['done_greybox']=is_greybox
    
    state.simulation_data[id]=current
  elif 'done_greybox' not in state.simulation_data[id] or not state.simulation_data[id]['done_greybox']:
    state.simulation_data[id]['done_greybox']=is_greybox