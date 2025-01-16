#!/usr/bin/env python3
import os
from statistics import mean
import subprocess
import sys
import json
import getopt
import logging
import shutil

from core import *

from simapr_loop import TBarLoop, RecoderLoop

def parse_args(argv: list) -> GlobalState:
  """
  This function parses the list of command-line arguments, 
  and the parsing result is stored in the 'state' variable, which is a GlobalState object.
  
  At the latter part of the function, it creates the directory if the required directory doesn't exists.
  Additionally, it remove and re-create the 'tmp' direcrory.

  Args:
      argv (list): A list that is the same as sys.args

  Raises:
      ValueError: 

  Returns:
      GlobalState: returns a instance of GlobalState, which is used as a singloton object.
  """
  longopts = ["help", "outdir=", "workdir=", "timeout=", "time-limit=", "cycle-limit=",
              "mode=", 'skip-valid', 'params=', "no-exp-alpha",'tool-type=',
              "no-pass-test", "use-full-validation",'seed=','--correct-patch',
              "use-pattern", "use-simulation-mode=",'debug',
              'seapr-mode=','top-fl=','ignore-compile-error',
              'finish-correct-patch','not-count-compile-fail','not-use-guide','not-use-epsilon',
              'finish-top-method','instr-cp=','branch-output=', 'use-fl-score-in-greybox',
              'weight-critical-branch', 'optimized-instrumentation', 'only-get-test-time-data-mode',
              'test-time-data-location=', 'field-output=', 'use-field', 'use-branch']
  opts, args = getopt.getopt(argv[1:], "ho:w:t:m:c:T:E:k:", longopts)
  state = GlobalState()
  state.critical_branch_up_down_manager = CriticalBranchesUpDownManager(is_this_critical_branches = True)
  state.critical_field_up_down_manager = CriticalFieldsUpDownManager(is_this_critical_fields = True)
  state.original_args = argv
  state.args = args  # After --
  for o, a in opts:
    if o in ['-h', '--help']:
      print("Usage: python3 simapr.py [options] <file>")
      exit(1)
    elif o in ['-o', '--outdir']:
      state.out_dir = a
    elif o in ['-t', '--timeout']:
      state.timeout = int(a)
    elif o in ['-w', '--workdir']:
      state.work_dir = a
    elif o in ['-c', '--correct-patch']:
      state.correct_patch_str = a
      state.correct_patch_list=a.split(',')
    elif o in ['-m', '--mode']:
      state.mode = Mode[a.lower()]
    elif o in ['-T', '--time-limit']:
      state.time_limit = int(a)
    elif o in ['-E', '--cycle-limit']:
      state.cycle_limit = int(a)
    elif o in ['--no-pass-test']:
      state.use_pass_test = False
    elif o in ['--no-exp-alpha']:
      state.use_exp_alpha=False
    elif o in ['--skip-valid']:
      state.skip_valid=True
    elif o in ['--debug']:
      state.debug_mode=True
    elif o in ['--use-pattern']:
      state.use_pattern = True
    elif o in ['--top-fl']:
      state.top_fl=int(a)
    elif o in ['--seapr-mode']:
      if a.lower()=='file':
        state.seapr_layer = SeAPRMode.FILE
      elif a.lower()=='function':
        state.seapr_layer = SeAPRMode.FUNCTION
      elif a.lower()=='line':
        state.seapr_layer = SeAPRMode.LINE
      elif a.lower()=='type':
        state.seapr_layer = SeAPRMode.TYPE
      else:
        print(f'Invalid seapr mode: {a}',file=sys.stderr)
        exit(1)
    elif o in ['--use-simulation-mode']:
      if not os.path.exists(a):
        os.makedirs(os.path.dirname(a), exist_ok=True)
      state.use_simulation_mode = True
      state.prev_data = a
    elif o in ['--use-full-validation']:
      state.use_partial_validation = False
    elif o in ['--params']:
      parsed = a.split(",")
      for param in parsed[0].split(","):
        key, value = param.split('=')
        if key.upper()=='ALPHA_INCREASE':
          PT.ALPHA_INCREASE=int(value)
        elif key.upper()=='BETA_INCREASE':
          PT.BETA_INCREASE=int(value)
        elif key.upper()=='ALPHA_INIT':
          PT.ALPHA_INIT=int(value)
        elif key.upper()=='BETA_INIT':
          PT.BETA_INIT=int(value)
        elif key.upper()=='EPSILON_THRESHOLD':
          PT.EPSILON_THRESHOLD=float(value)
        elif key.upper()=='EPSILON_A':
          PT.EPSILON_A=int(value)
        elif key.upper()=='EPSILON_B':
          PT.EPSILON_B=int(value)
        elif key.upper()=='FL_WEIGHT':
          PT.FL_WEIGHT=float(value)
        else:
          state.logger.warning(f'Invalid parameter: {key}, just ignore it!')
    elif o in ['-k','--tool-type']:
      if a.lower()=='template':
        state.tool_type = ToolType.TEMPLATE
      elif a.lower()=='learning':
        state.tool_type = ToolType.LEARNING
      else:
        raise ValueError(f'Invalid tool type: {a}')
    elif o in ['--seed']:
      np.random.seed(int(a))
    elif o in ['--ignore-compile-error']:
      state.ignore_compile_error = False
    elif o in ['--finish-correct-patch']:
      state.finish_at_correct_patch=True
    elif o in ['--not-use-guide']:
      state.not_use_guided_search=True
    elif o in ['--not-use-epsilon']:
      state.not_use_epsilon_search=True
    elif o in ['--not-count-compile-fail']:
      state.count_compile_fail = False

    # Greybox stuffs
    elif o in ['--instr-cp']:
      state.instrumenter_classpath=a
    elif o in ['--branch-output']:
      state.branch_output=a
    elif o in ['--use-branch']:
      state.use_branch = True
    elif o in ['--use-fl-score-in-greybox']:
      state.use_fl_score_in_greybox=True
    elif o in ['weight-critical-branch']:
      state.weight_critical_branch=True
    elif o in ['--optimized-instrumentation']:
      state.optimized_instrumentation = True

    # only-get-test-time-data-mode. you can use this mode when you want to get running time data of some patches.
    elif o in ['--only-get-test-time-data-mode']:
      state.only_get_test_time_data_mode = True 
    elif o in ['--test-time-data-location']:
      state.test_time_data_location = a
      
    # Greybox field stuffs
    elif o in ['--field-output']:
      state.field_output = a
    elif o in ['--use-field']:
      state.use_field = True

  # make output directory if not exists
  if not os.path.exists(state.out_dir):
    os.makedirs(state.out_dir)
    
  # make branch output directory if not exists. if the branch output directory is not given in arguments, it makes default branch output directory.
  if state.use_simulation_mode:
    if state.branch_output=='':
      if not os.path.exists(os.path.join(state.out_dir,'branch')):
        os.makedirs(os.path.join(state.out_dir,'branch'))
    elif not os.path.exists(state.branch_output):
      os.makedirs(state.branch_output)
      
  # make field output directory if not exists. if the field output directory is not given in arguments, it makes default field output directory.
  if state.use_simulation_mode:
    if state.field_output=='':
      if not os.path.exists(os.path.join(state.out_dir,'field')):
        os.makedirs(os.path.join(state.out_dir,'field'))
    elif not os.path.exists(state.field_output):
      os.makedirs(state.field_output)
  
  # make tmp directory. if the tmp directory already exsists, remove and make it again.
  state.tmp_dir = os.path.join(state.out_dir, 'tmp')
  if os.path.exists(state.tmp_dir):
    shutil.rmtree(state.tmp_dir)
  os.makedirs(state.tmp_dir)

  if state.branch_output!='':
    if not os.path.exists(state.branch_output):
      os.makedirs(state.branch_output)
  elif state.instrumenter_classpath!='':
    state.branch_output=os.path.join(state.out_dir,'branch')
    
  if state.field_output!='':
    if not os.path.exists(state.field_output):
      os.makedirs(state.field_output)
  elif state.instrumenter_classpath!='':
    state.field_output=os.path.join(state.out_dir,'field')

  return state

def set_logger(state: GlobalState) -> logging.Logger:
  """
  initialize and return the logger.

  Args:
      state (GlobalState): _description_

  Returns:
      logging.Logger: _description_
  """
  logger = logging.getLogger('simapr')
  fh = logging.FileHandler(os.path.join(state.out_dir, 'simapr-search.log'))
  if state.debug_mode:
    logger.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
  fh.setFormatter(formatter)
  ch.setFormatter(formatter)
  logger.addHandler(fh)
  logger.addHandler(ch)
  logger.info('Logger is set')
  logger.debug(f"SimAPR: {' '.join(state.original_args)}")
  logger.debug(f"Version: {state.simapr_version}")
  return logger

def read_info_recoder(state: GlobalState) -> None:
  with open(os.path.join(state.work_dir, 'switch-info.json'), 'r') as f:
    info = json.load(f)
    state.d4j_negative_test = info['failing_test_cases']
    state.d4j_positive_test = info['passing_test_cases']
    state.d4j_failed_passing_tests = set(info['failed_passing_tests'])
    file_map = state.file_info_map
    
    for file in info['rules']:
      if len(file['functions']) == 0:
        continue
      file_info = FileInfo(file['file'])
      file_name = file['file']
      file_map[file['file']] = file_info

      for func in file['functions']:
        if len(func['lines'])==0:
          continue
        func_info = FuncInfo(file_info, func['function'])
        file_info.func_info_map[func['function']] = func_info
        state.func_list.append(func_info)

        for line in func['lines']:
          line_info = None
          if len(line['cases']) == 0:
            continue
          line_info=LineInfo(func_info, int(line['line']))
          func_info.line_info_map[line_info.uuid] = line_info
          fl_score = line["fl_score"]
          line_info.fl_score = fl_score

          for cs in line["cases"]:
            case_id = cs["case"]
            location = cs["location"]
            if 'prob' in cs:
              prob = cs["prob"]
            else:
              prob = 0.5

            recoder_case_info = RecoderCaseInfo(line_info, location, case_id)
            line_info.recoder_case_info_map[location] = recoder_case_info
            state.switch_case_map[location] = recoder_case_info
            state.patch_location_map[location] = recoder_case_info
            recoder_case_info.prob = prob
            line_info.score_list.append(prob)
            func_info.score_list.append(prob)
            file_info.score_list.append(prob)
            line_info.total_case_info += 1
            func_info.total_case_info += 1
            file_info.total_case_info += 1
            if line_info.fl_score not in func_info.total_patches_by_score:
              func_info.total_patches_by_score[line_info.fl_score] = 0
              func_info.searched_patches_by_score[line_info.fl_score] = 0
            func_info.total_patches_by_score[line_info.fl_score] += 1

          if len(line_info.recoder_case_info_map) == 0:
            del func_info.line_info_map[line_info.uuid]
            del line_info
          else:
            state.line_list.append(line_info)
            func_info.fl_score_list.append(fl_score)
            file_info.fl_score_list.append(fl_score)

            if fl_score not in state.score_remain_line_map:
              state.score_remain_line_map[fl_score]=[]
            state.score_remain_line_map[fl_score].append(line_info)
            if fl_score not in file_info.remain_lines_by_score:
              file_info.remain_lines_by_score[fl_score]=[]
            file_info.remain_lines_by_score[fl_score].append(line_info)
            if fl_score not in func_info.remain_lines_by_score:
              func_info.remain_lines_by_score[fl_score]=[]
            func_info.remain_lines_by_score[fl_score].append(line_info)
        
        if len(func_info.line_info_map) == 0:
          del file_info.func_info_map[func['function']]
          state.func_list.remove(func_info)
          del func_info
      if len(file_info.func_info_map) == 0:
        del state.file_info_map[file_name]
        del file_info

  state.d4j_buggy_project = info["project_name"]
  if state.d4j_buggy_project.startswith('Mockito'):
    state.skip_valid=False # We have to validate Mocktio because we use maven project instead of defects4j

  state.patch_ranking = info["ranking"]
  func_rank_checker: Set[FuncInfo] = set()
  rank_num = 0
  func_rank = 0
  for rank in state.patch_ranking:
    case_info: RecoderCaseInfo = state.switch_case_map[rank]
    line_info = case_info.parent
    func_info = line_info.parent
    file_info = func_info.parent
    func_info.case_rank_list.append(rank)
    case_info.patch_rank = rank_num
    rank_num += 1
    if func_info not in func_rank_checker:
      func_rank_checker.add(func_info)
      func_info.func_rank = func_rank
      func_rank += 1
    fl_score = line_info.fl_score
    if fl_score not in state.java_patch_ranking:
      state.java_patch_ranking[fl_score] = []
      state.java_remain_patch_ranking[fl_score] = []
    state.java_patch_ranking[fl_score].append(case_info)
    state.java_remain_patch_ranking[fl_score].append(case_info)
    if fl_score not in file_info.patches_by_score:
      file_info.patches_by_score[fl_score] = []
      file_info.remain_patches_by_score[fl_score] = []
    file_info.patches_by_score[fl_score].append(case_info)
    file_info.remain_patches_by_score[fl_score].append(case_info)
    if fl_score not in func_info.patches_by_score:
      func_info.patches_by_score[fl_score] = []
      func_info.remain_patches_by_score[fl_score] = []
    func_info.patches_by_score[fl_score].append(case_info)
    func_info.remain_patches_by_score[fl_score].append(case_info)
    if fl_score not in line_info.patches_by_score:
      line_info.patches_by_score[fl_score] = []
      line_info.remain_patches_by_score[fl_score] = []
    line_info.patches_by_score[fl_score].append(case_info)
    line_info.remain_patches_by_score[fl_score].append(case_info)
  
  patch_ranking_list=[]
  for fl_score in state.java_patch_ranking:
    if len(state.java_patch_ranking[fl_score])>0:
      patch_ranking_list.append(len(state.java_patch_ranking[fl_score]))
  state.max_epsilon_group_size=mean(patch_ranking_list)*2
  state.logger.debug(f'Set maximum epsilon group size to {state.max_epsilon_group_size}')

  #Add original to switch_case_map
  temp_file: FileInfo = FileInfo('original')
  temp_func = FuncInfo(temp_file, "original_fn")
  temp_file.func_info_map["original_fn:0-0"] = temp_func
  temp_line: LineInfo = LineInfo(temp_func, 0)
  temp_recoder_case = RecoderCaseInfo(temp_line, "original", 0)
  state.switch_case_map["original"] = temp_recoder_case
  state.patch_location_map["original"] = temp_recoder_case
  if state.use_simulation_mode:
    if os.path.exists(state.prev_data):
      with open(state.prev_data, "r") as f:
        prev_info = json.load(f)
        for key in prev_info:
          data=prev_info[key]
          state.simulation_data[key] = data
            
def read_info_tbar(state: GlobalState) -> None:
  """
  read the file and build the patch tree for vertical navigation.
  The function returns nothing. However, the result is stored in the 'state'.

  Args:
      state (GlobalState): _description_

  Raises:
      ValueError: _description_
  """
  with open(os.path.join(state.work_dir, 'switch-info.json'), 'r') as f:
    info = json.load(f)
    # Read test informations (which tests to run, which of them are failing test or passing test)
    state.d4j_negative_test = info["failing_test_cases"]
    if len(state.d4j_negative_test)==0:
      raise ValueError("No failing test case found, abort!")
    state.d4j_positive_test = info["passing_test_cases"]
    state.d4j_failed_passing_tests = set(info["failed_passing_tests"])

    rank_list=[]
    ranking = info['ranking']
    for rank in ranking:
      loc = ""
      if isinstance(rank, str):
        loc = rank  
      else:
        loc = rank['location']
      rank_list.append(loc)

    # Read rules to build patch tree structure
    file_map = state.file_info_map
    for file in info['rules']:
      if len(file['functions']) == 0:
        continue
      file_info = FileInfo(file['file_name'])
      if "class_name" in file:
        file_info.class_name = file["class_name"]
      file_map[file['file_name']] = file_info

      for func in file['functions']:
        if len(func['lines']) == 0:
          continue
        func_info = FuncInfo(file_info, func['function'])
        file_info.func_info_map[func['function']] = func_info
        state.func_list.append(func_info)

        for line in func['lines']:
          if len(line['cases']) == 0:
            continue
          line_info=LineInfo(func_info, int(line['line']))
          func_info.line_info_map[line_info.uuid] = line_info

          # Update fl score
          line_info.fl_score = float(line['fl_score'])
          func_info.fl_score_list.append(line_info.fl_score)
          file_info.fl_score_list.append(line_info.fl_score)

          # Update data structures related on the fl score
          if line_info.fl_score not in state.score_remain_line_map:
            state.score_remain_line_map[line_info.fl_score]=[]
          state.score_remain_line_map[line_info.fl_score].append(line_info)
          if line_info.fl_score not in file_info.remain_lines_by_score:
            file_info.remain_lines_by_score[line_info.fl_score]=[]
          file_info.remain_lines_by_score[line_info.fl_score].append(line_info)
          if line_info.fl_score not in func_info.remain_lines_by_score:
            func_info.remain_lines_by_score[line_info.fl_score]=[]
          func_info.remain_lines_by_score[line_info.fl_score].append(line_info)

          # Add patches
          for case in line['cases']:
            if case['mutation'] not in line_info.tbar_type_info_map:
              line_info.tbar_type_info_map[case['mutation']] = TbarTypeInfo(line_info, case['mutation'])
            type_info=line_info.tbar_type_info_map[case['mutation']]

            tbar_case_info = TbarCaseInfo(type_info, case['location'])
            type_info.tbar_case_info_map[case['location']] = tbar_case_info

            # Update data structures related on the patch
            fl_score=tbar_case_info.parent.parent.fl_score
            if fl_score not in state.java_patch_ranking:
              state.java_patch_ranking[fl_score] = []
              state.java_remain_patch_ranking[fl_score] = []
            state.java_patch_ranking[fl_score].append(tbar_case_info)
            state.java_remain_patch_ranking[fl_score].append(tbar_case_info)
            
            if fl_score not in tbar_case_info.parent.patches_by_score:
              tbar_case_info.parent.patches_by_score[fl_score] = []
              tbar_case_info.parent.remain_patches_by_score[fl_score]=[]
            tbar_case_info.parent.patches_by_score[fl_score].append(tbar_case_info)
            tbar_case_info.parent.remain_patches_by_score[fl_score].append(tbar_case_info)

            if fl_score not in tbar_case_info.parent.parent.patches_by_score:
              tbar_case_info.parent.parent.patches_by_score[fl_score] = []
              tbar_case_info.parent.parent.remain_patches_by_score[fl_score]=[]
            tbar_case_info.parent.parent.patches_by_score[fl_score].append(tbar_case_info)
            tbar_case_info.parent.parent.remain_patches_by_score[fl_score].append(tbar_case_info)

            if fl_score not in tbar_case_info.parent.parent.parent.patches_by_score:
              tbar_case_info.parent.parent.parent.patches_by_score[fl_score] = []
              tbar_case_info.parent.parent.parent.remain_patches_by_score[fl_score]=[]
            tbar_case_info.parent.parent.parent.patches_by_score[fl_score].append(tbar_case_info)
            tbar_case_info.parent.parent.parent.remain_patches_by_score[fl_score].append(tbar_case_info)

            if fl_score not in tbar_case_info.parent.parent.parent.parent.patches_by_score:
              tbar_case_info.parent.parent.parent.parent.patches_by_score[fl_score] = []
              tbar_case_info.parent.parent.parent.parent.remain_patches_by_score[fl_score]=[]
            tbar_case_info.parent.parent.parent.parent.patches_by_score[fl_score].append(tbar_case_info)
            tbar_case_info.parent.parent.parent.parent.remain_patches_by_score[fl_score].append(tbar_case_info)

            state.switch_case_map[tbar_case_info.location] = tbar_case_info
            state.patch_location_map[tbar_case_info.location] = tbar_case_info
            tbar_case_info.total_case_info+=1
            type_info.total_case_info += 1
            line_info.total_case_info += 1
            func_info.total_case_info += 1
            file_info.total_case_info += 1
            if line_info.fl_score not in func_info.total_patches_by_score:
              func_info.total_patches_by_score[line_info.fl_score]=0
              func_info.searched_patches_by_score[line_info.fl_score]=0
            func_info.total_patches_by_score[line_info.fl_score]+=1

  state.d4j_buggy_project = info["project_name"]
  if state.d4j_buggy_project.startswith('Mockito'):
    state.skip_valid=False # We have to validate Mocktio because we use maven project instead of defects4j
    
  # Read ranking
  rank_num = 0
  ranking = info['ranking']
  func_rank = 0
  for rank in ranking:
    rank_num += 1
    loc = ""
    if isinstance(rank, str):
      loc = rank  
    else:
      loc = rank['location']

    state.patch_ranking.append(loc)
    case_info: TbarCaseInfo = state.switch_case_map[loc]
    case_info.parent.parent.parent.case_rank_list.append(loc)
    fl_score=case_info.parent.parent.fl_score

    case_info.patch_rank = rank_num
    func_info = case_info.parent.parent.parent
    if func_info.func_rank == -1:
      func_info.func_rank = func_rank
      func_rank += 1

  patch_ranking_list=[]
  for fl_score in state.java_patch_ranking:
    if len(state.java_patch_ranking[fl_score])>0:
      patch_ranking_list.append(len(state.java_patch_ranking[fl_score]))
  state.max_epsilon_group_size=mean(patch_ranking_list)*2
  state.logger.debug(f'Set maximum epsilon group size to {state.max_epsilon_group_size}')

  #Add original to switch_case_map
  temp_file: FileInfo = FileInfo('original')
  temp_func = FuncInfo(temp_file, "original_fn")
  temp_file.func_info_map["original_fn:0-0"] = temp_func
  temp_line: LineInfo = LineInfo(temp_func, 0)
  temp_tbar_type = TbarTypeInfo(temp_line, "original_mut")
  temp_tbar_case = TbarCaseInfo(temp_tbar_type, "original")
  state.switch_case_map["original"] = temp_tbar_case
  state.patch_location_map["original"] = temp_tbar_case
  if state.use_simulation_mode:
    if os.path.exists(state.prev_data):
      with open(state.prev_data, "r") as f:
        prev_info = json.load(f)
        for key in prev_info:
          data=prev_info[key]
          state.simulation_data[key] = data

  # read no-instrumentation-time-data
  # if (state.mode == Mode.greybox and state.optimized_instrumentation and state.use_simulation_mode) or (state.mode == Mode.casino and state.no_instrumentation_time_data != ""):
  #   file_path = os.path.join(state.no_instrumentation_time_data_output, "no_instrumentation_time_data.json")
  #   if not (os.path.exists(file_path)):
  #     with open(file_path, 'w') as f:
  #       f.write('')
  #   with open(file_path, 'r') as f:
  #     info = json.load(f)
  #     state.no_instrumentation_time_data = info
      
def copy_previous_results(state: GlobalState) -> None:
  """
  saves the existing result with a prefix.
  This is not to overwrite the data to the existing experiment result.
  
  and removes the previous 'simapr-finished.txt'

  Args:
      state (GlobalState): 
  """
  result_log = os.path.join(state.out_dir, "simapr-search.log")
  result_json = os.path.join(state.out_dir, "simapr-result.json")
  prefix = 0
  if os.path.exists(result_log):
    while os.path.exists(os.path.join(state.out_dir, f"bak{prefix}-simapr-search.log")):
      prefix += 1
    shutil.copy(result_log, os.path.join(state.out_dir, f"bak{prefix}-simapr-search.log"))
    os.remove(result_log)
  
  if os.path.exists(result_json):
    while os.path.exists(os.path.join(state.out_dir, f"bak{prefix}-simapr-result.json")):
      prefix += 1
    shutil.copy(result_json, os.path.join(state.out_dir, f"bak{prefix}-simapr-result.json"))
    os.remove(result_json)

  if os.path.exists(os.path.join(state.out_dir, "simapr-finished.txt")):
    os.remove(os.path.join(state.out_dir, "simapr-finished.txt"))

def main(argv: list):
  """
  This function is divided into three main parts.
  - parse the command line arguments
  - read info ~~~
  - run the loop ~~~

  Args:
      argv (list): list of arguments, which will be handled by the function "arse_args(argv: list) -> GlobalState"

  Raises:
      e: _description_
  """
  sys.setrecursionlimit(2002) # Reset recursion limit, for preventing RecursionError
  state = parse_args(argv) # returns the GlobalState instance, and it is used as a singleton. i.e. It is instantiated only once throughout the entire execution.
  if not state.only_get_test_time_data_mode:
    copy_previous_results(state)
  state.logger = set_logger(state)
  if state.tool_type==ToolType.TEMPLATE:
    read_info_tbar(state)
    state.logger.info(f'Total methods: {state.total_methods}')
    state.logger.info('Template mode: Initialized!')
    simapr = TBarLoop(state)
  elif state.tool_type==ToolType.LEARNING:
    read_info_recoder(state)
    state.logger.info('Learning mode: Initialized!')
    simapr = RecoderLoop(state)
  state.logger.info('SimAPR is started')
  try:
    simapr.run()
    with open(os.path.join(state.out_dir, "simapr-finished.txt"), "w") as f:
      f.write(' '.join(state.original_args))
      f.write("\n")
      f.write(state.simapr_version + "\n")
      f.write("SimAPR is finished\n")
      f.write(f'Running time: {state.select_time+state.test_time}\n')
      f.write(f'Select time: {state.select_time}\n')
      f.write(f'Test time: {state.test_time}\n')
  except KeyboardInterrupt:
    state.logger.warning('SimAPR is interrupted by user')
  except Exception as e:
    if 'process PID not found' in str(e):
      state.logger.warning('SimAPR is interrupted by user')
    else:
      state.logger.error(f'SimAPR throws exception: {e}',exc_info=True)
      simapr.save_result()
      raise e
  state.logger.info('SimAPR is finished')
  # state.select_time/=1000000
  state.logger.info(f'Running time: {state.select_time+state.test_time}')
  state.logger.info(f'Select time: {state.select_time}')
  state.logger.info(f'Test time: {state.test_time}')
  if not state.only_get_test_time_data_mode:
    simapr.save_result()

if __name__ == "__main__":
  main(sys.argv)
