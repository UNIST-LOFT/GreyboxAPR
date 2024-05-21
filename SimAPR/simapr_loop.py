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
    """
    Check the ranks of every remaining methods are over then 30
    """
    if not self.state.finish_top_method: return False
    
    min_method_rank=10000 # Some large rank
    for p in self.state.patch_ranking:
      if self.state.switch_case_map[p].parent.parent.parent.func_rank < min_method_rank:
        min_method_rank=self.state.switch_case_map[p].parent.parent.parent.func_rank
    
    return min_method_rank>30

  def is_alive(self) -> bool:
    if len(self.state.file_info_map) == 0:
      self.state.logger.info("finish because of len(self.state.file_info_map) == 0")
      self.state.is_alive = False
    elif self.state.cycle_limit > 0 and self.state.iteration >= self.state.cycle_limit and \
          self.state.time_limit > 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.logger.info("finish because of cycle limit and time limit")
      self.state.is_alive = False
    elif self.state.time_limit <= 0 and self.state.cycle_limit > 0 and self.state.iteration >= self.state.cycle_limit:
      self.state.logger.info("finish because of cycle limit")
      self.state.is_alive = False
    elif self.state.time_limit > 0 and self.state.cycle_limit <= 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.logger.info("finish because of time limit")
      self.state.is_alive = False
    elif len(self.state.patch_ranking) == 0:
      self.state.logger.info("finish because of len(self.state.patch_ranking) == 0")
      self.state.is_alive = False
    elif self.state.finish_at_correct_patch and self.patch_str in self.state.correct_patch_str:
      self.state.logger.info("finish because of self.state.finish_at_correct_patch and self.patch_str in self.state.correct_patch_str")
      self.state.is_alive = False
    elif self._is_method_over():
      self.state.logger.info("finish because of self._is_method_over()")
      self.state.is_alive=False
    return self.state.is_alive
  
  def save_result(self) -> None:
    result_handler.save_result(self.state)
    
  def run_test(self, patch: TbarPatchInfo, test: str, get_branch_cov:bool=False) -> Tuple[bool, bool,float,branch_coverage.BranchCoverage]:
    """
    TODO: need more description
    _summary_

    Args:
        patch (TbarPatchInfo): _description_
        test (str): _description_

    Returns:
        Tuple[bool, bool,float,branch_coverage.BranchCoverage]: _description_
    """
    cur_cov=None
    new_env=EnvGenerator.get_new_env_tbar(self.state, patch, test)
    start_time=time.time()
    compilable, run_result, is_timeout = run_test.run_fail_test_d4j(self.state, new_env)
    run_time=time.time()-start_time
    
    if self.state.mode == Mode.greybox and (run_result or get_branch_cov):
      if not self.state.only_get_test_time_data_mode:
        new_env=EnvGenerator.get_new_env_tbar(self.state, patch, test,instrument=True)
        self.state.logger.info("Running the test again with full instrumentation.")
        _, _, _ = run_test.run_fail_test_d4j(self.state, new_env)

      try:
        cur_cov=branch_coverage.parse_cov(self.state.logger,new_env['GREYBOX_RESULT'])
        dest_file_name = os.path.join(self.state.branch_output,f'{patch.tbar_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt')
        self.state.logger.info(f"branch dest: {dest_file_name}")
        os.makedirs(os.path.dirname(dest_file_name), exist_ok=True)
        shutil.copyfile(new_env['GREYBOX_RESULT'],dest_file_name)
        os.remove(new_env['GREYBOX_RESULT'])
        
        if patch.tbar_case_info.location=='original':
          self.state.original_branch_cov[test]=cur_cov
      except OSError as e:
        self.state.logger.warning(f"Greybox result not found for {patch.tbar_case_info.location} {test}. expected location: {new_env['GREYBOX_RESULT']}")
        
    return compilable, run_result, run_time, cur_cov
      
  def run_test_positive(self, patch: TbarPatchInfo) -> Tuple[bool,float]:
    start_time=time.time()
    new_env = EnvGenerator.get_new_env_tbar(self.state, patch, "")
    run_result = run_test.run_pass_test_d4j(self.state, new_env)
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
        compilable, run_result,_,_ = self.run_test(op, neg,get_branch_cov=True)
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
    """
    Run the loop.
    """
    
    self.initialize()

    if self.state.only_get_test_time_data_mode:
      self.get_run_time_data()
      return
    
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
      coverages:Dict[str,branch_coverage.BranchCoverage]=dict() # key: test name, value: branch coverage(contains a dict that shows how many times each branch has been taken.)
      self.state.new_critical_list = []
      
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
          self.state.logger.debug(f"each result neg name: {neg}")
          each_result[neg]=True

        if cur_cov is not None:
          self.state.logger.debug(f"coverages neg name: {neg}")
          coverages[neg]=cur_cov
          
        self.state.test_time+=fail_time
        
      #add an entry that maps this patch to its branches
      if is_compilable:
        self.state.visited_tbar_patch.append(patch.tbar_case_info.location)
        self.state.patch_to_branches_map[patch.tbar_case_info.location] = []
        
      if self.state.mode==Mode.greybox:
        # if self.state.optimized_instrumentation:
        #   if pass_exists or self.state.critical_branch_up_down_manager.upDownDict:
        #     self.state.logger.info("result handler is called")
        #     result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)
        #   else:
        #     self.state.logger.info(f"what the hell{pass_exists}, {self.state.critical_branch_up_down_manager.upDownDict}")
        # else:
          # TODO: wait a minute... pass result is ALWAYS False?? what is going on?
          # well never mind. the function below doesn't even use the pass_result.
        self.state.logger.debug("result handler is called")
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
      self.state.new_critical_list = []
      # checks if there is a cached data
      if key not in self.state.simulation_data or 'fail_time' not in self.state.simulation_data[key]:
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
        if self.state.mode==Mode.greybox:
          result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_tbar(self.state, patch, pass_exists)
          if result and self.state.use_pass_test:
            pass_result,pass_time = self.run_test_positive(patch)
            self.state.test_time+=pass_time
            result_handler.update_positive_result_tbar(self.state, patch, pass_result)
        if is_compilable or self.state.count_compile_fail:
          self.state.iteration += 1

      else: # use cached results
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
        greybox_done=simapr_result['done_greybox'] if 'done_greybox' in simapr_result else False
        
        #add an entry that maps this patch to its branchess
        if is_compilable:
          self.state.visited_tbar_patch.append(patch.tbar_case_info.location)
          self.state.patch_to_branches_map[patch.tbar_case_info.location] = []

        if self.state.mode==Mode.greybox:
          coverages:Dict[str,branch_coverage.BranchCoverage]=dict()
          if is_compilable:
            for test in each_result.keys():
              cov_file=os.path.join(self.state.branch_output,
                                    f'{patch.tbar_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt')
              if not os.path.exists(cov_file) and not greybox_done:
                # Retry if greybox not done yet
                compilable, run_result,fail_time,cur_cov = self.run_test(patch, test,get_branch_cov=True)
              if os.path.exists(cov_file):
                cur_cov=branch_coverage.parse_cov(self.state.logger,cov_file)
                coverages[test]=cur_cov
              else:
                self.state.logger.warning(f"Greybox result not found for {patch.tbar_case_info.location} {test}. expected location: {cov_file}")
          result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_tbar(self.state, patch, pass_exists)
          if result:
            result_handler.update_positive_result_tbar(self.state, patch, pass_result)
        if is_compilable or self.state.count_compile_fail:
          self.state.iteration += 1
      result_handler.append_result(self.state, [patch], each_result, pass_result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_tbar(self.state, patch)
      
  def get_run_time_data(self):
    self.state.logger.info("get_run_time_data_mode")
    project_name = self.state.work_dir.split('/')[-1]
    with open(os.path.join(self.state.test_time_data_location, "passed_patch_list.json"), "r") as f:
      self.state.logger.info("reading "+os.path.join(self.state.test_time_data_location, "passed_patch_list.json"))
      patch_list_data = json.load(f)
      patch_list = patch_list_data[project_name]
    if os.path.exists(os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json")):
      with open(os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"), "r") as f:
        self.state.logger.info("reading "+os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"))
        test_time_data = json.load(f)
    else:
      test_time_data = {}
    if self.state.mode.name not in list(test_time_data.keys()):
      test_time_data[self.state.mode.name] = {}
    for patch in patch_list:
      self.state.logger.info("finding patch:"+ patch)
      if patch not in list(test_time_data[self.state.mode.name].keys()):
        found_patch = False
        for fl in list(self.state.java_patch_ranking.keys()):
          for case_info in self.state.java_patch_ranking[fl]:
            if case_info.location == patch:
              found_patch == True
              test_time_data[self.state.mode.name][patch] = {}
              for neg in self.state.d4j_negative_test:
                self.state.logger.info("run test: "+ neg)
                compilable, run_result,fail_time,cur_cov = self.run_test(TbarPatchInfo(case_info), neg)
                test_time_data[self.state.mode.name][patch][neg] = fail_time
              break
          if found_patch:
            break
      else:
        self.state.logger.info("test time data already exists. "+ patch)
    with open(os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"), "w") as f:
      self.state.logger.info("writing "+os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"))
      json.dump(test_time_data, f, indent=2)


class RecoderLoop(TBarLoop):
  def is_alive(self) -> bool:
    if len(self.state.file_info_map) == 0:
      self.state.logger.info("finish because of len(self.state.file_info_map) == 0")
      self.state.is_alive = False
    elif self.state.cycle_limit > 0 and self.state.iteration >= self.state.cycle_limit and \
          self.state.time_limit > 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.logger.info("finish because of cycle limit and time limit")
      self.state.is_alive = False
    elif self.state.cycle_limit > 0 and self.state.time_limit <= 0 and self.state.iteration >= self.state.cycle_limit:
      self.state.logger.info("finish because of cycle limit")
      self.state.is_alive = False
    elif self.state.time_limit > 0 and self.state.cycle_limit <= 0 and (self.state.select_time+self.state.test_time) > self.state.time_limit:
      self.state.logger.info("finish because of time limit")
      self.state.is_alive = False
    elif len(self.state.patch_ranking) == 0:
      self.state.logger.info("finish because of len(self.state.patch_ranking) == 0")
      self.state.is_alive = False
    elif self.state.finish_at_correct_patch and (self.patch_str == self.state.correct_patch_str):
      self.state.logger.info("finish because of self.state.finish_at_correct_patch and self.patch_str in self.state.correct_patch_str")
      self.state.is_alive = False
    elif self._is_method_over():
      self.state.logger.info("finish because of self._is_method_over()")
      self.state.is_alive=False
    return self.state.is_alive
  
  def run_test(self, patch: RecoderPatchInfo, test: str, get_branch_cov:bool=False) -> Tuple[bool, bool, float, branch_coverage.BranchCoverage]:
    cur_cov=None
    new_env=EnvGenerator.get_new_env_recoder(self.state, patch, test)
    start_time=time.time()
    compilable, run_result, is_timeout = run_test.run_fail_test_d4j(self.state, new_env)
    run_time=time.time()-start_time
    
    if self.state.mode == Mode.greybox and (run_result or get_branch_cov):
      if not self.state.only_get_test_time_data_mode:
        new_env=EnvGenerator.get_new_env_recoder(self.state, patch, test,instrument=True)
        self.state.logger.info("Running the test again with full instrumentation.")
        _, _, _ = run_test.run_fail_test_d4j(self.state, new_env)

      try:
        cur_cov=branch_coverage.parse_cov(self.state.logger,new_env['GREYBOX_RESULT'])
        self.state.logger.info("everything is fine")
        dest_file_name = os.path.join(self.state.branch_output,f'{patch.recoder_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt')
        os.makedirs(os.path.dirname(dest_file_name), exist_ok=True)
        shutil.copyfile(new_env['GREYBOX_RESULT'],dest_file_name)
        os.remove(new_env['GREYBOX_RESULT'])

        if patch.recoder_case_info.location=='original':
          self.state.original_branch_cov[test]=cur_cov
      except OSError as e:
        self.state.logger.error(e)
        self.state.logger.warning(f"Greybox result not found for {patch.recoder_case_info.location} {test}. expected location: {new_env['GREYBOX_RESULT']}")

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
      compilable, run_result,_,_ = self.run_test(op, neg,get_branch_cov=True)
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
          if ft in self.state.d4j_negative_test or ft in self.state.failed_positive_test:
            continue
          self.state.logger.info("Removing {} from positive test".format(ft))
          self.state.d4j_failed_passing_tests.add(ft)

  def run(self) -> None:
    self.initialize()
    if self.state.only_get_test_time_data_mode:
      self.get_run_time_data()
      return
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
      coverages:Dict[str,branch_coverage.BranchCoverage]=dict()
      self.state.new_critical_list = []
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

        if cur_cov is not None:
          coverages[neg]=cur_cov

      if is_compilable:
        self.state.visited_tbar_patch.append(patch.recoder_case_info.location)
        self.state.patch_to_branches_map[patch.recoder_case_info.location] = []
      if self.state.mode==Mode.greybox:
        result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

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
      self.state.new_critical_list = []
      if key not in self.state.simulation_data or 'fail_time' not in self.state.simulation_data[key]:
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
            if self.state.use_partial_validation and self.state.instrumenter_classpath!='' and \
               self.state.mode==Mode.seapr:
              break
          else:
            each_result[neg]=True

          if cur_cov is not None:
            coverages[neg]=cur_cov

        #add an entry that maps this patch to its branchess
        if is_compilable:
          self.state.visited_tbar_patch.append(patch.recoder_case_info.location)
          self.state.patch_to_branches_map[patch.recoder_case_info.location] = []
        if self.state.mode==Mode.greybox:
          result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

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
        greybox_done=simapr_result['done_greybox'] if 'done_greybox' in simapr_result else False

        #add an entry that maps this patch to its branchess
        if is_compilable:
          self.state.visited_tbar_patch.append(patch.recoder_case_info.location)
          self.state.patch_to_branches_map[patch.recoder_case_info.location] = []

        if self.state.mode==Mode.greybox:
          coverages:Dict[str,branch_coverage.BranchCoverage]=dict()
          if is_compilable:
            for test in each_result.keys():
              if each_result[test]:
                cov_file=os.path.join(self.state.branch_output,
                                      f'{patch.recoder_case_info.location.replace("/","#")}_{test.split(".")[-2]}.{test.split(".")[-1]}.txt')
                if not os.path.exists(cov_file) and not greybox_done:
                  # Retry if greybox not done yet
                  compilable, run_result,fail_time,cur_cov = self.run_test(patch, test,get_branch_cov=True)
                if os.path.exists(cov_file):
                  cur_cov=branch_coverage.parse_cov(self.state.logger,cov_file)
                  coverages[test]=cur_cov
                else:
                  self.state.logger.warning(f"Greybox result not found for {patch.recoder_case_info.location} {test}. expected location: {cov_file}")
          result_handler.update_result_branch(self.state,patch,coverages,is_compilable,each_result,pass_result)

        if is_compilable or self.state.ignore_compile_error:
          result_handler.update_result_recoder(self.state, patch, pass_exists)
          if run_result:
            result_handler.update_positive_result_recoder(self.state, patch, pass_result)
      if is_compilable or self.state.count_compile_fail:
        self.state.iteration += 1
      result_handler.append_result(self.state, [patch], each_result, pass_result, is_compilable,fail_time,pass_time)
      result_handler.remove_patch_recoder(self.state, patch)

  def get_run_time_data(self):
    self.state.logger.info("get_run_time_data_mode")
    project_name = self.state.work_dir.split('/')[-1]
    with open(os.path.join(self.state.test_time_data_location, "passed_patch_list.json"), "r") as f:
      self.state.logger.info("reading "+os.path.join(self.state.test_time_data_location, "passed_patch_list.json"))
      patch_list_data = json.load(f)
      patch_list = patch_list_data[project_name]
    if os.path.exists(os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json")):
      with open(os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"), "r") as f:
        self.state.logger.info("reading "+os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"))
        test_time_data = json.load(f)
    else:
      test_time_data = {}
    if self.state.mode.name not in list(test_time_data.keys()):
      test_time_data[self.state.mode.name] = {}
    for patch in patch_list:
      self.state.logger.info("finding patch:"+ patch)
      if patch not in list(test_time_data[self.state.mode.name].keys()):
        found_patch = False
        for fl in list(self.state.java_patch_ranking.keys()):
          for case_info in self.state.java_patch_ranking[fl]:
            if case_info.location == patch:
              found_patch == True
              test_time_data[self.state.mode.name][patch] = {}
              for neg in self.state.d4j_negative_test:
                self.state.logger.info("run test: "+ neg)
                compilable, run_result,fail_time,cur_cov = self.run_test(RecoderPatchInfo(case_info), neg)
                test_time_data[self.state.mode.name][patch][neg] = fail_time
              break
          if found_patch:
            break
      else:
        self.state.logger.info("test time data already exists. "+ patch)
    with open(os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"), "w") as f:
      self.state.logger.info("writing "+os.path.join(self.state.test_time_data_location, f"{project_name}_test_time_data.json"))
      json.dump(test_time_data, f, indent=2)

