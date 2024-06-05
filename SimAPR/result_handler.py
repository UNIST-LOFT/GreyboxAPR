from core import *
from typing import List
import json

def get_ochiai(s_h: float, s_l: float, d_h: float, d_l: float) -> float:
  if s_h == 0.0:
    return 0.0
  return s_h / (((s_h + d_h) * (s_h + s_l)) ** 0.5)

def save_result(state: GlobalState) -> None:
  state.last_save_time = time.time()
  result_file = os.path.join(state.out_dir, "simapr-result.json")

  state.logger.info(f"Saving result to {result_file}")
  with open(result_file, 'w') as f:
    json.dump(state.simapr_result, f, indent=2)

  if state.use_simulation_mode:
    # Save cached result to file
    with open(state.prev_data, "w") as f:
      json.dump(state.simulation_data, f, indent=2)

  # if (state.mode == Mode.greybox and state.optimized_instrumentation and state.use_simulation_mode) or (state.mode == Mode.casino and state.no_instrumentation_time_data != ""):
  #   file_path = os.path.join(state.no_instrumentation_time_data_output, "no_instrumentation_time_data.json")
  #   if not (os.path.exists(file_path)):
  #     with open(file_path, 'w') as f:
  #       json.dump(state.no_instrumentation_time_data, f, indent=2)

# Append result list, save result to file periodically
def append_result(state: GlobalState, selected_patch: List[Union[TbarPatchInfo,RecoderPatchInfo]], test_result: Dict[str,bool],pass_test_result:bool=False,compilable: bool = True,fail_time:float=0.0,pass_time:float=0.0) -> None:
  """
    fail_time: second
    pass_time: second
  """
  save_interval = 1800 # 30 minutes
  tm = time.time()
  tm_interval=state.select_time+state.test_time
  result = Result(state.cycle,state.iteration,tm_interval, selected_patch, 
          True in test_result.values(), pass_test_result, False not in test_result.values(), compilable=compilable)
  
  if result.result:
    state.total_passed_patch+=1
  if result.pass_result:
    state.total_plausible_patch+=1
  state.total_searched_patch+=1
  obj = result.to_json_object(state.total_searched_patch,state.total_passed_patch,state.total_plausible_patch, new_critical_branch = state.new_critical_list)
  state.simapr_result.append(obj)
  state.used_patch.append(result)

  if state.use_simulation_mode:
    # Cache test result if option used
    for patch in selected_patch:
      # For Java, case_info is tbar_case_info
      if state.tool_type==ToolType.TEMPLATE:
        case_info = patch.tbar_case_info
      else:
        case_info = patch.recoder_case_info
      append_java_cache_result(state,case_info,test_result,pass_test_result,compilable,fail_time,pass_time,state.mode==Mode.greybox)
  
  if (tm - state.last_save_time) > save_interval:
    save_result(state)

def update_result_tbar(state: GlobalState, selected_patch: TbarPatchInfo, result: bool) -> None:
  """
  TODO: need more description

  Args:
      state (GlobalState): _description_
      selected_patch (TbarPatchInfo): _description_
      result (bool): True if the test is passed, but there is 
  """
  selected_patch.update_result(result, PT.ALPHA_INCREASE, PT.BETA_INCREASE, state.use_exp_alpha)
  if result:
    state.total_basic_patch += 1
    print(f'black-box alpha updated')
    selected_patch.tbar_type_info.children_basic_patches+=1
    print(f'black-box alpha updated')
    selected_patch.line_info.children_basic_patches+=1
    print(f'black-box alpha updated')
    selected_patch.func_info.children_basic_patches+=1
    print(f'black-box alpha updated')
    selected_patch.file_info.children_basic_patches+=1
    print(f'black-box alpha updated')
    selected_patch.tbar_type_info.consecutive_fail_count=0
    selected_patch.line_info.consecutive_fail_count=0
    selected_patch.func_info.consecutive_fail_count=0
    selected_patch.file_info.consecutive_fail_count=0
  else:
    selected_patch.tbar_type_info.consecutive_fail_count+=1
    selected_patch.line_info.consecutive_fail_count+=1
    selected_patch.func_info.consecutive_fail_count+=1
    selected_patch.file_info.consecutive_fail_count+=1
    selected_patch.tbar_type_info.consecutive_fail_plausible_count+=1
    selected_patch.line_info.consecutive_fail_plausible_count+=1
    selected_patch.func_info.consecutive_fail_plausible_count+=1
    selected_patch.file_info.consecutive_fail_plausible_count+=1

  state.previous_score=selected_patch.line_info.fl_score

  if state.mode == Mode.seapr:
    # Optimization: for default SeAPR, we use cluster to update the result
    if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
      for func_info in state.func_list:
        if selected_patch.func_info == func_info: # same function with selected patch
          func_info.same_seapr_pf.update(result, 1)
        else:
          func_info.diff_seapr_pf.update(result, 1)
    else:
      seapr_list_for_sort=[]
      for loc in state.patch_ranking:
        ts: TbarCaseInfo = state.switch_case_map[loc]
        tbar_type_info = ts.parent
        line_info = tbar_type_info.parent
        func_info = line_info.parent
        file_info = func_info.parent
          
        is_share = False
        same_pattern = False
        if state.seapr_layer == SeAPRMode.FILE:
          if selected_patch.file_info == file_info:
            is_share = True
        elif state.seapr_layer == SeAPRMode.FUNCTION:
          if selected_patch.func_info == func_info:
            is_share = True
        elif state.seapr_layer == SeAPRMode.LINE:
          if selected_patch.line_info == line_info:
            is_share = True
        if selected_patch.tbar_type_info.mutation == tbar_type_info.mutation:
          same_pattern = True
        if is_share:
          ts.same_seapr_pf.update(result, 1)
        else:
          ts.diff_seapr_pf.update(result, 1)
        if state.use_pattern and result and same_pattern:
          ts.same_seapr_pf.update(True, 1)

        seapr_list_for_sort.append((1.-get_ochiai(ts.same_seapr_pf.pass_count, ts.same_seapr_pf.fail_count,
            ts.diff_seapr_pf.pass_count, ts.diff_seapr_pf.fail_count),ts.patch_rank,ts.location))

    if state.debug_mode:
      # Sort seapr list, for debugging
      cor_set=set()
      for cor_str in state.correct_patch_list:
        if type(state.switch_case_map[cor_str])==TbarCaseInfo:
          cor_set.add(state.switch_case_map[cor_str].parent.parent.parent)
        else:
          cor_set.add(state.switch_case_map[cor_str].parent.parent.parent.parent)

        if selected_patch.func_info in cor_set:
          if not result:
            state.logger.debug('Misguide type L')
          else:
            state.logger.debug('Correct guide H')
        elif selected_patch.func_info not in cor_set:
          if result:
            state.logger.debug('Misguide type H')
          else:
            state.logger.debug('Correct guide L')

def update_positive_result_tbar(state: GlobalState, selected_patch: TbarPatchInfo, result: bool) -> None:
  if result:
    selected_patch.tbar_type_info.children_plausible_patches+=1
    selected_patch.line_info.children_plausible_patches+=1
    selected_patch.func_info.children_plausible_patches+=1
    selected_patch.file_info.children_plausible_patches+=1
    selected_patch.tbar_type_info.consecutive_fail_plausible_count=0
    selected_patch.line_info.consecutive_fail_plausible_count=0
    selected_patch.func_info.consecutive_fail_plausible_count=0
    selected_patch.file_info.consecutive_fail_plausible_count=0
  else:
    selected_patch.tbar_type_info.consecutive_fail_plausible_count+=1
    selected_patch.line_info.consecutive_fail_plausible_count+=1
    selected_patch.func_info.consecutive_fail_plausible_count+=1
    selected_patch.file_info.consecutive_fail_plausible_count+=1
    
  selected_patch.update_result_positive(result, PT.ALPHA_INCREASE, PT.BETA_INCREASE,state.use_exp_alpha)

def remove_patch_tbar(state: GlobalState, selected_patch: TbarPatchInfo) -> None:
  selected_patch.remove_patch(state)

def update_result_recoder(state: GlobalState, selected_patch: RecoderPatchInfo, result: bool) -> None:
  selected_patch.update_result(result, PT.ALPHA_INCREASE, PT.BETA_INCREASE,state.use_exp_alpha)
  if result:
    state.total_basic_patch += 1
    print(f'black-box alpha updated')
    selected_patch.line_info.children_basic_patches += 1
    print(f'black-box alpha updated')
    selected_patch.func_info.children_basic_patches += 1
    print(f'black-box alpha updated')
    selected_patch.file_info.children_basic_patches += 1
    print(f'black-box alpha updated')
    selected_patch.line_info.consecutive_fail_count = 0
    selected_patch.func_info.consecutive_fail_count = 0
    selected_patch.file_info.consecutive_fail_count = 0
  else:
    selected_patch.line_info.consecutive_fail_count += 1
    selected_patch.func_info.consecutive_fail_count += 1
    selected_patch.file_info.consecutive_fail_count += 1
    selected_patch.line_info.consecutive_fail_plausible_count += 1
    selected_patch.func_info.consecutive_fail_plausible_count += 1
    selected_patch.file_info.consecutive_fail_plausible_count += 1

  state.previous_score=selected_patch.line_info.fl_score

  if state.mode == Mode.seapr:
    # Optimization: for default SeAPR, we use cluster to update the result
    if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
      for func_info in state.func_list:
        if selected_patch.func_info == func_info:  # same function with selected patch
          func_info.same_seapr_pf.update(result, 1)
        else:
          func_info.diff_seapr_pf.update(result, 1)
    else:
      for loc in state.patch_ranking:
        rc: RecoderCaseInfo = state.switch_case_map[loc]
        line_info = rc.parent
        func_info = line_info.parent
        file_info = func_info.parent
        is_share = False
        if state.seapr_layer == SeAPRMode.FILE:
          if selected_patch.file_info == file_info:
            is_share = True
        elif state.seapr_layer == SeAPRMode.FUNCTION:
          if selected_patch.func_info == func_info:
            is_share = True
        elif state.seapr_layer == SeAPRMode.LINE:
          if selected_patch.line_info == line_info:
            is_share = True
        if is_share:
          rc.same_seapr_pf.update(result, 1)
        else:
          rc.diff_seapr_pf.update(result, 1)

def update_positive_result_recoder(state: GlobalState, selected_patch: RecoderPatchInfo, result: bool) -> None:
  if result:
    selected_patch.line_info.children_plausible_patches += 1
    selected_patch.func_info.children_plausible_patches += 1
    selected_patch.file_info.children_plausible_patches += 1
    selected_patch.line_info.consecutive_fail_plausible_count = 0
    selected_patch.func_info.consecutive_fail_plausible_count = 0
    selected_patch.file_info.consecutive_fail_plausible_count = 0
  else:
    selected_patch.line_info.consecutive_fail_plausible_count += 1
    selected_patch.func_info.consecutive_fail_plausible_count += 1
    selected_patch.file_info.consecutive_fail_plausible_count += 1
  selected_patch.update_result_positive(result, PT.ALPHA_INCREASE, PT.BETA_INCREASE,state.use_exp_alpha)

def remove_patch_recoder(state: GlobalState, selected_patch: RecoderPatchInfo) -> None:
  selected_patch.remove_patch(state)

def update_result_branch_coverage_tbar(state: GlobalState, selected_patch:TbarPatchInfo, coverage_diff:Set[Tuple[int,int]]):  
  total_same=0
  for cov in coverage_diff:
    if cov in state.hq_patch_diff_coverage_set:
      total_same+=1
      
  if total_same>0:
    state.diff_patch_num+=1
    # TODO: Do we need exp_alpha?
    selected_patch.file_info.coverage_info.update(True, total_same,0)
    selected_patch.func_info.coverage_info.update(True, total_same,0)
    selected_patch.line_info.coverage_info.update(True, total_same,0)
    selected_patch.tbar_type_info.coverage_info.update(True, total_same,0)
  
def update_result_branch_coverage_recoder(state: GlobalState, selected_patch:RecoderPatchInfo, coverage_diff:Set[Tuple[int,int]]):
  total_same=0
  for cov in coverage_diff:
    if cov in state.hq_patch_diff_coverage_set:
      total_same+=1

  if total_same>0:
    state.diff_patch_num+=1
    selected_patch.file_info.coverage_info.update(True, total_same,0)
    selected_patch.func_info.coverage_info.update(True, total_same,0)
    selected_patch.line_info.coverage_info.update(True, total_same,0)
    
def update_result_branch(state:GlobalState,selected_patch:Union[TbarPatchInfo,RecoderPatchInfo],branch_coverage:Dict[str,branch_coverage.BranchCoverage],
                         is_compilable:bool,each_result:Dict[str,bool],pass_result:bool):
  """
  This function is used for the GreyBox Approach of the Casino.
  It deals with the branch data of patched program runs when each test has end.
  This function basically handle the every patch testing result that has to be done for the GreyBox approach. 
  
  This function does the jobs below.
  - Finds critical branch.
    - For each failing test, if the test for patched program is passed, the branches that has different count to that of buggy program is now critical branches
  - Compare the count of each branches between the buggy(=original) program and the patched one, and update the branch data in GlobalState and each PatchTreeNode that is ancester of patch.
    - Critical branches are saved as state.critical_branches:Dict[str, Set[Tuple[int,int]]], where the tuple[0] is the branch index and tuple[1] is difference. 
    - examples: 
        for some branch[1] and test_A, if branch[1] is taken 5 time in patched version and 8 time in original buggy version, then (1, -3) becomes an element of critical_branches[test_A].
        for some branch[0] and test_B, if branch[0] is taken 7 time in patched version and 0 time in original buggy version, then (0, 7) becomes an element of critical_branches[test_B].
  - However, if the patch is not compilable (is_compilable == false), this function does nothing.
  
  This function is composed of following parts.
  - A loop for comparing the branches of the buggy program and the patched program to find out the critical branches and save the branch informations.

  Args:
      state (GlobalState): The global state. It is a object that saves every information of total run of SimAPR and is used just like a singleton.
      selected_patch (Union[TbarPatchInfo,RecoderPatchInfo]): Patch information. It varies depending on the 
      branch_coverage (Dict[str,branch_coverage.BranchCoverage]): branch
      is_compilable (bool): whether the patched program is compilable.
      each_result (Dict[str,bool]): The test results of each test on the patched program. Key(:str) is the name of a test, and value(:bool) is the result (true if the test is passedm otherwise false).
      pass_result (bool): whether the all tests has passed. It has to be true when every value of 'each_result(:Dict[str,bool])' is true, otherwise it is false.
  """
  
  if not is_compilable:
    return
  
  state.logger.debug(f"update_result_branch is called, d4j_negative_test length: {len(state.d4j_negative_test)}")
  
  if isinstance(selected_patch,TbarPatchInfo):
    cur_node=selected_patch.tbar_case_info
  elif isinstance(selected_patch,RecoderPatchInfo):
    cur_node=selected_patch.recoder_case_info
  else:
    raise RuntimeError(f'Invalid patch type: {type(selected_patch)}, it should be TbarPatchInfo or RecoderPatchInfo')

  while not isinstance(cur_node,GlobalState):
    # Update critical branches in each nodes
    if isinstance(cur_node,FileInfo):
      cur_node=state
    else:
      cur_node=cur_node.parent
    critical_branch_list:List[int] = list(cur_node.critical_branch_up_down_manager.upDownDict.keys())

    if state.optimized_instrumentation and state.use_simulation_mode:
      for testName in state.d4j_negative_test:
        if each_result[testName]:
          # If the patch is cached and interesting, prune non-critical branches
          if testName in each_result and testName in branch_coverage and testName in state.original_branch_cov:
              branch_coverage[testName].branch_coverage = {key: value for key, value in branch_coverage[testName].branch_coverage.items() if key in critical_branch_list}
          else:
            state.logger.debug(f"testName in each_result: {testName in each_result}, "
                              f"each_result[testName]: {each_result[testName]}, "
                              f"testName in branch_coverage: {testName in branch_coverage}, "
                              f"testName in state.original_branch_cov: {testName in state.original_branch_cov}")
    
    for testName in state.d4j_negative_test:
      if testName in each_result and testName in branch_coverage and testName in state.original_branch_cov:
        # get branch difference
        branch_difference_list: list[Tuple[int,int]] = branch_coverage[testName].diff(state.original_branch_cov[testName]) # list of (branch index, branch count difference)
        state.logger.debug(f"update_result_branch updating successfully.")

        if each_result[testName]:
          # update if the patch is interesting
          for branch_tuple in branch_difference_list:
            branch_index:int=branch_tuple[0]
            branch_difference=branch_tuple[1]
            
            # update the critical branch data in current node
            cur_node.critical_branch_up_down_manager.update(state,branch_index, branch_difference)
      else:
        state.logger.debug(f"testName in each_result: {testName in each_result}, "
                          f"each_result[testName]: {each_result[testName]}, "
                          f"testName in branch_coverage: {testName in branch_coverage}, "
                          f"testName in state.original_branch_cov: {testName in state.original_branch_cov}")
