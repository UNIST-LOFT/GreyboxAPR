from sys import argv

project=argv[1]

import subprocess
import os
import shutil

cur_path=os.path.abspath(os.path.dirname(__file__))

# Checkout and compile project
subj,ver=project.split('_')

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

result=subprocess.run(['java','-jar',f'{cur_path}/DatasetExtractor/build/libs/DatasetExtractor-0.0.1-all.jar',
                f'{cur_path}/SuspiciousCodePositions_updated/{project}/Ochiai.txt',
                f'{cur_path}/buggy/{project}{get_src_paths(project)}',f'{cur_path}/SRepair/dataset',
                project,f'{cur_path}/d4j'])