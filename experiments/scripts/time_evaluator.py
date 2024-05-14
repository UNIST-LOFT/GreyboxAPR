from sys import argv
import subprocess
from os import getcwd,environ,path
from time import time

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

def get_target_paths(project):
    project_name, bug_id = project.split('_')
    bug_id = int(bug_id)

    if project_name == "Math":
        return "/target/classes"
    elif project_name == "Time":
        if bug_id < 12:
            return "/target/classes"
        return "/build/classes"
    elif project_name == "Lang":
        if bug_id <= 20 or 42 <= bug_id <= 65:
            return "/target/classes"
        elif 21 <= bug_id <= 41:
            return "/target/classes"
    elif project_name == "Chart":
        return "/build"
    elif project_name == "Closure":
        return "/build/classes"
    elif project_name == "Mockito":
        return "/target/classes"
    
    # D4J 2.0
    elif project_name == "Cli":
        return '/target/classes'
    elif project_name == "Codec":
        if bug_id <=16:
            return "/target/classes"
        return "/target/classes"
    elif project_name == "Collections":
        return '/target/classes'
    elif project_name == "Compress":
        return '/target/classes'
    elif project_name == "Csv":
        return '/target/classes'
    elif project_name == "Gson":
        return '/target/classes'
    elif project_name == "JacksonCore":
        return '/target/classes'
    elif project_name == "JacksonDatabind":
        return '/target/classes'
    elif project_name == "JacksonXml":
        return '/target/classes'
    elif project_name == "Jsoup":
        return '/target/classes'
    elif project_name == "JxPath":
        return '/target/classes'
    raise Exception("Unknown project: "+project_name)

def checkout(project:str):
    subject,version=project.split('_')
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{version}b','-w',f'{getcwd()}/{project}'])
    if res.returncode!=0:
        raise RuntimeError(f'{project} checkout fail!')
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{version}b','-w',f'{getcwd()}/{project}b'])
    if res.returncode!=0:
        raise RuntimeError(f'{project} checkout fail!')

def compile(project:str):
    shutil.copytree(f'/root/project/JPatchInst/src/main/resources/kr',f'{getcwd()}/{project}{get_src_paths(project)}/kr',
                    dirs_exist_ok=True)
    res=subprocess.run(['defects4j','compile','-w',f'{getcwd()}/{project}'])
    if res.returncode!=0:
        raise RuntimeError(f'{project} compile fail!')
    
    start_time=time()
    res=subprocess.run(['defects4j','compile','-w',f'{getcwd()}/{project}b'])
    if res.returncode!=0:
        raise RuntimeError(f'{project} compile fail!')
    return time()-start_time

def instrument(project:str): # Return (time, branch_instrumented)
    start_time=time()
    res=subprocess.run(['java','-Xmx100G','-jar','/root/project/JPatchInst/build/libs/JPatchInst.jar',
                        f'{getcwd()}/{project}b{get_target_paths(project)}',
                        f'{getcwd()}/{project}{get_target_paths(project)}'],
                        stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if res.returncode!=0:
        raise RuntimeError(f'{project} instrument fail!')
    
    lines=res.stdout.decode().splitlines()
    for line in lines:
        if 'Total instrumented' in line:
            instrumented=int(line.split(' ')[-1].strip())
    return time()-start_time,instrumented

def test(project:str,test:str): # Return (orig time, instrumented time, branch count, branch hit count)
    start_time=time()
    res=subprocess.run(['defects4j','test','-w',f'{getcwd()}/{project}b','-t',test])
    end_time=time()-start_time

    new_env=environ.copy()
    new_env['GREYBOX_BRANCH']='1'
    new_env['GREYBOX_RESULT']=f'/tmp/{project}-{test.replace("::","#")}.txt'
    start_time=time()
    res=subprocess.run(['defects4j','test','-t',test],env=new_env,cwd=f'{getcwd()}/{project}')
    new_end_time=time()-start_time

    def parse_cov(cov_file: str):
        branch_cov=dict()
        with open(cov_file, 'r') as f:
            for line in f:
                try:
                    branch_id,count=line.strip().split(":")
                    branch_cov[int(branch_id)]=int(count)
                except:
                    pass
        return branch_cov

    if path.exists(new_env['GREYBOX_RESULT']):
        branch_cov=parse_cov(new_env['GREYBOX_RESULT'])
        return end_time,new_end_time,len(branch_cov),sum(branch_cov.values())
    else:
        return end_time,new_end_time,0,0
    
import benchmarks
import json
import shutil

def get_result(bug:str):
    global tool
    if not path.exists(f'/root/project/GreyboxAPR/{tool}/d4j/{bug}/switch-info.json'):
        return {
            'compile_time':0.,
            'instrument_time':0.,
            'instrument_branch':0,
            'test_result':{}
        }
    
    checkout(bug)
    compile_time=compile(bug)
    instrument_time,instrumented_branch=instrument(bug)
    
    with open(f'/root/project/GreyboxAPR/{tool}/d4j/{bug}/switch-info.json') as f:
        failing_tests=json.load(f)['failing_test_cases']

    test_result=dict()
    for test_case in failing_tests:
        orig_test_time,new_test_time,branch_count,branch_hit_count=test(bug,test_case)
        test_result[test_case]={'orig_time':orig_test_time,'instrumented_time':new_test_time,
                                'branch_count':branch_count,'branch_hit_count':branch_hit_count}
    
    shutil.rmtree(f'{getcwd()}/{bug}')
    shutil.rmtree(f'{getcwd()}/{bug}b')
    return {
        'compile_time':compile_time,
        'instrument_time':instrument_time,
        'instrument_branch':instrumented_branch,
        'test_result':test_result
    }
        
tool=argv[1]

total_result=dict()
for bug in benchmarks.D4J_1_2_0_LIST:
    result=get_result(bug)
    total_result[bug]=result
    if result['compile_time']!=0.:
        print(f'{bug}: {result["compile_time"]}, {result["instrument_time"]}, {result["test_result"]}')

    with open(f'{getcwd()}/test-time.json','w') as f:
        json.dump(total_result,f,indent=4)