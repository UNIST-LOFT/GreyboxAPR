#!/usr/bin/python3
import sys, os, time, subprocess,fnmatch, shutil, csv,re, datetime
import json
import javalang
import javalang.tree
from typing import Tuple, List, Dict, Set
global_id_to_fl: Dict[str, 'PatchLoc'] = dict()
global_files = dict()

cache = ("", "")
cache_id = ""

global_switch_info = dict()

class PatchLoc:
    id: str
    rank: int
    file: str
    line: int
    removed_lines: int
    fl_score: float
    function: dict

    def __init__(self, id: str, rank: int, file: str, line: int, removed_lines: int, fl_score: float, function: dict):
        self.id = id
        self.rank = rank
        self.file = file
        self.line = line
        self.removed_lines = removed_lines
        self.fl_score = fl_score
        self.function = function

    def get_location(self, patch_count: int) -> str:
        file_name = self.file.split("/")[-1]
        return f"{self.get_loc_dir(patch_count)}/{file_name}"

    def get_loc_dir(self, patch_count: int) -> str:
        return f"patch/{self.rank}/{patch_count}"


def syntax_check(java: str) -> bool:
    try:
        tokens = javalang.tokenizer.tokenize(java)
        parser = javalang.parser.Parser(tokens)
        parser.parse()
    except:
        return False
    return True

def get_end_line(node: javalang.tree.Node, lineid: int) -> int:
    line = lineid
    # print(type(node))
    if node is None or isinstance(node, str) or isinstance(node, bool):
        return line
    if isinstance(node, list) or isinstance(node, set):
        for n in node:
            line = get_end_line(n, line)
        return line   
    if hasattr(node, 'position'):
        if node.position is not None:
            if node.position.line > line:
                line = node.position.line
    if hasattr(node, 'children') and node.children is not None:
        for n in node.children:
            line = get_end_line(n, line)
    return line + 1


def get_method_range(target: str, lineid: int) -> dict:
    method_range = dict()
    found_method = False
    tokens = javalang.tokenizer.tokenize(target)
    parser = javalang.parser.Parser(tokens)
    tree = parser.parse()
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        if node.position is None:
            continue
        start_line = node.position.line
        end_line = get_end_line(node, start_line)
        if (start_line <= lineid + 1) and (end_line >= lineid + 1):
            print(f"[method] [name {node.name}]  [line {start_line}, {end_line}]")
            method_range = { "function": node.name, "begin": start_line, "end": end_line }
            found_method = True
            break
    if found_method:
        return method_range
    for path, node in tree.filter(javalang.tree.ConstructorDeclaration):
        if node.position is None:
            continue
        start_line = node.position.line
        end_line = get_end_line(node, start_line)
        if (start_line <= lineid + 1) and (end_line >= lineid + 1):
            print(f"[method] [name {node.name}]  [line {start_line}, {end_line}]")
            method_range = { "function": node.name, "begin": start_line, "end": end_line }
            found_method = True
            break
    if found_method:
        return method_range
    return { "function": "0no_function_found", "begin": lineid, "end": lineid }


def add_patch(loc_id: str, patch: str, patch_count: str):
    global global_id_to_fl, global_files, global_switch_info
    meta = global_id_to_fl[loc_id]
    location = meta.get_location(patch_count)
    predit = patch
    src = meta.file
    method = f"{meta.function['function']}:{meta.function['begin']}-{meta.function['end']}"
    line = loc_id
    rules = global_switch_info["rules"]
    if src not in rules:
        rules[src] = dict()
    if method not in rules[src]:
        rules[src][method] = dict()
    if line not in rules[src][method]:
        rules[src][method][line] = list()
    patch_info = {
        "case": patch_count,
        "location": location,
        "code": predit,
    }
    rules[src][method][line].append(patch_info)
    ranking = global_switch_info["ranking"]
    ranking.append(location)


def executePatch(line_id: str, startNo: int, removedNo: int, fpath: str, predit: str, patch_count: int, total: int) -> bool:
    # first checkout buggy project
    # os.system(f'defects4j checkout -p {projectId} -v {bugId}b -w {PATCH_DIR}')
    # keep a copy of the buggy file
    global global_id_to_fl, global_files
    meta = global_id_to_fl[line_id]
    save_dir = os.path.join(D4J_DIR, meta.get_loc_dir(patch_count))
    os.makedirs(save_dir, exist_ok=True)
    patched_file = os.path.join(D4J_DIR, meta.get_location(patch_count))
    endNo = startNo + removedNo
    global cache, cache_id
    if cache_id == line_id:
        prev_file = cache[0]
        post_file = cache[1]
    else:
        prev_file = ""
        post_file = ""
        cache_id = line_id
        contents = global_files[fpath]
        for i in range(len(contents)):
            line = contents[i]
            if i + 1 < startNo:
                prev_file += line
            elif i + 1 >= endNo:
                post_file += line
        cache = (prev_file, post_file)
    # apply patch
    patched = prev_file + predit + "\n" + post_file
    if syntax_check(patched):
        add_patch(line_id, predit, patch_count)
        with open(patched_file, 'w') as f:
            f.write(patched)
        with open(os.path.join(D4J_DIR, "patches.log"), "a") as f:
            f.write(f"[patch] [lid {line_id}] [id {patch_count}] [path {patched_file}] [diff \"{predit}\"]\n")
            print((f"[patch] [lid {line_id}] [id {patch_count}] [path {patched_file}] [diff \"{predit}\"]"))
        return True
    else:
        with open(os.path.join(D4J_DIR, "patches.log"), "a") as f:
            f.write(f"[synerr] [lid {line_id}] [id {total - patch_count}] [path {patched_file}] [diff \"{predit}\"] [syntax error]\n")
            print(f"[synerr] [lid {line_id}] [id {total - patch_count}] [path {patched_file}] [diff \"{predit}\"]")
        return False


def execute(patchId,repodir,originFile,rootdir):
    compile_error_flag = True

    program_path=repodir+'/'+patchId
    print('****************'+program_path+'******************')
    #get compile result
    cmd = "cd " + program_path + ";"
    cmd += "timeout 90 defects4j compile"
    exectresult='[timeout]'
    symbolVaraible=''
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print(result)
    
    # evaluate compilable
    if 'Running ant (compile)' in str(result):
        result = str(result).split("Running ant (compile)")[1]
        result=result.split('\n')
        for i in range(0,len(result)):
            if 'error: ' in result[i]:
                firstError=result[i].split('error: ')[1]
                exectresult=firstError.split('[javac]')[0]
                if '\\' in exectresult:
                    exectresult=exectresult.split('\\')[0]
                print('=======First Error========='+firstError)
                # 'cannot  find  symbol      
                if 'symbol' in firstError and 'cannot' in firstError and 'find' in firstError:       
                    if '[javac]' in firstError:
                        lines = firstError.split('[javac]')
                        for l in lines:
                            if 'symbol:'in l and 'variable' in l:
                                symbolVaraible=l.split('variable')[1]
                                if '\\' in symbolVaraible:
                                    symbolVaraible=symbolVaraible.split('\\')[0]
                                break

                exectresult='[CE] '+exectresult+symbolVaraible
                break
            elif 'OK' in result[i]:               
                exectresult='OK'
                compile_error_flag=False

    # evaluate plausible
    if not compile_error_flag:
        #get test result
        cmd = "cd " + program_path + ";"
        cmd += "timeout 120 defects4j test"
        result=''
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        print(result)
        if 'Failing tests: 0' in str(result):
            exectresult='[Plausible]'
        elif 'Failing tests' in str(result):
            result=str(result).split('Failing tests:')[1]
            result=str(result).split('-')
            for i in range(1,len(result)):
                failingtest = result[i]
                if '::' not in failingtest and i+1<len(result):
                    failingtest = result[i+1]
                if '\\' in failingtest:
                    failingtest = failingtest.split('\\')[0]
                failingtest=failingtest.strip()

                if '::' in failingtest:
                    failingTestMethod=failingtest.split('::')[1]
                    faildiag = getFailingTestDiagnostic(failingtest,program_path)
                    exectresult = '[FE] ' + faildiag +' '+failingTestMethod
                else:
                    exectresult = '[FE] '
                break
   
    os.chdir(rootdir)

    return exectresult


def getFailingTestDiagnostic(failingtest,program_path):
    testclass = failingtest.split("::")[0]

    cmd = "cd " + program_path + ";"
    cmd += "timeout 120 defects4j monitor.test -t "+failingtest
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print('====result===='+str(result))
    if 'failed!' in str(result) :
        result = str(result).split('failed!')[1]
        if testclass in str(result):
            result = str(result).split(testclass)[1]
            if '):' in str(result):
                result = str(result).split('):')[1]
                if '\\' in str(result):
                    result = str(result).split('\\')[0]
    else:
        result =''

    return str(result)

def read_fl(file) -> Tuple[dict, dict]:
    id_to_fl = dict()
    files = dict()
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            tokens = line.strip().split("\t")
            loc_id = tokens[0]
            bid = tokens[1]
            rank = tokens[2]
            removed_lines = tokens[3]
            src = tokens[4]
            line = tokens[5]
            fl_score = tokens[6]
            print(f"[fl] [id {loc_id}]")
            if src not in files:
                with open(os.path.join(PATCH_DIR, src), 'r', encoding='latin-1', errors='ignore') as f:
                    files[src] = f.readlines()
            func = get_method_range("".join(files[src]), int(line))
            id_to_fl[loc_id] = PatchLoc(loc_id, int(rank), src, int(line), int(removed_lines), float(fl_score), func)

    return id_to_fl, files


def add_tests(bugid: str, switch_info: dict) -> None:
    proj = bugid.split("_")[0]
    bid = bugid.split("_")[1]
    build_dir = os.path.join("patch", bugid)
    os.makedirs(build_dir, exist_ok=True)
    gen_proj_cmd = f"defects4j checkout -p {proj} -v {bid}b -w {build_dir}"
    gen_fixed_proj_cmd = f"defects4j checkout -p {proj} -v {bid}f -w {build_dir}f"
    print("Generating project directory! " + gen_proj_cmd)
    os.system(gen_proj_cmd)
    os.system(gen_fixed_proj_cmd)
    compile_fixed = f"defects4j compile -w {build_dir}f"
    os.system(compile_fixed)
    fix_test_cmd = ["defects4j", "test", "-w", build_dir + "f"]
    test_proc = subprocess.Popen(fix_test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    so, se = test_proc.communicate()
    result_str = so.decode("utf-8")
    err_str = se.decode("utf-8")
    failed_tests = list()
    for line in result_str.splitlines():
        line = line.strip()
        if line.startswith("Failing tests:"):
            error_num = int(line.split(":")[1].strip())
            continue
        if line.startswith("-"):
            ft = line.replace("-", "").strip()
            failed_tests.append(ft)
    tests_all_file = os.path.join(D4J_DIR, "tests.all")
    tests_relevant_file = os.path.join(D4J_DIR, "tests.rel")
    tests_trigger_file = os.path.join(D4J_DIR, "tests.trig")
    gen_test_all_cmd = f"defects4j export -w {build_dir} -o {tests_all_file} -p tests.all"
    os.system(gen_test_all_cmd)
    gen_test_rel_cmd = f"defects4j export -w {build_dir} -o {tests_relevant_file} -p tests.relevant"
    os.system(gen_test_rel_cmd)
    gen_test_trig_cmd = f"defects4j export -w {build_dir} -o {tests_trigger_file} -p tests.trigger"
    os.system(gen_test_trig_cmd)
    # TODO: tests
    failing_test_cases = list()
    failed = dict()
    passing_test_cases = list()
    relevent_test_cases = list()
    with open(tests_trigger_file, "r") as tf:
        for line in tf.readlines():
            test = line.strip()
            failing_test_cases.append(test)
    with open(tests_all_file, "r") as tf:
        for line in tf.readlines():
            test = line.strip()
            passing_test_cases.append(test)
    with open(tests_relevant_file, "r") as tf:
        for line in tf.readlines():
            test = line.strip()
            relevent_test_cases.append(test)
    switch_info["failing_test_cases"] = failing_test_cases
    switch_info["passing_test_cases"] = passing_test_cases
    switch_info["relevant_test_cases"] = relevent_test_cases
    switch_info["failed_passing_tests"] = failed_tests


def init_switch_info(bugid: str, id_to_fl: Dict[str, PatchLoc], files: Dict[str, List[str]]) -> dict:
    switch_info = dict()
    switch_info["project_name"] = bugid
    add_tests(bugid, switch_info)
    # priority
    priority_list = list()
    for loc_id in id_to_fl:
        item = {
            "file": id_to_fl[loc_id].file,
            "line": id_to_fl[loc_id].line,
            "score": id_to_fl[loc_id].fl_score,
        }
        priority_list.append(item)
    switch_info["priority"] = priority_list
    switch_info["rules"] = dict() # Should be converted into a list
    switch_info["ranking"] = list()
    return switch_info

if __name__ == '__main__':

    BUG_ID = sys.argv[1]
    proj, bid = BUG_ID.split('_')
    patchFromPath = f'd4j/{BUG_ID}/raw_results.csv'
    patchToPath = f'd4j/{BUG_ID}/results.csv'
    PATCH_DIR = os.path.join("patch", BUG_ID)
    if not os.path.exists(PATCH_DIR):
        # os.system(f'rm -rf {PATCH_DIR}')
        os.makedirs("patch", exist_ok=True)
        os.system(f'defects4j checkout -p {proj} -v {bid}b -w {PATCH_DIR}')
    D4J_DIR = os.path.join("d4j", BUG_ID)
    os.system(f'rm -rf {D4J_DIR}/patch')
    os.system(f"rm -f {D4J_DIR}/patches.log")
    
    global_id_to_fl, global_files = read_fl(os.path.join("repair_iteration", f"{proj}{bid}", "fl.csv"))
    global_switch_info = init_switch_info(BUG_ID, global_id_to_fl, global_files)
    patch_count = 0
    with open(patchFromPath,'r') as patchFile:
        patches = patchFile.readlines()
        # len(patches)
        for i in range(len(patches)):
            try:
                patch=patches[i]
                tokens = patch.strip().split('\t')
                loc_id = tokens[0]
                predit = tokens[1]
                # Read extra from metadata in repair_iteration/{BUG_ID}/fl.csv
                meta = global_id_to_fl[loc_id]
                projectId = proj
                bugId = bid
                startNo = meta.line
                removedNo = meta.removed_lines
                path = meta.file
                preditNoSpace = predit.replace(' ','').replace('\n','').replace('\r','').replace('[Delete]','')
                exeresult = executePatch(loc_id, startNo, removedNo, path, predit, patch_count, i)
                if exeresult:
                    patch_count += 1
            except (IndexError, RuntimeError, TypeError, NameError,FileNotFoundError) as e:
                print(e)
    
    # post process
    rules = global_switch_info["rules"]
    final_rules = list()
    for src in rules:
        methods = list()
        for method in rules[src]:
            line_objects = list()
            for line in rules[src][method]:
                patches = rules[src][method][line]
                meta = global_id_to_fl[line]
                line_object = { 
                    "line": meta.line,
                    "id": meta.rank,
                    "fl_score": meta.fl_score,
                    "file": meta.file,
                    "cases": patches 
                }
                line_objects.append(line_object)
            method_object = { "function": method, "lines": line_objects }
            methods.append(method_object)
        file_object = { "file": src, "functions": methods }
        final_rules.append(file_object)
    global_switch_info["rules"] = final_rules
    with open(os.path.join(D4J_DIR, "switch-info.json"), "w") as f:
        json.dump(global_switch_info, f, indent=2)




