import subprocess
import os
import shutil
import json
from typing import List, Tuple
import xml.etree.ElementTree as ET

def checkout(fixed_version=False):
    global cur_path,project,subj,ver
    
    if fixed_version:
        if os.path.exists(f'{cur_path}/buggy/{project}f'):
            shutil.rmtree(f'{cur_path}/buggy/{project}f')
        result=subprocess.run(['defects4j','checkout','-p',subj,'-v',f'{ver}f','-w',f'{cur_path}/buggy/{project}f'])
        result=subprocess.run(['defects4j','compile','-w',f'{cur_path}/buggy/{project}f'])
    else:
        if os.path.exists(f'{cur_path}/buggy/{project}'):
            shutil.rmtree(f'{cur_path}/buggy/{project}')
        result=subprocess.run(['defects4j','checkout','-p',subj,'-v',f'{ver}b','-w',f'{cur_path}/buggy/{project}'])
        result=subprocess.run(['defects4j','compile','-w',f'{cur_path}/buggy/{project}'])

def get_src_paths(project):
    project_name, bug_id = project.split('_')
    if len(bug_id)>=4:
        bug_id=bug_id[:-3]
    bug_id = int(bug_id)

    if project_name=='Math':
        if bug_id < 85:
            return '/src/main/java'
        else:
            return '/src/java'
    elif project_name=='Time':
        return '/src/main/java'
    elif project_name=='Lang':
        if bug_id <= 35:
            return '/src/main/java'
        else:
            return '/src/java'
    elif project_name=='Chart':
        return '/source'
    elif project_name=='Closure':
        return '/src'
    elif project_name=='Mockito':
        return '/src'
    
    # D4J 2.0
    elif project_name=='Cli':
        if 30 <= bug_id <= 40:
            return '/src/main/java'
        else:
            return '/src/java'
    elif project_name=='Codec':
        if bug_id <= 10:
            return '/src/java'
        else:
            return '/src/main/java'
    elif project_name=='Collections':
        return '/src/main/java'
    elif project_name=='Compress':
        return '/src/main/java'
    elif project_name=='Csv':
        return '/src/main/java'
    elif project_name=='Gson':
        return '/gosn/src/main/java'
    elif project_name=='JacksonCore':
        return '/src/main/java'
    elif project_name=='JacksonDatabind':
        return '/src/main/java'
    elif project_name=='JacksonXml':
        return '/src/main/java'
    elif project_name=='Jsoup':
        return '/src/main/java'
    elif project_name=='JxPath':
        return '/src/java'
    else:
        raise Exception("Unknown project: "+project_name)

def run_test(work_dir: str, buggy_project: str) -> Tuple[int, List[str]]:
    if buggy_project.startswith('Mockito'):
        # Mockito should use modified project structure by Ali Ghanbari
        cmd=['mvn','test']
        test_proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=work_dir)
    else:
        cmd = ["defects4j", "test", "-w", work_dir]
        test_proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    result_str = test_proc.stdout.decode('utf-8').strip()
    err_str = test_proc.stderr.decode('utf-8').strip()
    # print(err_str, file=sys.stderr)
    error_num = -1
    failed_tests = list()
    if buggy_project.startswith('Mockito'):
        error_num=0
        if buggy_project.split('_')[1] not in ('23','24','25','26','38'):
            for line in result_str.splitlines():
                line=line.strip()
                if ('<<< ERROR!' in line or '<<< FAILURE!' in line) and not line.startswith('Tests run:'):
                    temp_str=line.split(' ')[0]
                    error_class=temp_str.split('(')[1][:-1]
                    error_method=temp_str.split('(')[0]
                    failed_tests.append(error_class+'::'+error_method)
                    error_num+=1
        else:
            # Version that using surefire plugin
            cur_tests=[]
            for _f in os.listdir(f'{work_dir}/target/surefire-reports'):
                if _f.startswith('TEST-') and _f.endswith('.xml'):
                    removed_test=_f.split('-')[1].split('.')[:-1]
                    cur_tests.append('.'.join(removed_test))

            for _test in cur_tests:
                with open(f'{work_dir}/target/surefire-reports/TEST-{_test}.xml','r') as f:
                    tree=ET.parse(f)
                    root=tree.getroot()
                    for child in root:
                        if child.tag=='testcase':
                            if len(child)!=0 and (child[0].tag=='failure' or child[0].tag=='error'):
                                failed_tests.append(child.attrib['classname']+'::'+child.attrib['name'])
                                error_num+=1
    else:
        for line in result_str.splitlines():
            line = line.strip()
            if line.startswith("Failing tests:"):
                error_num = int(line.split(":")[1].strip())
                continue
            if line.startswith("-"):
                ft = line.replace("-", "").strip()
                failed_tests.append(ft)
    return error_num, failed_tests

def extract_input():
    global cur_path,project,subj,ver
    result=subprocess.run(['java','-jar',f'{cur_path}/DatasetExtractor/build/libs/DatasetExtractor-0.0.1-all.jar',
                    f'{cur_path}/SuspiciousCodePositions/{project}/Ochiai.txt',
                    f'{cur_path}/buggy/{project}{get_src_paths(project)}',f'{cur_path}/SRepair/dataset',
                    project,f'{cur_path}/d4j'])
    
total_patches=0
MAX_FL_RANK=40

def run_solution_and_gen(skip_solution=False,skip_gen_patch=False,skip_postprocess=False):
    global cur_path,project,subj,ver,json_patch_tree
    info_path=f'{cur_path}/d4j/{project}/input'
    for file in os.listdir(info_path):
        info_file=os.path.join(info_path,file)
        cur_fl_rank=int(file.split('.')[0])
        if cur_fl_rank>MAX_FL_RANK:
            break

        if not skip_solution:
            if not os.path.exists(f'{cur_path}/d4j/{project}/solution'):
                os.makedirs(f'{cur_path}/d4j/{project}/solution')
            # Get solution
            result=subprocess.run(['python3',f'{cur_path}/SRepair/src/sf_gen_solution.py','-d',info_file,
                                '-o',f'{cur_path}/d4j/{project}/solution/{cur_fl_rank}.json','-s','2','-bug',project,'-fl'])
        
    for file in os.listdir(info_path):
        info_file=os.path.join(info_path,file)
        cur_fl_rank=int(file.split('.')[0])
        if cur_fl_rank>MAX_FL_RANK:
            break
        
        if not skip_gen_patch:
            if not os.path.exists(f'{cur_path}/d4j/{project}/patches'):
                os.makedirs(f'{cur_path}/d4j/{project}/patches')
            # Generate actual patches
            result=subprocess.run(['python3',f'{cur_path}/SRepair/src/sf_gen_patch.py','-d',info_file,
                                '-o',f'{cur_path}/d4j/{project}/patches/{cur_fl_rank}.json',
                                '-s',f'{cur_path}/d4j/{project}/solution/{cur_fl_rank}_extracted.json','-bug',project,'-fl'])
        
        if not skip_postprocess:
            with open(info_file,'r') as f:
                input_root=json.load(f)[project]
            source_file_path=input_root['file_path']
            start_line=input_root['start_line']
            end_line=input_root['end_line']

            with open(f'{cur_path}/d4j/{project}/patches/{cur_fl_rank}.json','r') as f:
                patches=json.load(f)[project]['patches']

            with open(source_file_path,'r') as f:
                source_code=f.readlines()

            for patch in patches:
                global total_patches
                total_patches+=1
                patched_code=source_code[:start_line-1]+[patch]+source_code[end_line:]

                if not os.path.exists(f'{cur_path}/d4j/{project}/{cur_fl_rank}'):
                    os.mkdir(f'{cur_path}/d4j/{project}/{cur_fl_rank}')
                if os.path.exists(f'{cur_path}/d4j/{project}/{cur_fl_rank}/{total_patches}'):
                    shutil.rmtree(f'{cur_path}/d4j/{project}/{cur_fl_rank}/{total_patches}')
                os.mkdir(f'{cur_path}/d4j/{project}/{cur_fl_rank}/{total_patches}')
                
                with open(f'{cur_path}/d4j/{project}/{cur_fl_rank}/{total_patches}/{source_file_path.split("/")[-1]}','w') as f:
                    f.writelines(patched_code)

                # Store patch tree
                buggy_loc=input_root['location']
                for file in json_patch_tree:
                    if file['file']==f'{get_src_paths(project)[1:]}/{buggy_loc["file"]}.java':
                        cur_file=file
                        break
                else:
                    cur_file={'file':f'{get_src_paths(project)[1:]}/{buggy_loc["file"]}.java','functions':[]}
                    json_patch_tree.append(cur_file)
                
                for func in cur_file['functions']:
                    if func['function']==f'{input_root["method_signature"]["method_name"]}:{input_root["start_line"]}-{input_root["end_line"]}':
                        cur_func=func
                        break
                else:
                    cur_func={'function':f'{input_root["method_signature"]["method_name"]}:{input_root["start_line"]}-{input_root["end_line"]}','lines':[]}
                    cur_file['functions'].append(cur_func)

                for line in cur_func['lines']:
                    if line['line']==buggy_loc['line']:
                        cur_line=line
                        break
                else:
                    cur_line={'line':buggy_loc['line'],'fl_score':buggy_loc['score'],'file':f'{get_src_paths(project)[1:]}/{buggy_loc["file"]}.java','cases':[]}
                    cur_func['lines'].append(cur_line)

                cur_line['cases'].append({'case':total_patches,'location':f'{cur_fl_rank}/{total_patches}/{source_file_path.split("/")[-1]}'})
                json_original_rank.append(f'{cur_fl_rank}/{total_patches}/{source_file_path.split("/")[-1]}')

import argparse

parser=argparse.ArgumentParser()
parser.add_argument('-skip-extract',action='store_true')
parser.add_argument('-skip-solution',action='store_true')
parser.add_argument('-skip-gen',action='store_true')
parser.add_argument('-skip-postprocess',action='store_true')
parser.add_argument('project',type=str)

args=parser.parse_args()

project=args.project
cur_path=os.path.abspath(os.path.dirname(__file__))

# Checkout and compile project
subj,ver=project.split('_')
json_output_root=dict()
json_output_root['project_name']=project

checkout()
if not args.skip_postprocess:
    # Find failing test cases
    checkout(fixed_version=True)
    failed_passing_num,failed_passing_tests=run_test(f'{cur_path}/buggy/{project}f',project)

    res=subprocess.run(['defects4j','export','-p','tests.trigger','-w',f'{cur_path}/buggy/{project}'],stdout=subprocess.PIPE)
    json_output_root['failing_test_cases']=res.stdout.decode('utf-8').splitlines()

    res=subprocess.run(['defects4j','export','-p','tests.all','-w',f'{cur_path}/buggy/{project}'],stdout=subprocess.PIPE)
    json_output_root['passing_test_cases']=res.stdout.decode('utf-8').splitlines()

    json_output_root['failed_passing_tests']=failed_passing_tests

    # Store FL result
    with open(f'{cur_path}/SuspiciousCodePositions/{project}/Ochiai.txt','r') as f:
        fls=[]
        for line in f:
            file,line,score=line.split('@')
            fls.append({
                'file':get_src_paths(project)[1:]+'/'+file.replace('.','/')+'.java',
                'line':int(line),
                'score':float(score)
            })
        
        json_output_root['priority']=fls

json_patch_tree=[]
json_original_rank=[]

if not args.skip_extract:
    extract_input()
run_solution_and_gen(args.skip_solution,args.skip_gen,args.skip_postprocess)

if not args.skip_postprocess:
    # Save patch tree
    json_output_root['rules']=json_patch_tree
    json_output_root['ranking']=json_original_rank

    with open(f'{cur_path}/d4j/{project}/switch-info.json','w') as f:
        json.dump(json_output_root,f,indent=2)