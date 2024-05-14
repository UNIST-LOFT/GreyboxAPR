from sys import argv
import subprocess
from os import getcwd,environ,path
from time import time

def get_target_paths(project):
    project_name, bug_id = project.split('_')
    bug_id = int(bug_id)

    if project_name == "Math":
        return "/target/classes/"
    elif project_name == "Time":
        if bug_id < 12:
            return "/target/classes/"
        return "/build/classes/", "/build/tests/"
    elif project_name == "Lang":
        if bug_id <= 20 or 42 <= bug_id <= 65:
            return "/target/classes/"
        elif 21 <= bug_id <= 41:
            return "/target/classes/"
    elif project_name == "Chart":
        return "/build/"
    elif project_name == "Closure":
        return "/build/classes/"
    elif project_name == "Mockito":
        return "/target/classes/"
    
    # D4J 2.0
    elif project_name == "Cli":
        return '/target/classes/'
    elif project_name == "Codec":
        if bug_id <=16:
            return "/target/classes/"
        return "/target/classes/"
    elif project_name == "Collections":
        return '/target/classes/'
    elif project_name == "Compress":
        return '/target/classes/'
    elif project_name == "Csv":
        return '/target/classes/'
    elif project_name == "Gson":
        return '/target/classes/'
    elif project_name == "JacksonCore":
        return '/target/classes/'
    elif project_name == "JacksonDatabind":
        return '/target/classes/'
    elif project_name == "JacksonXml":
        return '/target/classes/'
    elif project_name == "Jsoup":
        return '/target/classes/'
    elif project_name == "JxPath":
        return '/target/classes/'
    raise Exception("Unknown project: "+project_name)

def checkout(project:str):
    subject,version=project.split('_')
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{version}b','-w',f'{getcwd()}/{project}'])
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{version}b','-w',f'{getcwd()}/{project}b'])

def compile(project:str):
    res=subprocess.run(['defects4j','compile','-w',f'{getcwd()}/{project}b'])
    start_time=time()
    res=subprocess.run(['defects4j','compile','-w',f'{getcwd()}/{project}'])
    return time()-start_time

def instrument(project:str):
    start_time=time()
    res=subprocess.run(['java','-Xmx100G','-jar','/root/project/JPatchInst/build/libs/JPatchInst.jar',
                        f'{getcwd()}/{project}{get_target_paths(project)}b',
                        f'{getcwd()}/{project}{get_target_paths(project)}'])
    return time()-start_time

def test(project:str,test:str): # Return (orig time, instrumented time, branch count, branch hit count)
    start_time=time()
    res=subprocess.run(['defects4j','test','-w',f'{getcwd()}/{project}b','-t',test])
    end_time=time()-start_time

    new_env=environ.copy()
    new_env['GREYBOX_BRANCH']='1'
    new_env['GREYBOX_RESULT']=f'/tmp/{project}-{test.replace("::","#")}.txt'
    start_time=time()
    res=subprocess.run(['defects4j','test','-w',f'{getcwd()}/{project}','-t',test])
    new_end_time=time()-start_time

    def parse_cov(cov_file: str):
        """
        :param cov_file: branch coverage file
        :return: branch coverage vector
        """
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
    if not path.exists(f'/root/project/GreyboxAPR/TBar/d4j/{bug}/switch-info.json'):
        return {
            'compile_time':0.,
            'instrument_time':0.,
            'test_result':{}
        }
    
    checkout(bug)
    compile_time=compile(bug)
    instrument_time=instrument(bug)
    
    with open(f'/root/project/GreyboxAPR/TBar/d4j/{bug}/switch-info.json') as f:
        failing_tests=json.load(f)['failing_test_cases']

    test_result=dict()
    for test_case in failing_tests:
        orig_test_time,new_test_time,branch_count,branch_hit_count=test(bug,test_case)
        test_result[test_case]={'orig_time':orig_test_time,'instrumented_time':new_test_time,
                                'branch_count':branch_count,'branch_hit_count':branch_hit_count}
    
    shutil.rmtree(f'{getcwd()}/{bug}')
    return {
        'compile_time':compile_time,
        'instrument_time':instrument_time,
        'test_result':test_result
    }
        
tool=argv[1]

total_result=dict()
for bug in benchmarks.D4J_1_2_0_LIST:
    result=get_result(bug)
    total_result[bug]=result
    print(f'{bug}: {result["compile_time"]}, {result["instrument_time"]}, {result["test_result"]["branch_count"]}')

with open(f'{getcwd()}/test-time.json','w') as f:
    json.dump(total_result,f)