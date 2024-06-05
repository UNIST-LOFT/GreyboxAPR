from typing import Any
from core import *
import numpy as np
import random

def epsilon_greedy(total:int,x:int):
  """
    Compute epsilin value of Epsilon-greedy algorithm
    x: larger epsilon for larger x
  """
  return 1 / (1 + np.e ** (-1 / (total / PT.EPSILON_A) * (x - total / PT.EPSILON_B)))

def weighted_mean(a:float, b:float, weight_a:int=1, weight_b:int=1):
  """
    Compute weighted mean, for guided decision
  """
  return (a * weight_a + b * weight_b) / (weight_a + weight_b)

def get_ochiai(s_h: float, s_l: float, d_h: float, d_l: float) -> float:
  if s_h == 0.0:
    return 0.0
  return s_h / (((s_h + d_h) * (s_h + s_l)) ** 0.5)

def get_static_score(element):
  if type(element)==FileInfo or type(element)==FuncInfo:
    return max(element.fl_score_list)
  elif type(element)==LineInfo:
    return element.fl_score
  elif type(element) == RecoderCaseInfo:
    return element.parent.fl_score
  elif type(element)==TbarTypeInfo:
    return element.parent.fl_score
  elif type(element)==TbarCaseInfo:
    return element.parent.parent.fl_score
  elif type(element) == RecoderCaseInfo:
    return element.prob
  else: raise ValueError(f'Unknown element type {type(element)}')
    
def second_vertical_search_recursion(state:GlobalState, source:PatchTreeNode):
  """
  A recursive method.

  Args:
      isUp (bool): _description_
      source (PatchTreeNode): _description_
  """
  if source is None:
    _source=state
  else:
    _source=source
  if _source.critical_branch_up_down_manager.is_empty():
    return epsilon_select(state, source)

  selected_branch:int = random.choice(list(_source.critical_branch_up_down_manager.upDownDict.keys()))
  isUp:bool=_source.critical_branch_up_down_manager.get_isUp(selected_branch)

  state.logger.debug(f"during second vertical search. source: {_source}")
  if source is None:
    # Select file
    children_map = state.file_info_map
    if state.use_fl_score_in_greybox:
      children_map = filter_children_list_by_fl_score(state, source, children_map)
    state.logger.debug(f"second vertical traversing on root. file_info_map len: {len(children_map)}, isUp: {isUp}, selected_branch: {selected_branch}")
  if isinstance(source, FileInfo):
    children_map = source.func_info_map
    if state.use_fl_score_in_greybox:
      children_map = filter_children_list_by_fl_score(state, source, children_map)
    state.logger.debug(f"second vertical traversing on file level. func_info_map len: {len(children_map)}, isUp: {isUp}, selected_branch: {selected_branch}")
  elif isinstance(source, FuncInfo):
    children_map = source.line_info_map
    if state.use_fl_score_in_greybox:
      children_map = filter_children_list_by_fl_score(state, source, children_map)
    state.logger.debug(f"second vertical traversing on func level. line_info_map len: {len(children_map)}, isUp: {isUp}, selected_branch: {selected_branch}")
  elif isinstance(source, LineInfo):
    if state.tool_type == ToolType.TEMPLATE:
      children_map = source.tbar_type_info_map
      state.logger.debug(f"second vertical traversing on line level. type_info_map len: {len(children_map)}, isUp: {isUp}, selected_branch: {selected_branch}")
    elif state.tool_type == ToolType.LEARNING:
      children_map = source.recoder_case_info_map
      state.logger.debug(f"second vertical traversing on line level. recoder_case_info_map len: {len(children_map)}, isUp: {isUp}, selected_branch: {selected_branch}")
  elif isinstance(source, TbarTypeInfo): # Only for Tbar
    children_map = source.tbar_case_info_map
    state.logger.debug(f"second vertical traversing on type level. case_info_map len: {len(children_map)}, isUp: {isUp}, selected_branch: {selected_branch}")
  elif isinstance(source, TbarCaseInfo): # Only for Tbar
    state.logger.debug(f"second vertical search done. isUp: {isUp}, selected_branch: {selected_branch}")
    return source
  elif isinstance(source, RecoderCaseInfo): # Only for Recoder
    state.logger.debug(f"second vertical search done. isUp: {isUp}, selected_branch: {selected_branch}")
    return source  

  randomly_selected_values = []
  for child in children_map.values():
    randomly_selected_values.append(child.critical_branch_up_down_manager.select_value(selected_branch, isUp))

  _debug=f'Mode of 2nd vertical: {_source}: '
  for child in children_map.values():
    _debug+=f'{child.critical_branch_up_down_manager.upDownDict[selected_branch].mode(isUp)}'
  state.logger.debug(_debug)

  _debug=f'Prob of 2nd vertical: {_source}: '
  for i in randomly_selected_values:
    _debug+=f'{i},'
  state.logger.debug(_debug)
  
  max_index = randomly_selected_values.index(max(randomly_selected_values))
  new_source = list(children_map.values())[max_index]
  
  return second_vertical_search_recursion(state, new_source)
  
def filter_children_list_by_fl_score(state:GlobalState, source:PatchTreeNode, given_map):
  """
  filters the children map of PatchTreeNode to get Nodes with Highest fl score.
  source should be the upper than line level of the patch tree node.
  """
  if source is None:
    highest_fl_score = max(list(state.score_remain_line_map.keys()))
  else:
    highest_fl_score = max(list(source.remain_lines_by_score.keys()))

  state.logger.debug(f"filtering the childern list. highest_fl_score: {highest_fl_score}")
  if source is None:
    new_map=dict()
    for file in state.file_info_map:
      file_info = state.file_info_map[file]
      max_score=max(file_info.fl_score_list)
      if max_score == highest_fl_score:
        new_map[file] = file_info
  elif isinstance(source,FileInfo):
    new_map=dict()
    for func in source.func_info_map:
      func_info=source.func_info_map[func]
      max_score=max(func_info.fl_score_list)
      if max_score == highest_fl_score:
        new_map[func] = func_info
  elif isinstance(source, FuncInfo):
    new_map = dict()
    for line in source.line_info_map:
      if source.line_info_map[line].fl_score == highest_fl_score:
        new_map[line] = source.line_info_map[line]
  else:
    raise RuntimeError(f"source should be FileInfo, FuncInfo, or None; given {type(source)}")

  state.logger.debug(f"filtered map: {new_map}")
  return new_map

def epsilon_select(state:GlobalState,source:PatchTreeNode=None):
  """
  Here is the main logic of the horizontal navigation(= epsilon search)
  
  
  previous description:
    Do epsilon search if there's no basic patch.
    source: File/Function/Line/TbarType info, or None if file selection
  """
  top_fl_patches:List[Union[TbarCaseInfo,RecoderCaseInfo]]=[] # All 'not searched' top scored patches
  top_all_patches=[] # All top scored patches, include searched or not searched
  cur_score=-100. # the value -100 means that this variable is not initialized yet.
  start_time=time.time()
  # Get all top fl patches
  if source is None:
    cur_list=state.java_patch_ranking
    cur_remain_list=state.java_remain_patch_ranking
    cur_remain_list_sorted=sorted(cur_remain_list.keys(),reverse=True)
    for score in cur_remain_list_sorted:
      if len(cur_remain_list[score])>0 and cur_score==-100.:
        cur_score=score
        top_fl_patches += cur_remain_list[score]
        top_all_patches += cur_list[score]
        break
  else:
    cur_remain_list_sorted=sorted(source.remain_patches_by_score.keys(),reverse=True)
    for score in cur_remain_list_sorted:
      if len(source.remain_patches_by_score[score])>0 and cur_score==-100.:
        cur_score=score
        top_fl_patches += source.remain_patches_by_score[score]
        top_all_patches += source.patches_by_score[score]
        break

  # Get total patches and total searched patches, for epsilon greedy method
  total_patches=len(top_all_patches)
  total_searched=len(top_all_patches)-len(top_fl_patches)
  epsilon=epsilon_greedy(total_patches,total_searched)
  is_epsilon_greedy=np.random.random()<epsilon and not state.not_use_epsilon_search

  if is_epsilon_greedy:
    if source is None:
      _source=state
    else:
      _source=source

    if state.mode == Mode.greybox and not _source.critical_branch_up_down_manager.is_empty() and \
            ((source is not None and source.children_basic_patches > 0) or (source is None and state.total_basic_patch > 0)):
      state.logger.debug(f"Use second vertical search, epsilon: {epsilon}")
      return second_vertical_search_recursion(state, source)
    # Perform random search in epsilon probability
    else:
      state.logger.debug(f'is critical_branch empty: {_source.critical_branch_up_down_manager.is_empty()}, is source none: {source is None}')
    state.logger.debug(f'Use epsilon greedy method, epsilon: {epsilon}')

    # Choose random element in candidates
    index=np.random.randint(0,len(top_fl_patches))
    state.select_time+=time.time()-start_time
    return top_fl_patches[index]
  else:
    # Return top scored layer in original
    state.logger.debug(f'Use original order, epsilon: {epsilon}')
    state.select_time+=time.time()-start_time
    return top_fl_patches[0]
  
def select_patch_guide_algorithm(state: GlobalState,elements:Dict[Any,PatchTreeNode],parent:PatchTreeNode=None):
  """
  one step of vertical traversal.
  This function selects a child node of the 'parent' in the patch tree.
  - select a random value from the each child node. (the values are temporarily stored in 'p_b'in this function)
  - select the child node with the highest value.
  And return the selected child node.

  Args:
      state (GlobalState): _description_
      elements (dict): the dictionary containing the children of the 'parent'. In normal cases, parent contains it but for some reason this dictionary is required by this function :b
      parent (PatchTreeNode, optional): the node that you want to select a child from. Defaults to None.

  Returns:
      _type_: _description_
  """
  start_time=time.time()

  selected:List[PatchTreeNode]=[]
  p_b=[]
  if parent is None: # Selecting file
    total_basic_patch=state.total_basic_patch
  else:
    total_basic_patch=parent.children_basic_patches
  
  if total_basic_patch>0:
    # Follow guided search if basic patch exist
    selected.clear()
    for element_name in elements:
      info:PatchTreeNode = elements[element_name]
      selected.append(info)
      # Use vertical nav for the enabled edges
      if info.children_basic_patches>0:
        p_b.append(info.positive_pf.select_value(PT.ALPHA_INIT,PT.BETA_INIT))
      else:
        p_b.append(0.)

    _debug=f'Mode of 1st vertical: {parent}: '
    for element_name in elements:
      info:PatchTreeNode = elements[element_name]
      _debug+=f'{info.positive_pf.beta_mode(PT.ALPHA_INIT,PT.BETA_INIT)},'
    state.logger.debug(_debug)

    _debug=f'Prob of 1st vertical: {parent}: '
    for i in p_b:
      _debug+=f'{i},'
    state.logger.debug(_debug)

    max_score=0.
    max_index=-1
    scores=[]
    for i in range(len(selected)):
      scores.append(get_static_score(selected[i]))
      if p_b[i]>max_score:
        max_score=p_b[i]
        max_index=i
    scores.append(state.previous_score)
    
    if max_index>=0:
      state.logger.debug(f'Try basic patch with a: {selected[max_index].pf.pass_count}, b: {selected[max_index].pf.fail_count}')
      freq=selected[max_index].children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0.
      bp_freq=selected[max_index].consecutive_fail_count
      cur_score=get_static_score(selected[max_index])
      prev_score=state.previous_score
      score_rate=min(cur_score/prev_score,1.) if prev_score!=0. else 0.
      # Acceptance probability
      if np.random.random()< (weighted_mean(PassFail.concave_up(freq),PassFail.log_func(bp_freq))*(score_rate*PT.FL_WEIGHT if score_rate!=1.0 else 1.0)):
        state.logger.debug(f'Use guidance: {PassFail.concave_up(freq)}, {PassFail.log_func(bp_freq)}, {cur_score}/{prev_score}')

        state.select_time+=time.time()-start_time
        return selected[max_index]
      else:
        state.logger.debug(f'Do not use guidance: {PassFail.concave_up(freq)}, {PassFail.log_func(bp_freq)}, {cur_score}/{prev_score}')
        state.select_time+=time.time()-start_time
        return None
      
  else:
    # No guide in this layer, use top ranked patch
    state.logger.debug(f'No guided found in this layer, use original order!')
    return None

def select_patch_tbar_mode(state: GlobalState) -> TbarPatchInfo:
  """
  Select a patch in appropriate way and return the patch.
  The default method for selecting is select_patch_tbar_guided(state).

  Args:
      state (GlobalState): _description_

  Returns:
      TbarPatchInfo: _description_
  """
  if state.mode == Mode.orig:
    return select_patch_tbar(state)
  elif state.mode==Mode.genprog:
    return select_patch_tbar_genprog(state)
  elif state.mode == Mode.seapr:
    return select_patch_tbar_seapr(state)
  else:
    return select_patch_tbar_guided(state)

def select_patch_tbar(state: GlobalState) -> TbarPatchInfo:
  loc = state.patch_ranking.pop(0)
  caseinfo = state.switch_case_map[loc]
  caseinfo.parent.parent.parent.case_rank_list.pop(0)
  return TbarPatchInfo(caseinfo)

def select_patch_tbar_guided(state: GlobalState) -> TbarPatchInfo:
  """
  Here is the main logic of the vertical navigation.
  It traverses the patch tree from the root, selecting file, function, line, type?, and patch.
  During the traversing, It occationally switch to the horizontal navigation.

  Args:
      state (GlobalState): _description_

  Returns:
      TbarPatchInfo: _description_
  """
  p_fl = list() # fault localization
  p_frequency = list() # frequency of basic patches from total basic patches
  p_bp_frequency=list() # frequency of basic patches from total searched patches in subtree

  # Select file
  if state.total_basic_patch==0 or state.not_use_guided_search:
    selected_switch_info=epsilon_select(state)
    result = TbarPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result

  selected_file_info:FileInfo = select_patch_guide_algorithm(state,state.file_info_map,None)
  if selected_file_info is None:
    selected_switch_info=epsilon_select(state,None)
    result = TbarPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    # for logging (begin)
    for file_name in state.file_info_map:
      file_info=state.file_info_map[file_name]
      p_fl.append(max(file_info.fl_score_list))
      p_frequency.append(file_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(file_info.consecutive_fail_count)
    norm=PassFail.normalize(p_fl)
    selected_file=0
    for i,file in enumerate(state.file_info_map):
      if state.file_info_map[file]==selected_file_info:
        selected_file=i
        break
    state.logger.debug(f'Selected file: FL: {norm[selected_file]}/{p_fl[selected_file]}, Basic: {selected_file_info.pf.beta_mode(selected_file_info.pf.pass_count,selected_file_info.pf.fail_count)}, '+
                    f'Plausible: {selected_file_info.positive_pf.beta_mode(selected_file_info.positive_pf.pass_count,selected_file_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_file])}/{p_frequency[selected_file]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_file])}')
    # for logging (end)

    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent.parent.parent.parent==selected_file_info:
        state.logger.debug(f'Correct guide at file')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at file')
    
  # Select function
  selected_func_info:FuncInfo = select_patch_guide_algorithm(state,selected_file_info.func_info_map,selected_file_info)
  if selected_func_info is None:
    selected_switch_info=epsilon_select(state,selected_file_info)
    result = TbarPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    # for logging (begin)
    for func_name in selected_file_info.func_info_map:
      func_info=selected_file_info.func_info_map[func_name]
      p_fl.append(max(func_info.fl_score_list))
      p_frequency.append(func_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(func_info.consecutive_fail_count)
    norm=PassFail.normalize(p_fl)
    selected_func=0
    for i,func in enumerate(selected_file_info.func_info_map):
      if selected_file_info.func_info_map[func]==selected_func_info:
        selected_func=i
        break
    norm=PassFail.normalize(p_fl)
    state.logger.debug(f'Selected function: FL: {norm[selected_func]}/{p_fl[selected_func]}, Basic: {selected_func_info.pf.beta_mode(selected_func_info.pf.pass_count,selected_func_info.pf.fail_count)}, '+
                    f'Plausible: {selected_func_info.positive_pf.beta_mode(selected_func_info.positive_pf.pass_count,selected_func_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_func])}/{p_frequency[selected_func]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_func])}')
    # for logging (end)

    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent.parent.parent==selected_func_info:
        state.logger.debug(f'Correct guide at func')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at func')

  # Select line
  selected_line_info:LineInfo = select_patch_guide_algorithm(state,selected_func_info.line_info_map,selected_func_info)
  if selected_line_info is None:
    selected_switch_info=epsilon_select(state,selected_func_info)
    result = TbarPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    # for logging (begin)
    for line in selected_func_info.line_info_map:
      line_info=selected_func_info.line_info_map[line]
      p_fl.append(line_info.fl_score)
      p_frequency.append(line_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(line_info.consecutive_fail_count)
    norm=PassFail.normalize(p_fl)
    selected_line=0
    for i,line in enumerate(selected_func_info.line_info_map):
      if selected_func_info.line_info_map[line]==selected_line_info:
        selected_line=i
        break
    norm=PassFail.normalize(p_fl)
    state.logger.debug(f'Selected line: FL: {norm[selected_line]}/{p_fl[selected_line]}, Basic: {selected_line_info.pf.beta_mode(selected_line_info.pf.pass_count,selected_line_info.pf.fail_count)}, '+
                    f'Plausible: {selected_line_info.positive_pf.beta_mode(selected_line_info.positive_pf.pass_count,selected_line_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_line])}/{p_frequency[selected_line]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_line])}')
    # for logging (end)
  
    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent.parent==selected_line_info:
        state.logger.debug(f'Correct guide at line')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at line')

  # Select type
  selected_type_info:TbarTypeInfo = select_patch_guide_algorithm(state,selected_line_info.tbar_type_info_map,selected_line_info)
  if selected_type_info is None:
    selected_switch_info=epsilon_select(state,selected_line_info)
    result = TbarPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    # for logging (begin)
    for tbar_type in selected_line_info.tbar_type_info_map:
      type_info=selected_line_info.tbar_type_info_map[tbar_type]
      p_frequency.append(type_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(type_info.consecutive_fail_count)
    selected_type=0
    for i,tbar_type in enumerate(selected_line_info.tbar_type_info_map):
      if selected_line_info.tbar_type_info_map[tbar_type]==selected_type_info:
        selected_type=i
        break
    state.logger.debug(f'Selected type: Basic: {selected_type_info.pf.beta_mode(selected_type_info.pf.pass_count,selected_type_info.pf.fail_count)}, '+
                    f'Plausible: {selected_type_info.positive_pf.beta_mode(selected_type_info.positive_pf.pass_count,selected_type_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_type])}/{p_frequency[selected_type]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_type])}')
    # for logging (end)

    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent==selected_type_info:
        state.logger.debug(f'Correct guide at type')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at type')

  # select tbar patch
  selected_switch_info:TbarCaseInfo=epsilon_select(state,selected_type_info)
  result = TbarPatchInfo(selected_switch_info)
  state.patch_ranking.remove(selected_switch_info.location)
  return result

def select_patch_tbar_seapr(state: GlobalState) -> TbarPatchInfo:
  selected_patch: TbarCaseInfo = None
  max_score = 0.0
  has_high_qual_patch = False

  def get_first_case_info(state: GlobalState, func: FuncInfo) -> TbarCaseInfo:
    loc = func.case_rank_list[0]
    case_info: TbarCaseInfo = state.switch_case_map[loc]
    return case_info

  state.func_list.sort(key=lambda x: max(x.fl_score_list), reverse=True)
  seapr_ranks:Dict[float,List[FuncInfo]]=dict()
  for func in state.func_list:
    if func.func_rank > 30:
      continue
    cur_score = get_ochiai(func.same_seapr_pf.pass_count, func.same_seapr_pf.fail_count, func.diff_seapr_pf.pass_count, func.diff_seapr_pf.fail_count)
    if cur_score not in seapr_ranks:
      seapr_ranks[cur_score]=[]
    seapr_ranks[cur_score].append(func)
  seapr_ranks_sorted=sorted(seapr_ranks.keys(), reverse=True)

  if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
    for cor_patch in state.correct_patch_list:
      counter=0
      is_finish=False
      for score in seapr_ranks_sorted:
        for func in seapr_ranks[score]:
          if func.func_rank > 30:
            continue
          if cor_patch not in func.case_rank_list:
            counter+=len(func.case_rank_list)
          else:
            for patch in func.case_rank_list:
              if patch!=cor_patch:
                counter+=1
              else:
                is_finish=True
                state.logger.debug(f'Correct patch {cor_patch} is ranked {counter+1}')
                break
          if is_finish:
            break
        if is_finish:
          break
  else:
    patch_ranking:Dict[float,List[str]]=dict()
    for loc in state.patch_ranking:
      tbar_case_info: TbarCaseInfo = state.switch_case_map[loc]
      if tbar_case_info.parent.parent.parent.func_rank > 30:
        continue
      if loc not in tbar_case_info.parent.tbar_case_info_map:
        continue
      cur_score = get_ochiai(tbar_case_info.same_seapr_pf.pass_count, tbar_case_info.same_seapr_pf.fail_count,
        tbar_case_info.diff_seapr_pf.pass_count, tbar_case_info.diff_seapr_pf.fail_count)
      if cur_score not in patch_ranking:
        patch_ranking[cur_score]=[]
      patch_ranking[cur_score].append(loc)
    
    patch_ranking_sort=sorted(list(patch_ranking.keys()),reverse=True)
    for cor_patch in state.correct_patch_list:
      counter=0
      is_finish=False
      for score in patch_ranking_sort:
        if cor_patch not in patch_ranking[score]:
          counter+=len(patch_ranking[score])
        else:
          for patch in patch_ranking[score]:
            if patch!=cor_patch:
              counter+=1
            else:
              is_finish=True
              state.logger.debug(f'Correct patch {cor_patch} is ranked {counter+1}')
              break
          if is_finish:
            break
        if is_finish:
          break


  # Optimization for default SeAPR
  start_time = time.time()
  if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
    state.func_list.sort(key=lambda x: max(x.fl_score_list), reverse=True)
    min_patch_rank = len(state.switch_case_map) + 1
    for func in state.func_list:
      if func.func_rank > 30:
        continue
      cur_score = get_ochiai(func.same_seapr_pf.pass_count, func.same_seapr_pf.fail_count, func.diff_seapr_pf.pass_count, func.diff_seapr_pf.fail_count)
      if cur_score > max_score:
        max_score = cur_score
        selected_patch = get_first_case_info(state, func)
        min_patch_rank = selected_patch.patch_rank
      elif cur_score == max_score:
        tmp_patch = get_first_case_info(state, func)
        if min_patch_rank > tmp_patch.patch_rank:
          min_patch_rank = tmp_patch.patch_rank
          selected_patch = tmp_patch
      has_high_qual_patch = True
  else:
    for loc in state.patch_ranking:
      tbar_case_info: TbarCaseInfo = state.switch_case_map[loc]
      if tbar_case_info.parent.parent.parent.func_rank > 30:
        continue
      if loc not in tbar_case_info.parent.tbar_case_info_map:
        continue
      cur_score = get_ochiai(tbar_case_info.same_seapr_pf.pass_count, tbar_case_info.same_seapr_pf.fail_count,
        tbar_case_info.diff_seapr_pf.pass_count, tbar_case_info.diff_seapr_pf.fail_count)
      if cur_score > max_score:
        max_score = cur_score
        selected_patch = tbar_case_info
        has_high_qual_patch = True
  if not has_high_qual_patch:
    state.logger.debug('Every top-30 methods are searched, follow original order!')
    state.select_time+=time.time()-start_time
    return select_patch_tbar(state)
  selected_patch.parent.parent.parent.case_rank_list.pop(0)
  state.select_time+=time.time()-start_time
  state.logger.debug(f'SeAPR score: {max_score}')
  state.patch_ranking.remove(selected_patch.location)
  return TbarPatchInfo(selected_patch)

def select_patch_tbar_genprog(state: GlobalState) -> TbarPatchInfo:
  start_time = time.time()
  # Select file
  state.logger.debug(f'Select with simple stochastic')
  file_score_list=[]
  file_list=[]
  for file in state.file_info_map:
    file_score_list.append(max(state.file_info_map[file].fl_score_list))
    file_list.append(state.file_info_map[file])
  file_score_norm=PassFail.normalize(file_score_list)
  selected_file_index=PassFail.select_by_probability(file_score_norm)
  selected_file:FileInfo=file_list[selected_file_index]

  # Select method
  method_score_list=[]
  method_list=[]
  for method in selected_file.func_info_map.values():
    method_score_list.append(max(method.fl_score_list))
    method_list.append(method)
  method_score_norm=PassFail.normalize(method_score_list)
  selected_method_index=PassFail.select_by_probability(method_score_norm)
  selected_method:FuncInfo=method_list[selected_method_index]

  # Select Line
  line_score_list=[]
  line_list=[]
  for line in selected_method.line_info_map.values():
    line_score_list.append(line.fl_score)
    line_list.append(line)
  line_score_norm=PassFail.normalize(line_score_list)
  selected_line_index=PassFail.select_by_probability(line_score_norm)
  selected_line:LineInfo=line_list[selected_line_index]

  # Select template
  template_list=list(selected_line.tbar_type_info_map.values())
  selected_template_index=np.random.randint(0,len(template_list))
  selected_template:TbarTypeInfo=template_list[selected_template_index]

  # Select patch
  patch_list=list(selected_template.tbar_case_info_map.values())
  selected_patch_index=np.random.randint(0,len(patch_list))
  selected_patch=patch_list[selected_patch_index]

  state.select_time+=time.time()-start_time
  state.logger.debug(f'{selected_patch.location} selected')
  state.patch_ranking.remove(selected_patch.location)
  return TbarPatchInfo(selected_patch)

def select_patch_recoder_mode(state: GlobalState) -> RecoderPatchInfo:
  if state.mode == Mode.orig:
    return select_patch_recoder(state)
  elif state.mode==Mode.genprog:
    return select_patch_recoder_genprog(state)
  elif state.mode == Mode.seapr:
    return select_patch_recoder_seapr(state)
  else:
    return select_patch_recoder_guided(state)

def select_patch_recoder(state: GlobalState) -> RecoderPatchInfo:
  p = state.patch_ranking.pop(0)
  caseinfo = state.switch_case_map[p]
  if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
    caseinfo.parent.parent.case_rank_list.pop(0)
  return RecoderPatchInfo(caseinfo)

def select_patch_recoder_guided(state: GlobalState) -> RecoderPatchInfo:
  p_fl = list()  # fault localization
  p_frequency = list()  # frequency of basic patches from total basic patches
  # frequency of basic patches from total searched patches in subtree
  p_bp_frequency = list()

  if state.total_basic_patch == 0 or state.not_use_guided_search:
    selected_switch_info = epsilon_select(state)
    state.patch_ranking.remove(selected_switch_info.location)
    result = RecoderPatchInfo(selected_switch_info)
    return result
  
  selected_file_info:FileInfo = select_patch_guide_algorithm(state,state.file_info_map,None)
  if selected_file_info is None:
    selected_switch_info=epsilon_select(state,None)
    result = RecoderPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    for file_name in state.file_info_map:
      file_info=state.file_info_map[file_name]
      p_fl.append(max(file_info.fl_score_list))
      p_frequency.append(file_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(file_info.consecutive_fail_count)
    norm=PassFail.normalize(p_fl)
    selected_file=0
    for i,file in enumerate(state.file_info_map):
      if state.file_info_map[file]==selected_file_info:
        selected_file=i
        break
    state.logger.debug(f'Selected file: FL: {norm[selected_file]}/{p_fl[selected_file]}, Basic: {selected_file_info.pf.beta_mode(selected_file_info.pf.pass_count,selected_file_info.pf.fail_count)}, '+
                    f'Plausible: {selected_file_info.positive_pf.beta_mode(selected_file_info.positive_pf.pass_count,selected_file_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_file])}/{p_frequency[selected_file]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_file])}')

    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent.parent.parent==selected_file_info:
        state.logger.debug(f'Correct guide at file')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at file')

  selected_func_info:FuncInfo = select_patch_guide_algorithm(state,selected_file_info.func_info_map,selected_file_info)
  if selected_func_info is None:
    selected_switch_info=epsilon_select(state,selected_file_info)
    result = RecoderPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    for func_name in selected_file_info.func_info_map:
      func_info=selected_file_info.func_info_map[func_name]
      p_fl.append(max(func_info.fl_score_list))
      p_frequency.append(func_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(func_info.consecutive_fail_count)
    norm=PassFail.normalize(p_fl)
    selected_func=0
    for i,func in enumerate(selected_file_info.func_info_map):
      if selected_file_info.func_info_map[func]==selected_func_info:
        selected_func=i
        break
    norm=PassFail.normalize(p_fl)
    state.logger.debug(f'Selected function: FL: {norm[selected_func]}/{p_fl[selected_func]}, Basic: {selected_func_info.pf.beta_mode(selected_func_info.pf.pass_count,selected_func_info.pf.fail_count)}, '+
                    f'Plausible: {selected_func_info.positive_pf.beta_mode(selected_func_info.positive_pf.pass_count,selected_func_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_func])}/{p_frequency[selected_func]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_func])}')

    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent.parent==selected_func_info:
        state.logger.debug(f'Correct guide at func')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at func')
  
  selected_line_info:LineInfo = select_patch_guide_algorithm(state,selected_func_info.line_info_map,selected_func_info)
  if selected_line_info is None:
    selected_switch_info=epsilon_select(state,selected_func_info)
    result = RecoderPatchInfo(selected_switch_info)
    state.patch_ranking.remove(selected_switch_info.location)
    return result
  
  if state.debug_mode:
    for line in selected_func_info.line_info_map:
      line_info=selected_func_info.line_info_map[line]
      p_fl.append(line_info.fl_score)
      p_frequency.append(line_info.children_basic_patches/state.total_basic_patch if state.total_basic_patch > 0 else 0)
      p_bp_frequency.append(line_info.consecutive_fail_count)
    norm=PassFail.normalize(p_fl)
    selected_line=0
    for i,line in enumerate(selected_func_info.line_info_map):
      if selected_func_info.line_info_map[line]==selected_line_info:
        selected_line=i
        break
    norm=PassFail.normalize(p_fl)
    state.logger.debug(f'Selected line: FL: {norm[selected_line]}/{p_fl[selected_line]}, Basic: {selected_line_info.pf.beta_mode(selected_line_info.pf.pass_count,selected_line_info.pf.fail_count)}, '+
                    f'Plausible: {selected_line_info.positive_pf.beta_mode(selected_line_info.positive_pf.pass_count,selected_line_info.positive_pf.fail_count)}, '+
                    f'Unique/Freq: {PassFail.concave_up(p_frequency[selected_line])}/{p_frequency[selected_line]}, BPFreq: {PassFail.log_func(p_bp_frequency[selected_line])}')

    is_correct_guide=False
    for cor in state.correct_patch_list:
      cor_patch=state.switch_case_map[cor]
      if cor_patch.parent==selected_line_info:
        state.logger.debug(f'Correct guide at line')
        is_correct_guide=True
        break
    if not is_correct_guide:
      state.logger.debug(f'Misguide at line')

  selected_case_info: RecoderCaseInfo = epsilon_select(state, selected_line_info)
  state.patch_ranking.remove(selected_case_info.location)
  result = RecoderPatchInfo(selected_case_info)
  return result

def select_patch_recoder_seapr(state: GlobalState) -> RecoderPatchInfo:
  selected_patch: RecoderCaseInfo = None
  max_score = 0.0
  has_high_qual_patch = False

  def get_first_case_info(state: GlobalState, func: FuncInfo) -> RecoderCaseInfo:
    loc = func.case_rank_list[0]
    case_info: RecoderCaseInfo = state.switch_case_map[loc]
    return case_info
  patch_ranking: Dict[float,List[str]]=dict()
  start_time = time.time()
  if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
    state.func_list.sort(key=lambda x: max(x.fl_score_list), reverse=True)
    min_patch_rank = len(state.switch_case_map) + 1
    for func in state.func_list:
      if func.func_rank > 30:
        continue
      cur_score = get_ochiai(func.same_seapr_pf.pass_count, func.same_seapr_pf.fail_count,
                             func.diff_seapr_pf.pass_count, func.diff_seapr_pf.fail_count)
      if cur_score not in patch_ranking:
        patch_ranking[cur_score] = list()
      patch_ranking[cur_score].extend(func.case_rank_list)
      if cur_score > max_score:
        max_score = cur_score
        selected_patch = get_first_case_info(state, func)
        min_patch_rank = selected_patch.patch_rank
      elif cur_score == max_score:
        tmp_patch = get_first_case_info(state, func)
        if min_patch_rank > tmp_patch.patch_rank:
          min_patch_rank = tmp_patch.patch_rank
          selected_patch = tmp_patch
      has_high_qual_patch = True
  else:
    for loc in state.patch_ranking:
      recoder_case_info: RecoderCaseInfo = state.switch_case_map[loc]
      if recoder_case_info.location not in recoder_case_info.parent.recoder_case_info_map:
        continue
      cur_score = get_ochiai(recoder_case_info.same_seapr_pf.pass_count, recoder_case_info.same_seapr_pf.fail_count,
        recoder_case_info.diff_seapr_pf.pass_count, recoder_case_info.diff_seapr_pf.fail_count)
      if cur_score > max_score:
        max_score = cur_score
        selected_patch = recoder_case_info
        has_high_qual_patch = True

  patch_ranking_sort = sorted(list(patch_ranking.keys()), reverse=True)
  seapr_rank = 0
  is_finished = False
  print(patch_ranking_sort)
  for score in patch_ranking_sort:
    if state.correct_patch_str not in patch_ranking[score]:
      seapr_rank += len(patch_ranking[score])
    else:
      for patch in patch_ranking[score]:
        if patch != state.correct_patch_str:
          seapr_rank += 1
        else:
          state.logger.info(f"Correct patch {state.correct_patch_str} is ranked {seapr_rank}")
          is_finished = True
          break
    if is_finished:
      break
  if not has_high_qual_patch:
    state.logger.debug('Every top-30 methods are searched, follow original order!')
    state.select_time+=time.time()-start_time
    return select_patch_recoder(state)
  state.patch_ranking.remove(selected_patch.location)
  state.logger.debug(f"Selected patch: {selected_patch.location}, seapr score: {max_score}")
  if not state.use_pattern and state.seapr_layer == SeAPRMode.FUNCTION:
    selected_patch.parent.parent.case_rank_list.pop(0)
  state.select_time+=time.time()-start_time

  return RecoderPatchInfo(selected_patch)

def select_patch_recoder_genprog(state: GlobalState) -> TbarPatchInfo:
  start_time = time.time()
  # Select file
  state.logger.debug(f'Select with simple stochastic')
  file_score_list=[]
  file_list=[]
  for file in state.file_info_map:
    file_score_list.append(max(state.file_info_map[file].fl_score_list))
    file_list.append(state.file_info_map[file])
  file_score_norm=PassFail.normalize(file_score_list)
  selected_file_index=PassFail.select_by_probability(file_score_norm)
  selected_file:FileInfo=file_list[selected_file_index]

  # Select method
  method_score_list=[]
  method_list=[]
  for method in selected_file.func_info_map.values():
    method_score_list.append(max(method.fl_score_list))
    method_list.append(method)
  method_score_norm=PassFail.normalize(method_score_list)
  selected_method_index=PassFail.select_by_probability(method_score_norm)
  selected_method:FuncInfo=method_list[selected_method_index]

  # Select Line
  line_score_list=[]
  line_list=[]
  for line in selected_method.line_info_map.values():
    line_score_list.append(line.fl_score)
    line_list.append(line)
  line_score_norm=PassFail.normalize(line_score_list)
  selected_line_index=PassFail.select_by_probability(line_score_norm)
  selected_line:LineInfo=line_list[selected_line_index]

  # Select patch
  patch_list=list(selected_line.recoder_case_info_map.values())
  selected_patch_index=np.random.randint(0,len(patch_list)-1)
  selected_patch=patch_list[selected_patch_index]

  state.select_time+=time.time()-start_time
  state.logger.debug(f'{selected_patch.location} selected')
  state.patch_ranking.remove(selected_patch.location)
  return RecoderPatchInfo(selected_patch)
