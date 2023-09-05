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
          True in test_result.values(), pass_test_result, selected_patch[0].out_dist, False not in test_result.values(), compilable=compilable)
  
  if result.result:
    state.total_passed_patch+=1
  if result.pass_result:
    state.total_plausible_patch+=1
  state.total_searched_patch+=1
  obj = result.to_json_object(state.total_searched_patch,state.total_passed_patch,state.total_plausible_patch)
  state.simapr_result.append(obj)
  state.used_patch.append(result)

  if state.use_simulation_mode and state.tool_type!=ToolType.PRAPR:
    # Cache test result if option used
    for patch in selected_patch:
      # For Java, case_info is tbar_case_info
      if state.tool_type==ToolType.TEMPLATE:
        case_info = patch.tbar_case_info
      else:
        case_info = patch.recoder_case_info
      append_java_cache_result(state,case_info,test_result,pass_test_result,compilable,fail_time,pass_time)
  
  if (tm - state.last_save_time) > save_interval:
    save_result(state)

def update_result_tbar(state: GlobalState, selected_patch: TbarPatchInfo, result: bool) -> None:
  selected_patch.update_result(result, PT.ALPHA_INCREASE, PT.BETA_INCREASE,state.use_exp_alpha)
  if result:
    state.total_basic_patch += 1
    selected_patch.tbar_type_info.children_basic_patches+=1
    selected_patch.line_info.children_basic_patches+=1
    selected_patch.func_info.children_basic_patches+=1
    selected_patch.file_info.children_basic_patches+=1
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
    selected_patch.line_info.children_basic_patches += 1
    selected_patch.func_info.children_basic_patches += 1
    selected_patch.file_info.children_basic_patches += 1
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
    
def update_result_branch(state:GlobalState,selected_patch:Union[TbarPatchInfo,RecoderPatchInfo],coverage:Dict[str,branch_coverage.BranchCoverage],
                         is_compilable:bool,each_result:Dict[str,bool],pass_result:bool):
  critical_branches_list = []
  #count_no_pass=0 #counter for number of test passed
  interestingBranches = []
  unchangedBranches = []
  interestingPatch=False        
  for test in each_result.keys():
    interestingPath=False
    if is_compilable and test in coverage:
      cur_cov=coverage[test]
      if test in state.original_branch_cov and cur_cov is not None:
        #get cov_diff
        cov_diff=cur_cov.diff(state.original_branch_cov[test])
        
        #extract interesting branches
        interestingBranches = [item[0] for item in cov_diff]
        
        #extract branches that do not have any changes in terms of count or appearance
        coverage_set = set(cur_cov.branch_coverage.keys())
        unchangedBranches = coverage_set.difference(set(x[0] for x in cov_diff))
          
        if each_result[test]:  # if interesting Path
          state.logger.info(f'Day la interesting cov bao gom c_i: {interestingBranches}')
          interestingPath=True
          interestingPatch=True
          # count_no_pass+=1
          
          #deal with branches that has some sort of changes in interesting Path                
          for branch in interestingBranches:
            #for bar chart drawing
            if branch not in critical_branches_list:
              critical_branches_list.append(branch)
            #for bar charts drawing  
              
            if branch not in state.branch_map_ochiai:
              newBranch = BranchInfo(branch, 0,0,0,0)
              state.branch_map_ochiai[branch] = newBranch

            state.branch_map_ochiai[branch].update_ci(state.branch_map_ochiai[branch].c_i+1)
            if branch in cur_cov.branch_coverage:
              state.patch_to_branches_map[selected_patch.tbar_case_info.location].append(state.branch_map_ochiai[branch])
                      
          #deal with branches that has no changes in interesting Path      
          for branch in unchangedBranches:
            if branch not in state.branch_map_ochiai:
              newBranch = BranchInfo(branch, 0,0,0,0)
              state.branch_map_ochiai[branch] = newBranch
            state.branch_map_ochiai[branch].update_ci(state.branch_map_ochiai[branch].c_i+1)

            if branch in cur_cov.branch_coverage:
              state.patch_to_branches_map[selected_patch.tbar_case_info.location].append(state.branch_map_ochiai[branch])   
                          
          #increment the times that other branches do not appear in an interesting patch                
          for branchId, branch in state.branch_map_ochiai.items():
            if branchId not in interestingBranches and branchId not in unchangedBranches:
              state.branch_map_ochiai[branchId].update_ni(state.branch_map_ochiai[branchId].n_i+1)
          
          for cov in cov_diff:
            state.hq_patch_diff_coverage_set.add(cov)

        if not interestingPath: 
          for branch in interestingBranches:
            if branch not in state.branch_map_ochiai:
              newBranch = BranchInfo(branch, 0,0,0,0)
              state.branch_map_ochiai[branch] = newBranch

            state.branch_map_ochiai[branch].update_cu(state.branch_map_ochiai[branch].c_u+1)
            if branch in cur_cov.branch_coverage:
              state.patch_to_branches_map[selected_patch.tbar_case_info.location].append(state.branch_map_ochiai[branch])
              
          for branch in unchangedBranches:
            if branch not in state.branch_map_ochiai:
              newBranch = BranchInfo(branch, 0,0,0,0)
              state.branch_map_ochiai[branch] = newBranch

            state.branch_map_ochiai[branch].update_cu(state.branch_map_ochiai[branch].c_u+1)
            if branch in cur_cov.branch_coverage:
              state.patch_to_branches_map[selected_patch.tbar_case_info.location].append(state.branch_map_ochiai[branch])
              
        if is_compilable or state.ignore_compile_error:
            cov_diff=cur_cov.diff(state.original_branch_cov[test])
            update_result_branch_coverage_tbar(state, selected_patch, cov_diff)
            
  #After finish checking 1 patch
  for branch in critical_branches_list:
    if interestingPatch and not pass_result:
      state.branch_map_ochiai[branch].interesting_pass_count+=1 
    if pass_result:
      state.branch_map_ochiai[branch].plausible_pass_count = state.branch_map_ochiai[branch].plausible_pass_count + 1
            
  #Over for loop for failed tests     
  for patch_name in state.visited_tbar_patch:
    ochiai_score = patch_ochiai_calculator(state, patch_name)
    state.patch_to_ochiai_map[patch_name] = ochiai_score 

  if is_compilable:
    selected_patch.file_info.patches_template_type.append(selected_patch.tbar_case_info.location)
    selected_patch.func_info.patches_template_type.append(selected_patch.tbar_case_info.location)
    selected_patch.line_info.patches_template_type.append(selected_patch.tbar_case_info.location)
    selected_patch.tbar_type_info.patches_template_type.append(selected_patch.tbar_case_info.location)
    selected_patch.tbar_case_info.patches_template_type.append(selected_patch.tbar_case_info.location)
  