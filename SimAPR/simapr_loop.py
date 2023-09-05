import time
from core import *
import select_patch
import result_handler as result_handler
import run_test
import shutil
import json
import matplotlib.pyplot as plt
import numpy as np

class TBarLoop():
  def __init__(self, state: GlobalState) -> None:
    self.state:GlobalState=state
    self.is_initialized:bool=False

  def _is_method_over(self) -> bool:
    """Check the ranks of every remaining methods are over then 30"""
    if not self.state.finish_top_method: return False
    
    min_method_rank=10000 # Some large rank
    for p in self.state.patch_ranking:
      if self.state.switch_case_map[p].parent.parent.parent.func_rank < min_method_rank:
        min_method_rank=self.state.switch_case_map[p].parent.parent.parent.func_rank
    
    return min_method_rank>30

  def is_alive(self) -> bool:
    if len(self.state.file_info_map) == 0:
      self.state.is_alive = False
    if self.state.cycle_limit > 0 and self.state.iteration >= self.state.cycle_limit:
      self.state.is_alive = False
    elif self.state.time_limit > 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.is_alive = False
    elif len(self.state.patch_ranking) == 0:
      self.state.is_alive = False
    elif self.state.finish_at_correct_patch and self.patch_str in self.state.correct_patch_str:
      self.state.is_alive = False
    elif self._is_method_over():
      self.state.is_alive=False
    return self.state.is_alive
  def save_result(self) -> None:
    result_handler.save_result(self.state)
  def run_test(self, patch: TbarPatchInfo, test: str) -> Tuple[bool, bool,float,branch_coverage.BranchCoverage]:
    new_env=EnvGenerator.get_new_env_tbar(self.state, patch, test)
    start_time=time.time()
    compilable, run_result, is_timeout = run_test.run_fail_test_d4j(self.state, new_env)
    run_time=time.time()-start_time

    cur_cov=None
    if self.state.instrumenter_classpath!='' and compilable:
      try:
        cur_cov=branch_coverage.parse_cov(self.state.logger,new_env['GREYBOX_RESULT'])
        shutil.copyfile(new_env['GREYBOX_RESULT'],os.path.join(self.state.branch_output,f'{patch.tbar_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt'))
        # if self.state.use_simulation_mode:
        #   shutil.copyfile(new_env['GREYBOX_RESULT'],os.path.join(self.state.branch_output,f'{patch.tbar_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt'))
        os.remove(new_env['GREYBOX_RESULT'])
        
        if patch.tbar_case_info.location=='original':
          self.state.original_branch_cov[test]=cur_cov
      except OSError as e:
        self.state.logger.warning(f"Greybox result not found for {patch.tbar_case_info.location} {test}")
        
    return compilable, run_result, run_time, cur_cov
  def run_test_positive(self, patch: TbarPatchInfo) -> Tuple[bool,float]:
    start_time=time.time()
    run_result = run_test.run_pass_test_d4j(self.state, EnvGenerator.get_new_env_tbar(self.state, patch, ""))
    run_time=time.time()-start_time
    return run_result,run_time
  def initialize(self) -> None:
    self.is_initialized = True
    self.state.logger.info("Initializing...")
    original = self.state.patch_location_map["original"]
    op = TbarPatchInfo(original)
    for neg in self.state.d4j_negative_test.copy():
      if neg in self.state.failed_positive_test:
        self.state.d4j_negative_test.remove(neg)
      else:
        compilable, run_result,_,_ = self.run_test(op, neg)
        if not compilable:
          self.state.logger.warning("Project is not compilable")
          self.state.is_alive = False
          return
        if run_result:
          self.state.logger.warning(f"Removing {neg} from negative test")
          self.state.d4j_negative_test.remove(neg)
      if len(self.state.d4j_negative_test) == 0:
        self.state.logger.critical("No negative test left!!!!")
        self.state.is_alive = False
        return
    if not self.state.skip_valid:
      self.state.logger.info(f"Validating {len(self.state.d4j_positive_test)} pass tests")
      new_env = EnvGenerator.get_new_env_tbar(self.state, op, "")
      new_env = EnvGenerator.get_new_env_d4j_positive_tests(self.state, self.state.d4j_positive_test, new_env)
      run_result, failed_tests = run_test.run_pass_test_d4j_exec(self.state, new_env, self.state.d4j_positive_test)
      if not run_result:
        fail_set = set()
        for ft in failed_tests:
          if ft in self.state.d4j_negative_test or ft in self.state.failed_positive_test:
            continue
          self.state.logger.warning(f"FAIL at {ft}!!!!")
          self.state.d4j_failed_passing_tests.add(ft)
  def run(self) -> None:
    self.initialize()
    if self.state.use_simulation_mode:
      self.run_sim()
      return
    self.state.start_time = time.time()
    self.state.cycle = 0
    while self.is_alive():
      self.state.logger.info(f'[{self.state.cycle}]: executing')
      patch = select_patch.select_patch_tbar_mode(self.state)
      self.patch_str=patch.tbar_case_info.location
      self.state.logger.info(f"Patch: {patch.tbar_case_info.location}")
      self.state.logger.info(f"{patch.file_info.file_name}${patch.func_info.id}${patch.line_info.line_number}")
      pass_exists = False
      result = True
      pass_result = False
      each_result=dict()
      is_compilable = True
      pass_time=0
      coverages:Dict[str,branch_coverage.BranchCoverage]=dict()
      for neg in self.state.d4j_negative_test:
        compilable, run_result,fail_time,cur_cov = self.run_test(patch, neg)
        if not compilable:
          is_compilable = False
        if run_result:
          pass_exists = True
        if not run_result:
          result = False
          each_result[neg]=False
          if self.state.use_partial_validation and self.state.mode==Mode.seapr and \
              self.state.instrumenter_classpath=='': 
            break
        else:
          each_result[neg]=True

        if cur_cov is not None:
          coverages[neg]=cur_cov
        self.state.test_time+=fail_time
        
      #add an entry that maps this patch to its branchess
      if is_compilable:
        self.state.visited_tbar_patch.append(patch.tbar_case_info.location)
        self.state.patch_to_branches_map[patch.tbar_case_info.location] = []
      result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

      if is_compilable or self.state.ignore_compile_error:
        result_handler.update_result_tbar(self.state, patch, pass_exists)
        if result and self.state.use_pass_test:
          pass_result,pass_time = self.run_test_positive(patch)
          self.state.test_time+=pass_time
          result_handler.update_positive_result_tbar(self.state, patch, pass_result)

      if is_compilable or self.state.count_compile_fail:
        self.state.iteration += 1
      result_handler.append_result(self.state, [patch], each_result, pass_result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_tbar(self.state, patch)
  
  def run_sim(self) -> None:
    self.state.start_time = time.time()
    self.state.cycle = 0
    
    while(self.is_alive()):
      self.state.logger.info(f'[{self.state.cycle}]: executing')
      patch = select_patch.select_patch_tbar_mode(self.state)
      self.patch_str=patch.tbar_case_info.location
      self.state.logger.info(f"Patch: {patch.tbar_case_info.location}")
      self.state.logger.info(f"{patch.file_info.file_name}${patch.func_info.id}${patch.line_info.line_number}")
      pass_exists = False
      result = True
      pass_result = False
      is_compilable = True
      pass_time=0
      key = patch.tbar_case_info.location
      if key not in self.state.simulation_data:
        if not self.is_initialized:
          self.initialize()

        each_result=dict()
        coverages:Dict[str,branch_coverage.BranchCoverage]=dict()
        for neg in self.state.d4j_negative_test:
          compilable, run_result,fail_time,cur_cov = self.run_test(patch, neg)
          self.state.test_time+=fail_time
          if not compilable:
            is_compilable = False
          if run_result:
            pass_exists = True
          if not run_result:
            result = False
            each_result[neg]=False
            if self.state.use_partial_validation and self.state.mode==Mode.seapr and \
                self.state.instrumenter_classpath!='':
              break
          else:
            each_result[neg]=True
          if cur_cov is not None:
            coverages[neg]=cur_cov

        #add an entry that maps this patch to its branchess
        if is_compilable:
          self.state.visited_tbar_patch.append(patch.tbar_case_info.location)
          self.state.patch_to_branches_map[patch.tbar_case_info.location] = []
        result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_tbar(self.state, patch, pass_exists)
          if result and self.state.use_pass_test:
            pass_result,pass_time = self.run_test_positive(patch)
            self.state.test_time+=pass_time
            result_handler.update_positive_result_tbar(self.state, patch, pass_result)
        if is_compilable or self.state.count_compile_fail:
          self.state.iteration += 1

      else:
        simapr_result = self.state.simulation_data[key]
        each_result=simapr_result['basic']
        pass_exists = True in each_result.values()
        result = simapr_result['pass_all_fail']
        pass_result = simapr_result['plausible']
        fail_time=simapr_result['fail_time']
        self.state.test_time+=fail_time
        self.state.test_time+=pass_time
        pass_time=simapr_result['pass_time']
        is_compilable=simapr_result['compilable']
        
        coverages:Dict[str,branch_coverage.BranchCoverage]=dict()
        if is_compilable:
          for test in each_result.keys():
            cov_file=os.path.join(self.state.branch_output,
                                  f'{patch.tbar_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt')
            cur_cov=branch_coverage.parse_cov(self.state.logger,cov_file)
            coverages[test]=cur_cov

        #add an entry that maps this patch to its branchess
        if is_compilable:
          self.state.visited_tbar_patch.append(patch.tbar_case_info.location)
          self.state.patch_to_branches_map[patch.tbar_case_info.location] = []

        result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_tbar(self.state, patch, pass_exists)
          if result:
            result_handler.update_positive_result_tbar(self.state, patch, pass_result)
        if is_compilable or self.state.count_compile_fail:
          self.state.iteration += 1
      result_handler.append_result(self.state, [patch], each_result, pass_result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_tbar(self.state, patch)
      
class RecoderLoop(TBarLoop):
  def is_alive(self) -> bool:
    if len(self.state.file_info_map) == 0:
      self.state.is_alive = False
    if self.state.cycle_limit > 0 and self.state.iteration >= self.state.cycle_limit:
      self.state.is_alive = False
    elif self.state.time_limit > 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.is_alive = False
    elif len(self.state.patch_ranking) == 0:
      self.state.is_alive = False
    elif self.state.finish_at_correct_patch and (self.patch_str == self.state.correct_patch_str):
      self.state.is_alive = False
    elif self._is_method_over():
      self.state.is_alive=False
    return self.state.is_alive
  def run_test(self, patch: RecoderPatchInfo, test: str) -> Tuple[bool, bool, float, branch_coverage.BranchCoverage]:
    new_env=EnvGenerator.get_new_env_recoder(self.state, patch, test)
    start_time=time.time()
    compilable, run_result, is_timeout = run_test.run_fail_test_d4j(self.state, new_env)
    run_time=time.time() - start_time

    cur_cov=None
    if self.state.instrumenter_classpath!='' and compilable:
      try:
        cur_cov=branch_coverage.parse_cov(self.state.logger,new_env['GREYBOX_RESULT'])
        #if self.state.use_simulation_mode:
        shutil.copyfile(new_env['GREYBOX_RESULT'],os.path.join(self.state.branch_output,f'{patch.line_info.line_id}-{patch.recoder_case_info.case_id}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt'))
        os.remove(new_env['GREYBOX_RESULT'])

        if patch.recoder_case_info.location=='original':
          self.state.original_branch_cov[test]=cur_cov
      except OSError as e:
        self.state.logger.warning(f"Greybox result not found for {patch.line_info.line_id}-{patch.recoder_case_info.case_id} {test}")

    return compilable, run_result,run_time,cur_cov
  def run_test_positive(self, patch: RecoderPatchInfo) -> Tuple[bool,float]:
    start_time=time.time()
    run_result = run_test.run_pass_test_d4j(self.state, EnvGenerator.get_new_env_recoder(self.state, patch, ""))
    run_time=time.time()-start_time
    return run_result,run_time
  def initialize(self) -> None:
    self.is_initialized = True
    self.state.logger.info("Initializing...")
    original = self.state.patch_location_map["original"]
    op = RecoderPatchInfo(original)
    for neg in self.state.d4j_negative_test.copy():
      compilable, run_result,_,_ = self.run_test(op, neg)
      if not compilable:
        self.state.logger.warning("Project is not compilable")
        self.state.is_alive = False
        return
      if run_result:
        self.state.logger.warning(f"Removing {neg} from negative test")
        self.state.d4j_negative_test.remove(neg)
        if len(self.state.d4j_negative_test) == 0:
          self.state.logger.critical("No negative test left!!!!")
          self.state.is_alive = False
          return
    if not self.state.skip_valid:
      self.state.logger.info(f"Validating {len(self.state.d4j_positive_test)} pass tests")
      new_env = EnvGenerator.get_new_env_recoder(self.state, op, "")
      new_env = EnvGenerator.get_new_env_d4j_positive_tests(self.state, self.state.d4j_positive_test, new_env)
      run_result, failed_tests = run_test.run_pass_test_d4j_exec(self.state, new_env, self.state.d4j_positive_test)
      if not run_result:
        for ft in failed_tests:
          self.state.logger.info("Removing {} from positive test".format(ft))
          self.state.d4j_failed_passing_tests.add(ft)
  def run(self) -> None:
    self.initialize()
    if self.state.use_simulation_mode:
      self.run_sim()
      return
    self.state.start_time = time.time()
    self.state.cycle = 0
    while(self.is_alive()):
      self.state.logger.info(f'[{self.state.cycle}]: executing')
      patch = select_patch.select_patch_recoder_mode(self.state)
      self.state.logger.info(f"Patch: {patch.recoder_case_info.location}")
      self.state.logger.info(f"{patch.file_info.file_name}${patch.func_info.id}${patch.line_info.line_number}")
      self.patch_str = patch.to_str_sw_cs()
      pass_exists = False
      result = True
      pass_result = False
      is_compilable = True
      pass_time=0
      each_result=dict()
      for neg in self.state.d4j_negative_test:
        compilable, run_result,fail_time,cur_cov = self.run_test(patch, neg)
        self.state.test_time+=fail_time
        if not compilable:
          is_compilable = False
        if run_result:
          pass_exists = True
        if not run_result:
          each_result[neg]=False
          result = False
          if self.state.use_partial_validation and self.state.instrumenter_classpath=='' and \
              self.state.mode==Mode.seapr:
            break
        else:
          each_result[neg]=True
          if neg in self.state.original_branch_cov and cur_cov is not None:
            cov_diff=cur_cov.diff(self.state.original_branch_cov[neg])
            for cov in cov_diff:
              self.state.hq_patch_diff_coverage_set.add(cov)
        if is_compilable or self.state.ignore_compile_error:
          if neg in self.state.original_branch_cov and cur_cov is not None:
            cov_diff=cur_cov.diff(self.state.original_branch_cov[neg])
            #result_handler.update_result_branch_coverage_recoder(self.state, patch, cov_diff)

      if is_compilable or self.state.count_compile_fail:
        self.state.iteration += 1
      if is_compilable or self.state.ignore_compile_error:
        result_handler.update_result_recoder(self.state, patch, pass_exists)
        if result and self.state.use_pass_test:
          pass_result,pass_time = self.run_test_positive(patch)
          self.state.test_time+=pass_time
          result_handler.update_positive_result_recoder(self.state, patch, pass_result)
      result_handler.append_result(self.state, [patch], each_result, pass_result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_recoder(self.state, patch)
  def run_sim(self) -> None:
    self.state.start_time = time.time()
    self.state.cycle = 0    
    
    #delete later
    info = {}
    while(self.is_alive()):
      self.state.logger.info(f'[{self.state.cycle}]: executing')
      patch = select_patch.select_patch_recoder_mode(self.state)
      self.state.logger.info(f"Patch: {patch.recoder_case_info.location}")
      self.state.logger.info(f"{patch.file_info.file_name}${patch.func_info.id}${patch.line_info.line_number}")
      self.patch_str = patch.to_str_sw_cs()
      pass_exists = False
      result = True
      pass_result = False
      is_compilable = True
      pass_time=0
      key = patch.recoder_case_info.location
      if key not in self.state.simulation_data:
        if not self.is_initialized:
          self.initialize()
        
        each_result=dict()
        for neg in self.state.d4j_negative_test:
          compilable, run_result,fail_time,cur_cov = self.run_test(patch, neg)
          self.state.test_time+=fail_time
          if not compilable:
            is_compilable = False
          if run_result:
            pass_exists = True
          if not run_result:
            result = False
            each_result[neg]=False
            if self.state.use_partial_validation and self.state.instrumenter_classpath!='' and \
               self.state.mode==Mode.seapr:
              break
          else:
            each_result[neg]=True
            if neg in self.state.original_branch_cov and cur_cov is not None:
              cov_diff=cur_cov.diff(self.state.original_branch_cov[neg])
              for cov in cov_diff:
                self.state.hq_patch_diff_coverage_set.add(cov)
          
          if is_compilable or self.state.ignore_compile_error:
            if neg in self.state.original_branch_cov and cur_cov is not None:
              cov_diff=cur_cov.diff(self.state.original_branch_cov[neg])
              #result_handler.update_result_branch_coverage_recoder(self.state, patch, cov_diff)

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_recoder(self.state, patch, pass_exists)
          if result and self.state.use_pass_test:
            pass_result,pass_time = self.run_test_positive(patch)
            self.state.test_time+=pass_time
            result_handler.update_positive_result_recoder(self.state, patch, pass_result)
      else:
        simapr_result = self.state.simulation_data[key]
        each_result=simapr_result['basic']
        pass_exists = True in each_result.values()
        run_result = simapr_result['pass_all_fail']
        pass_result = simapr_result['plausible']
        fail_time=simapr_result['fail_time']
        pass_time=simapr_result['pass_time']
        self.state.test_time+=fail_time
        self.state.test_time+=pass_time
        is_compilable=simapr_result['compilable']

        count_no_pass=0 #counter for number of test passed
        patch_ochiai=0    
        no_of_branch=0     
        ourData = {}
        interestingBranches = []
        unchangedBranches = []
        interestingPatch=False
        ochiaiDataPath = "/root/project/SimAPR/experiments/alpharepair/result/A_OchiaiData/" + self.state.d4j_buggy_project + ".json"
        if os.path.exists(ochiaiDataPath):
          with open(ochiaiDataPath, "r") as json_file:
            ourData = json.load(json_file)
        for test in each_result.keys():
          interestingPath=False
          # self.state.logger.info(f'Day la cov file')
          cov_file=os.path.join(self.state.branch_output,f'{patch.line_info.line_id}-{patch.recoder_case_info.case_id}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt')
          # self.state.logger.info(f'Day la cov file: {cov_file}')
          if os.path.exists(cov_file):
            # self.state.logger.info(f'Co cov file r ma')
            cur_cov=branch_coverage.parse_cov(self.state.logger,cov_file)
            # self.state.logger.info(f'In ra cur cov: {cur_cov.branch_coverage}')
            
            for branchKey in cur_cov.branch_coverage.keys():
              no_of_branch+=1
              if str(branchKey) in ourData:
                #self.state.logger.info(f'Tung branch: {branchKey}')
                branchOchiai = ourData[str(branchKey)][0]
                #self.state.logger.info(f'Tung ochiai cua branch: {branchOchiai}')
                patch_ochiai += branchOchiai
                # if branchOchiai > patch_ochiai:
                #   patch_ochiai = branchOchiai
            #patch_ochiai = float(patch_ochiai)/float(no_of_branch)
            
            if pass_result:
              gt_path = "/root/project/SimAPR/experiments/alpharepair/result/A_CorrectBranches/" + self.state.d4j_buggy_project + ".txt"
              # with open(gt_path, 'a') as file:
              #   for item in cur_cov.branch_coverage:
              #       file.write(str(item) + '\n')
              #   file.write('\n')
                
            #initilize lists to increment alpha
            fileList = []
            methodList = []
            lineList = []
            if test in self.state.original_branch_cov and cur_cov is not None:
              #get cov_diff
              cov_diff=cur_cov.diff(self.state.original_branch_cov[test])
              
              #extract interesting branches
              interestingBranches = [item[0] for item in cov_diff]
              self.state.logger.info(f'Critical branches: {interestingBranches}')
              
              #extract branches that does not have any change
              cur_cov_set = set(cur_cov.branch_coverage.keys())
              unchangedBranches = cur_cov_set.difference(set(x[0] for x in cov_diff))
              self.state.logger.info(f'Unchanged branches: {unchangedBranches}')
              
              if each_result[test]:  # if HQ patch
                interestingPath=True
                interestingPatch=True
                #self.state.logger.info(f'Patch nay interesting')
                count_no_pass+=1                
                for branch in interestingBranches:
                  #self.state.logger.info(f'Branch interesting patch + interesting: {branch}')
                  if branch not in self.state.branch_map_ochiai:
                    newBranch = BranchInfo(branch, 0,0,0,0)
                    self.state.branch_map_ochiai[branch] = newBranch
                    self.state.branch_map_ochiai[branch].update_ci(self.state.branch_map_ochiai[branch].c_i+1)
                  else: #branchInfo is already created
                    self.state.branch_map_ochiai[branch].update_ci(self.state.branch_map_ochiai[branch].c_i+1)
                    
                for branch in unchangedBranches:
                  #self.state.logger.info(f'Branch interesting patch + unchanged: {branch}')
                  if branch not in self.state.branch_map_ochiai:
                    newBranch = BranchInfo(branch, 0,0,0,0)
                    self.state.branch_map_ochiai[branch] = newBranch
                    self.state.branch_map_ochiai[branch].update_ci(self.state.branch_map_ochiai[branch].c_i+1)
                  else: #branchInfo is already created
                    self.state.branch_map_ochiai[branch].update_ci(self.state.branch_map_ochiai[branch].c_i+1)
                                
                for branchId, branch in self.state.branch_map_ochiai.items():
                  if branchId not in interestingBranches and branchId not in unchangedBranches:
                    self.state.branch_map_ochiai[branchId].update_ni(self.state.branch_map_ochiai[branchId].n_i+1)
                
                #get info of interesting branches
                interestingBranchesInfo = [branch for branch in self.state.branchInfoData if int(branch['id']) in interestingBranches]
                                
                # list that stores the branches that exist in patchable files
                filtered_branch_info = []
                
                # iterate through each interesting branches
                for data_point in interestingBranchesInfo:
                    file_name = ""
                    if ("src/" + data_point['fileName']) in list(self.state.file_info_map.keys()): 
                      file_name = "src/" + data_point['fileName']
                    if ("source/" + data_point['fileName']) in list(self.state.file_info_map.keys()):
                      file_name = "source/" + data_point['fileName']
                    # if there is an interesting branch in one of the patchable files
                    if file_name != "":
                      filtered_branch_info.append({'id': data_point['id'], 'fileName': file_name, 'methodName': data_point["methodName"], 'lineRange': data_point["lineRange"]})
                      # append the file to fileList
                      fileList.append(self.state.file_info_map[file_name])
                      start, end = map(int, data_point["lineRange"].split('-'))
                      for key, funcInfo in self.state.file_info_map[file_name].func_info_map.items():
                        self.state.logger.info(f'{key.split(":")[0]}: keyFunc')
                        self.state.logger.info(f'{data_point["methodName"]}: IFunc')
                        if key.split(":")[0] == data_point["methodName"]:
                          # append the method to the methodList
                          methodList.append(self.state.file_info_map[file_name].func_info_map[key])
                          # append the line to the lineList
                          for key2, lineInfo in self.state.file_info_map[file_name].func_info_map[key].line_info_map.items():
                            if start <= lineInfo.line_number <= end:
                              lineList.append(self.state.file_info_map[file_name].func_info_map[key].line_info_map[key2])
                              
                        # append the "no_function_found" methods within the lineRange of interesting branches
                        if key.startswith("no_function_found"):
                          if start <= funcInfo.begin <= end:
                            methodList.append(self.state.file_info_map[file_name].func_info_map[key])
                            # append the line to the lineList
                            for key3, lineInfo in self.state.file_info_map[file_name].func_info_map[key].line_info_map.items():
                              if lineInfo.line_number == funcInfo.begin:
                                lineList.append(self.state.file_info_map[file_name].func_info_map[key].line_info_map[key3])
                for cov in cov_diff:
                  self.state.hq_patch_diff_coverage_set.add(cov)
              if not interestingPath: #neu kp la interesting path
                for branch in interestingBranches:
                  if branch not in self.state.branch_map_ochiai:
                    newBranch = BranchInfo(branch, 0,0,0,0)
                    self.state.branch_map_ochiai[branch] = newBranch
                    self.state.branch_map_ochiai[branch].update_cu(self.state.branch_map_ochiai[branch].c_u+1)
                  else: #branchInfo is already created
                    self.state.branch_map_ochiai[branch].update_cu(self.state.branch_map_ochiai[branch].c_u+1)
                    
                for branch in unchangedBranches:
                  if branch not in self.state.branch_map_ochiai:
                    newBranch = BranchInfo(branch, 0,0,0,0)
                    self.state.branch_map_ochiai[branch] = newBranch
                    self.state.branch_map_ochiai[branch].update_cu(self.state.branch_map_ochiai[branch].c_u+1)
                  else: #branchInfo is already created
                    self.state.branch_map_ochiai[branch].update_cu(self.state.branch_map_ochiai[branch].c_u+1)
              
              if is_compilable or self.state.ignore_compile_error:
                cov_diff=cur_cov.diff(self.state.original_branch_cov[test])
                result_handler.update_result_branch_coverage_recoder(self.state, patch, cov_diff, fileList, methodList, lineList)
        
        if interestingPatch:
          for branch in interestingBranches:
            self.state.branch_map_ochiai[branch].add_interesting_patch(patch)
            self.state.branch_map_ochiai[branch].add_patch(patch)
          for branch in unchangedBranches:
            self.state.branch_map_ochiai[branch].add_interesting_patch(patch)
            self.state.branch_map_ochiai[branch].add_patch(patch)
        else: #not interesting patch
          for branch in interestingBranches:
            self.state.branch_map_ochiai[branch].add_patch(patch)
          for branch in unchangedBranches:
            self.state.branch_map_ochiai[branch].add_patch(patch)          
          
        if(no_of_branch != 0):
          patch_ochiai = float(patch_ochiai)/float(no_of_branch)
        #Over for loop
        info[patch.recoder_case_info.location] = {'no_test_passed': count_no_pass, 'ochiai_score': patch_ochiai, 'correctPatch': pass_result, 'interesting': interestingPatch}

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_recoder(self.state, patch, pass_exists)
          if run_result:
            result_handler.update_positive_result_recoder(self.state, patch, pass_result)
      if is_compilable or self.state.count_compile_fail:
        self.state.iteration += 1
      result_handler.append_result(self.state, [patch], each_result, pass_result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_recoder(self.state, patch)

    oderered_info = dict(sorted(info.items(), key=lambda x: x[1]['ochiai_score'], reverse=True))
    with open("/root/project/SimAPR/experiments/alpharepair/result/A_OchiaiData/" + self.state.d4j_buggy_project + "-Ochiai.json", "w") as json_file:
        json.dump(oderered_info, json_file, indent=4)
    self.state.logger.info(f'RUN SIM XONG ROIIII')
    ochiaiData = {}
    branch_patch_data = {}
    for branchID, branch in self.state.branch_map_ochiai.items():
      if branch.ochiai != float('inf'):
        ochiaiData[branchID] = [branch.ochiai, branch.c_i, branch.c_u, branch.n_i, branch.n_u]
        branch_patch_data[branchID] = {'ochiai_score': self.state.branch_map_ochiai[branchID].ochiai, 'prob': self.state.branch_map_ochiai[branchID].calculate_prob(), 'int_patch_len': len(self.state.branch_map_ochiai[branchID].interesting_patch_list), 'patch_pool': len(self.state.branch_map_ochiai[branchID].patch_list)}
    
    ochiaiDataPath = "/root/project/SimAPR/experiments/alpharepair/result/A_OchiaiData/" + self.state.d4j_buggy_project + ".json"
    with open(ochiaiDataPath, "w") as json_file:
        json.dump(ochiaiData, json_file, indent=4)
              
    oderered_info_branch_patch = dict(sorted(branch_patch_data.items(), key=lambda x: x[1]['ochiai_score'], reverse=True))
    ochiaiPatchDataPath = "/root/project/SimAPR/experiments/alpharepair/result/A_OchiaiData/" + self.state.d4j_buggy_project + "-Ochiai-Patch.json"
    with open(ochiaiPatchDataPath, "w") as json_file:
        json.dump(oderered_info_branch_patch, json_file, indent=4)

class PraPRLoop(TBarLoop):
  def _is_method_over(self) -> bool:
    """Check the ranks of every remaining methods are over then 30"""
    if not self.state.finish_top_method: return False
    
    min_method_rank=10000 # Some large rank
    for p in self.state.patch_ranking:
      if self.state.switch_case_map[p].parent.parent.parent.func_rank < min_method_rank:
        min_method_rank=self.state.switch_case_map[p].parent.parent.parent.func_rank
    
    return min_method_rank>30

  def is_alive(self) -> bool:
    if len(self.state.file_info_map) == 0:
      self.state.is_alive = False
    if self.state.cycle_limit > 0 and self.state.iteration >= self.state.cycle_limit:
      self.state.is_alive = False
    elif self.state.time_limit > 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.is_alive = False
    elif len(self.state.patch_ranking) == 0:
      self.state.is_alive = False
    elif self.state.finish_at_correct_patch and self.patch_str in self.state.correct_patch_str:
      self.state.is_alive = False
    elif self._is_method_over():
      self.state.is_alive=False
    return self.state.is_alive
  def save_result(self) -> None:
    result_handler.save_result(self.state)
  def run(self) -> None:
    assert self.state.use_simulation_mode,'PraPR needs cache files always'
    self.run_sim()
  
  def run_sim(self) -> None:
    self.state.start_time = time.time()
    self.state.cycle = 0
    while(self.is_alive()):
      self.state.logger.info(f'[{self.state.cycle}]: executing')
      patch = select_patch.select_patch_tbar_mode(self.state)
      self.patch_str=patch.tbar_case_info.location
      self.state.logger.info(f"Patch: {patch.tbar_case_info.location}")
      self.state.logger.info(f"{patch.file_info.file_name}${patch.func_info.id}${patch.line_info.line_number}")
      pass_exists = False
      result = True
      pass_result = False
      is_compilable = True
      pass_time=0
      key = patch.tbar_case_info.location

      simapr_result = self.state.simulation_data[key]
      pass_exists = simapr_result['basic']
      result = simapr_result['pass_all_fail']
      pass_result = simapr_result['plausible']
      fail_time=simapr_result['fail_time']
      self.state.test_time+=fail_time
      self.state.test_time+=pass_time
      pass_time=simapr_result['pass_time']
      is_compilable=simapr_result['compilable']
      if is_compilable or self.state.ignore_compile_error:
        result_handler.update_result_tbar(self.state, patch, pass_exists)
        if result:
          result_handler.update_positive_result_tbar(self.state, patch, pass_result)
      if is_compilable or self.state.count_compile_fail:
        self.state.iteration += 1
      result_handler.append_result(self.state, [patch], pass_exists, pass_result, result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_tbar(self.state, patch)
