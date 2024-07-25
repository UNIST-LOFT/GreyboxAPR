import sys
import d4j
import subprocess
import json
import os
import shutil

def get_src_paths(project):
    project_name, bug_id = project.split('_')
    if len(bug_id)>=4:
        bug_id=bug_id[:-3]
    bug_id = int(bug_id)

    if project_name=='Math':
        if bug_id < 85:
            return '/src/main/java/','/src/test/java/'
        else:
            return '/src/java/','/src/test/'
    elif project_name=='Time':
        return '/src/main/java/','/src/test/java/'
    elif project_name=='Lang':
        if bug_id <= 35:
            return '/src/main/java/','/src/test/java/'
        else:
            return '/src/java/','/src/test/'
    elif project_name=='Chart':
        return '/source/','/tests/'
    elif project_name=='Closure':
        return '/src/','/test/'
    elif project_name=='Mockito':
        return '/src/','/test/'

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
    shutil.rmtree(f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}',ignore_errors=True)
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{id}f','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'checkout {subject}-{id} failed')
    
    shutil.rmtree(f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}b',ignore_errors=True)
    res=subprocess.run(['defects4j','checkout','-p',subject,'-v',f'{id}b','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}b'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'checkout {subject}-{id} failed')

    src_path=f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}'+get_src_paths(f'{subject}_{id}')[0]
    shutil.copytree(f'/root/project/JPatchInst/src/main/resources/kr',src_path+'/kr',dirs_exist_ok=True)

    print(f'compile {subject}-{id}')
    res=subprocess.run(['defects4j','compile','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'compile {subject}-{id} failed')
    
    res=subprocess.run(['defects4j','compile','-w',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}b'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'compile {subject}-{id} failed')
    
def instrument(subject:str,id:int):
    print(f'instrument {subject}-{id}')
    res=subprocess.run(['java','-Xmx100G','-jar','/root/project/JPatchInst/build/libs/JPatchInst.jar',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}b/{get_target_paths(f"{subject}_{id}")[0]}',
                        f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}/{get_target_paths(f"{subject}_{id}")[0]}'],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(res.stdout.decode())
        print(f'instrument {subject}-{id} failed')

def test(subject:str,id:int,tool:str):
    if not os.path.exists(f'/root/project/GreyboxAPR/{tool}/d4j/{subject}_{id}/switch-info.json'): return
    with open(f'/root/project/GreyboxAPR/{tool}/d4j/{subject}_{id}/switch-info.json') as f:
        switch_info=json.load(f)
        failing_tests=switch_info['failing_test_cases']

    print(f'test {subject}-{id}')
    for test in failing_tests:
        new_env=os.environ.copy()
        new_env['GREYBOX_BRANCH']='1'
        new_env['GREYBOX_RESULT']=f'/root/project/GreyboxAPR/experiments/scripts/correct-branch/{subject}_{id}-{test.replace("::","#")}.txt'

        res=subprocess.run(['defects4j','test','-w',
                            f'/root/project/GreyboxAPR/experiments/scripts/correct-version/{subject}_{id}',
                            '-t',test],stdout=subprocess.PIPE, stderr=subprocess.STDOUT,env=new_env)

TBAR_LIST=['Chart_1','Chart_4','Chart_8','Chart_9','Chart_11','Chart_12','Chart_20','Chart_24','Chart_26',
'Closure_10','Closure_11','Closure_18','Closure_31','Closure_38','Closure_46','Closure_62','Closure_63','Closure_86','Closure_115','Closure_126',
'Lang_6','Lang_10','Lang_24','Lang_26','Lang_33','Lang_39','Lang_51','Lang_57','Lang_59',
'Math_5','Math_11','Math_30','Math_33','Math_34','Math_50','Math_57','Math_58','Math_59','Math_65','Math_70','Math_75','Math_80','Math_82','Math_85',
'Time_19',
]

AVATAR_LIST=['Chart_1','Chart_4','Chart_7','Chart_8','Chart_11','Chart_14','Chart_19','Chart_24','Chart_26',
'Closure_2','Closure_11','Closure_18','Closure_21','Closure_22','Closure_31','Closure_38','Closure_46','Closure_62','Closure_63','Closure_73','Closure_115','Closure_126',
'Lang_6','Lang_10','Lang_24','Lang_26','Lang_33','Lang_39','Lang_51','Lang_57','Lang_59',
'Math_5','Math_11','Math_30','Math_33','Math_34','Math_50','Math_57','Math_58','Math_59','Math_65','Math_70','Math_75','Math_80','Math_82','Math_85',
'Time_19'
]

FIXMINER_LIST=[
'Chart_1','Chart_11','Chart_19','Chart_24','Chart_4',
'Closure_10','Closure_38','Closure_62','Closure_63','Closure_73',
'Lang_57','Lang_59',
'Math_22','Math_30','Math_33','Math_34','Math_35','Math_57','Math_70','Math_75','Math_79','Math_82',
'Time_19'
]

KPAR_LIST=[
'Chart_1','Chart_14','Chart_19','Chart_26','Chart_4','Chart_7','Chart_8',
'Closure_10','Closure_18','Closure_2','Closure_31','Closure_38','Closure_4','Closure_40','Closure_62','Closure_63','Closure_70','Closure_73',
'Lang_22','Lang_24','Lang_59','Lang_6',
'Math_15','Math_33','Math_4','Math_58','Math_70','Math_75','Math_82','Math_85','Math_89',
'Time_19','Time_26','Time_7'
]

ALPHAREPAIR_LIST=['Chart_1','Chart_8','Chart_9','Chart_11','Chart_24','Chart_26',
'Closure_2','Closure_19','Closure_21','Closure_46','Closure_57','Closure_62','Closure_73','Closure_77','Closure_86','Closure_92','Closure_93','Closure_109','Closure_115',
'Lang_4','Lang_6','Lang_10','Lang_29','Lang_33','Lang_38','Lang_43','Lang_45','Lang_51','Lang_55','Lang_57','Lang_59','Lang_61',
'Math_2','Math_5','Math_11','Math_30','Math_34','Math_41','Math_50','Math_56','Math_57','Math_59','Math_63','Math_65','Math_70','Math_75','Math_80','Math_90','Math_94','Math_96','Math_98',
'Time_4','Time_7'
]

RECODER_LIST=['Chart_1','Chart_3','Chart_4','Chart_8','Chart_9','Chart_11','Chart_12','Chart_20','Chart_24','Chart_26',
'Closure_2','Closure_7','Closure_14','Closure_21','Closure_33','Closure_40','Closure_46','Closure_57','Closure_62','Closure_63','Closure_73','Closure_86','Closure_92','Closure_93','Closure_104','Closure_109','Closure_115','Closure_118','Closure_126',
'Lang_6','Lang_26','Lang_29','Lang_33','Lang_43','Lang_51','Lang_55','Lang_57','Lang_59',
'Math_5','Math_27','Math_30','Math_33','Math_34','Math_41','Math_50','Math_57','Math_58','Math_65','Math_70','Math_75','Math_82','Math_94','Math_96','Math_98','Math_105',
'Time_4','Time_7'
]

SREPAIR_LIST=[
'Chart_11','Chart_12','Chart_13','Chart_17','Chart_1','Chart_20','Chart_24','Chart_26','Chart_4','Chart_5','Chart_7','Chart_8','Chart_9',
'Closure_101','Closure_102','Closure_104','Closure_115','Closure_117','Closure_119','Closure_11','Closure_124','Closure_125','Closure_126','Closure_128','Closure_129','Closure_131','Closure_13','Closure_14','Closure_152','Closure_15','Closure_168','Closure_18','Closure_19','Closure_22','Closure_2','Closure_31','Closure_36','Closure_38','Closure_40','Closure_44','Closure_51','Closure_52','Closure_53','Closure_55','Closure_56','Closure_57','Closure_58','Closure_59','Closure_5','Closure_61','Closure_62','Closure_65','Closure_66','Closure_71','Closure_73','Closure_77','Closure_78','Closure_86','Closure_92','Closure_97',
'Lang_10','Lang_11','Lang_14','Lang_16','Lang_17','Lang_21','Lang_24','Lang_26','Lang_28','Lang_31','Lang_33','Lang_37','Lang_39','Lang_40','Lang_42','Lang_43','Lang_44','Lang_45','Lang_51','Lang_52','Lang_53','Lang_55','Lang_57','Lang_59','Lang_61','Lang_9',
'Math_101','Math_103','Math_105','Math_106','Math_11','Math_15','Math_17','Math_23','Math_25','Math_26','Math_27','Math_2','Math_30','Math_33','Math_34','Math_3','Math_41','Math_42','Math_43','Math_50','Math_53','Math_56','Math_57','Math_59','Math_5','Math_60','Math_69','Math_70','Math_72','Math_75','Math_79','Math_80','Math_82','Math_85','Math_86','Math_89','Math_8','Math_90','Math_91','Math_94','Math_95','Math_96',
'Time_15','Time_16','Time_18','Time_19','Time_20','Time_27','Time_4'
]

SELFAPR_LIST=[
'Chart_11','Chart_1','Chart_20','Chart_5','Chart_7','Chart_8',
'Closure_106','Closure_113','Closure_115','Closure_123','Closure_125','Closure_126','Closure_18','Closure_38','Closure_46','Closure_57','Closure_62','Closure_6','Closure_70','Closure_73','Closure_75','Closure_79','Closure_86','Closure_92',
'Lang_21','Lang_26','Lang_34','Lang_59','Lang_60','Lang_6','Lang_7',
'Math_104','Math_22','Math_30','Math_33','Math_41','Math_49','Math_50','Math_57','Math_5','Math_70','Math_72','Math_75','Math_77','Math_79','Math_80','Math_82','Math_85'
]

if __name__ == "__main__":
    if sys.argv[1]=='tbar':
        tool='TBar'
    elif sys.argv[1]=='avatar':
        tool='Avatar'
    elif sys.argv[1]=='fixminer':
        tool='Fixminer'
    elif sys.argv[1]=='kpar':
        tool='kPar'
    elif sys.argv[1]=='alpharepair':
        tool='AlphaRepair'
    elif sys.argv[1]=='recoder':
        tool='Recoder'
    elif sys.argv[1]=='srepair':
        tool='SRepair'
    elif sys.argv[1]=='selfapr':
        tool='SelfAPR'

    if sys.argv[1]=='tbar':
        benchmarks=TBAR_LIST
    elif sys.argv[1]=='avatar':
        benchmarks=AVATAR_LIST
    elif sys.argv[1]=='fixminer':
        benchmarks=FIXMINER_LIST
    elif sys.argv[1]=='kpar':
        benchmarks=KPAR_LIST
    elif sys.argv[1]=='alpharepair':
        benchmarks=ALPHAREPAIR_LIST
    elif sys.argv[1]=='recoder':
        benchmarks=RECODER_LIST
    elif sys.argv[1]=='srepair':
        benchmarks=SREPAIR_LIST
    elif sys.argv[1]=='selfapr':
        benchmarks=SELFAPR_LIST

    for project in benchmarks:
        project_name, bug_id = project.split('_')
        bug_id = int(bug_id)
        checkout(project_name,bug_id)
        instrument(project_name,bug_id)
        test(project_name,bug_id,tool)