import d4j
import subprocess
import json
import os

def get_target_paths(project):
    project_name, bug_id = project.split('_')
    if len(bug_id)>=4:
        bug_id=bug_id[:-3]
    bug_id = int(bug_id)

    if project_name == "Math":
        return "/target/classes/", "/target/test-classes/"
    elif project_name == "Time":
        if bug_id < 12:
            return "/target/classes/", "/target/test-classes/"
        return "/build/classes/", "/build/tests/"
    elif project_name == "Lang":
        if bug_id <= 20 or 42 <= bug_id <= 65:
            return "/target/classes/", "/target/tests/"
        elif 21 <= bug_id <= 41:
            return "/target/classes/", "/target/test-classes/"
    elif project_name == "Chart":
        return "/build/", "/build-tests/"
    elif project_name == "Closure":
        return "/build/classes/", "/build/test/"
    elif project_name == "Mockito":
        # if 11 >= bug_id or 18 <= bug_id <= 21:
        #   return "/build/classes/main/", "/build/classes/test/"
        return "/target/classes/", "/target/test-classes/"

def checkout(subject:str,id:int):
    print(f'checkout {subject}-{id}')
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{id}f','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'checkout {subject}-{id} failed')
    
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{id}f','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}f'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'checkout {subject}-{id} failed')
    
    print(f'compile {subject}-{id}')
    res=subprocess.run(['defects4j','compile','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'compile {subject}-{id} failed')
    
    res=subprocess.run(['defects4j','compile','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}f'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'compile {subject}-{id} failed')
    
def instrument(subject:str,id:int):
    print(f'instrument {subject}-{id}')
    res=subprocess.run(['java','-Xmx100G','-jar','/root/project/JPatchInst/build/libs/JPatchInst.jar',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}f/{get_target_paths(f"{subject}_{id}")[0]}',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}/{get_target_paths(f"{subject}_{id}")[0]}'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'instrument {subject}-{id} failed')

def test(subject:str,id:int):
    with open(f'/root/project/GreyboxAPR/TBar/d4j/{subject}_{id}/switch-info.json') as f:
        switch_info=json.load(f)
        failing_tests=switch_info['failing_test_cases']

    print(f'test {subject}-{id}')
    for test in failing_tests:
        new_env=os.environ.copy()
        new_env['GREYBOX_BRANCH']='1'
        new_env['GREYBOX_RESULT']=f'/tmp/{subject}_{id}-{test.replace("::","#")}.txt'

        res=subprocess.run(['defects4j','test','-w',
                            f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}',
                            '-t',test],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        if os.path.exists(new_env['GREYBOX_RESULT']):
            os.rename(new_env['GREYBOX_RESULT'],f'/root/project/GreyboxAPR/experiments/scripts/correct-branch/{subject}_{id}/{test.replace("::","#")}.txt')

if __name__ == "__main__":
    for project in d4j.D4J_1_2_LIST:
        project_name, bug_id = project.split('_')
        bug_id = int(bug_id)
        checkout(project_name,bug_id)
        instrument(project_name,bug_id)
        test(project_name,bug_id)