#!/usr/bin/python
import sys, os, time, subprocess,fnmatch, shutil, csv,re, datetime
from typing import List, Set, Dict, Tuple

FILE_LOC = os.path.abspath(__file__)
ROOT_DIR = os.path.dirname(os.path.dirname(FILE_LOC)) 

def start(bug_id, repodir):
    #get buggy file and buggy line
    print(f"[bugid] {bug_id}")

    targets = get_buggy_files(bug_id, repodir)

    for key, value in targets.items():
        if '.java' not in tf:
            tf=tf+'.java'
        diffLists = getBuggyLines(bug_id,repodir,tf)
        print('======diffLists========='+str(diffLists))
        
        if len(diffLists)>1:
            return;
        
        for k in range(0,len(diffLists)):
            diff=diffLists[k]
            startLineNo=diff.split('[buggy]')[0]
            buggyLines=diff.split('[buggy]')[1]
            buggyLines=buggyLines.split('[patch]')[0]
            patchLines = diff.split('[patch]')[1]
            patchLines = patchLines.split('[buggyLineNo]')[0]
            buggyLineCount = diff.split('[buggyLineNo]')[1]
        

            if str(startLineNo) not in '':
                constructTestSample(bug_id, k, tf, repodir, rootdir,str(startLineNo),buggyLines,patchLines,str(len(diffLists)),str(buggyLineCount))
   
    if os.path.exists(repodir+'/'+bug_id):
        os.system('rm -rf '+repodir+'/'+bug_id)

def get_buggy_files(bug_id) -> Dict[str, Set[int]]:
    sus_pos = os.path.join(ROOT_DIR, "SuspiciousCodePositions", bug_id, "Ochiai.txt")
    file_lines = dict()
    with open(sus_pos, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            class_name, line_no, score = line.split("@")
            if "$" in class_name:
                class_name = class_name.split("$")[0]
            class_name = class_name.replace(".", "/") + ".java"
            if class_name not in file_lines:
                file_lines[class_name] = set()
            file_lines[class_name].add(line_no)
    return file_lines


def get_buggy_lines(bug_id: str, repodir: str, filename: str, lines: Set[int]) -> List[str]:
    tclass = os.path.basename(filename)
    tclass = tclass.replace('.java', '').replace('\n', ' ').replace('\r', ' ')
    print(tclass)
    with open(os.path.join(repodir, bug_id, filename), 'r', encoding='latin1', errors="ignore") as f:
        contents = f.readlines()
        for line in lines:
            content = contents[line - 1]
            
            

def getBuggyLines(bugId,repodir,tf):
    tclass=tf.split('/')[-1]
    tclass=tclass.replace('.java','').replace('\n',' ').replace('\r',' ')
    print(tclass)
    projectPath=repodir+repodir
    tdiff = repodir+'scripts/D4JDiff/'+bugId+'_'+tclass+'.diff'

    diffList=[]
    with open(tdiff,'r', encoding='latin1') as diff:
        lines = diff.readlines()
        hunks = str(lines).split('@@ -')
        for i in range(1,len(hunks)):
            h = hunks[i]
            startLineNo=''
            buggyLines=''
            patchLines=''
            buggyLineNo=0
            print('*********hunk hunk hunk***********'+h)
            lines = h.split("\\n', '")
            for l in lines:
                if '@@' in l and '+' in l and ',' in l:
                    startLineNo= l.split(',')[0]
                    startLineNo= str(int(startLineNo)+1)   
                
                if l.startswith('-'):
                    startword = l[1:]
                    startword = startword.replace("\\n', \"+ ",' ')
                    startword = startword.replace("\\n\", '",' ')
                    startword =  startword.strip()
                    if not startword.startswith('/') and not startword.startswith('*') and not startword.startswith('import') and not startword.startswith('System.out') and not startword.startswith('Logger') and not startword.startswith('log.info') and  not startword.startswith('logger')  and  not startword.startswith('//'):
                        startword = startword.split('//')[0]
                        print('*********buggyLines buggyLines***********'+startword)
                        buggyLines = buggyLines + startword+' '
                                               
                        buggyLineNo+=1
                                      
                if l.startswith('+'):
                    startword = l[1:]
                    startword =  startword.strip()
                    if not startword.startswith('/') and not startword.startswith('*') and not startword.startswith('import') and not startword.startswith('System.out') and not startword.startswith('Logger') and not startword.startswith('log.info') and  not startword.startswith('logger') and  not startword.startswith('//'):
                        startword = startword.split('//')[0]
                        startword = startword.replace("\\n', \"+ ",' ')
                        print('*********patchLines patchLines***********'+startword)

                        patchLines = patchLines + startword+' '


            hunkinfo = startLineNo+'[buggy]'+buggyLines+'[patch]'+patchLines+'[buggyLineNo]'+str(buggyLineNo)
            diffList.append(hunkinfo)
    print(str(diffList))
    return diffList


def constructTestSample(bugId, indexId, targetfile, repodir, rootdir,startLineNo,buggyLines,patchLines,totalhunk,bno):   
    origTargetFile=targetfile.replace('\r','').replace('\n','')
    className = targetfile.split('/')[-1]
    className = className.replace('.java','').replace('\r','').replace('\n','')
    targetfile=repodir+bugId+'/'+targetfile
    targetfile = targetfile.split('.java')[0]+'.java'
    targetfile=targetfile.replace('\r','').replace('\n','')
    print('targetfile'+targetfile)
    print('startLineNo=========startLineNo====='+startLineNo)
    print('bugId=========bugId====='+bugId)
    print('buggyLines'+buggyLines)
    cxt=''
    metaInfo=''
    diagnosticMsg = executePerturbation(bugId,repodir,rootdir)
    print(diagnosticMsg)


    cmd = 'timeout 200 java -jar /root/SelfAPR/perturbation_model/target/perturbation-0.0.1-SNAPSHOT-jar-with-dependencies.jar '+targetfile+' test-'+startLineNo
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print(result)
    result = str(result)
    if '[CLASS]' in result:
        metaInfo = result.split('[CLASS]')[-1]
    if 'startline:' in result:
        cxtStart=result.split('startline:')[1]
        cxtStart=cxtStart.split(' ')[0]
    else:
        cxtStart = int(startLineNo)-10
    if 'endline:' in result:
        cxtEnd=result.split('endline:')[1]
        if '\'' in cxtEnd:
            cxtEnd=cxtEnd.split('\'')[0]
        if '\"' in cxtEnd:
            cxtEnd=cxtEnd.split('\"')[0]
    else:
        cxtEnd=int(startLineNo)+10


    print('meta=========meta====='+metaInfo)
    
    if 'startline' in metaInfo:
        metaInfo = metaInfo.split('startline')[0]
        

        
    if (int(cxtEnd) - int(startLineNo))>10:
        cxtEnd = str(int(startLineNo)+10)
    if (int(startLineNo) - int(cxtStart))>10:
        cxtStart = str(int(startLineNo)-10)       
    cxtStart=str(cxtStart)
    cxtEnd=str(cxtEnd)
      
    print('cxtStart=========cxtStart====='+cxtStart)
    print('cxtEnd=========cxtEnd====='+cxtEnd)

    sample=''
    #get context info
    if cxtStart not in '' and cxtEnd not in '':
        with open(targetfile,'r',encoding='latin1') as perturbFile:
            lines = perturbFile.readlines()
            for i in range(0,len(lines)):
                if i > int(cxtStart)-2 and i < int(cxtEnd):
                    l = lines[i]
                    l = l.strip()
                    #remove comments
                    if  l.startswith('/') or l.startswith('*'):
                        l = ' '
                    l = l.replace('  ','').replace('\r','').replace('\n','')
                    l = l.split('// ')[0]
                    if int(bno) > 0:
                        if i == int(startLineNo)-1:
                            l=' [BUGGY] '+l
                        elif i == int(startLineNo)+ int(bno) -1:
                            l= ' [BUGGY] '+l
                    elif int(bno) == 0:
                        if i == int(startLineNo)-1:
                            l=' [BUGGY] [BUGGY] '+l
      
                    cxt+=l+' '

    
    sample+='[BUG] [BUGGY] ' + buggyLines +' '+ diagnosticMsg+' '+' [CONTEXT] ' + cxt + ' [CLASS]  '+ metaInfo

    sample = sample.replace('\r','').replace('\n','').replace('\t','')
    sample = sample.replace('  ',' ')
    print(sample)

    global countindex 
    with open(repodir+'/test.csv','a')  as csvfile:
        filewriter = csv.writer(csvfile, delimiter='\t',  escapechar=' ', 
                                quoting=csv.QUOTE_NONE)               
        filewriter.writerow([str(countindex),'[PATCH] '+patchLines,sample,bugId+'_'+className+'_'+totalhunk+'_'+str(int(indexId)+1),startLineNo,str(bno),origTargetFile])
        countindex+=1


def execute(cmd: str, dir: str):
    print(f"Executing command: {cmd}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return result


def executePerturbation(bugId,repodir,rootdir):
    compile_error_flag = True
    project = bugId.split('_')[0]
    bugNo = bugId.split('_')[1]
    exectresult=''
    program_path=repodir+'/'+bugId
    print('****************'+program_path+'******************')
   
    #get test result
    cmd = "cd " + program_path + ";"
    cmd += "defects4j info -p "+project +"  -b "+bugNo
    result=''
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print(result)
    failingtest = ''
    faildiag = ''
    if 'Root cause in triggering tests:' in str(result):
        result=str(result).split('Root cause in triggering tests:')[1]
    if '--------' in str(result):
        result=str(result).split('--------')[0]
    print(result)
    resultLines = str(result).split('\\')
    for l in resultLines:
        if '-' in l and '::' in l and failingtest  in '':
            failingtest = l.split('-')[1]
            failingtest=failingtest.strip()
        if '-->' in l and faildiag  in '':
            faildiag = l.split('-->')[1]
            if '.' in faildiag:
                faildiag_dots = faildiag.split('.')
                if len(faildiag_dots)>2:
                    faildiag=''
                    for i in range(2,len(faildiag_dots)):
                        faildiag+=faildiag_dots[i]
  
    print('==========failingtest======='+failingtest)
    print('==========faildiag======='+faildiag)

    failingTestMethod=failingtest.split('::')[1]
    exectresult = '[FE] ' + faildiag +' '+failingTestMethod
    os.chdir(rootdir)

    return exectresult



if __name__ == '__main__':

    bug_id = sys.argv[1]
    bug_id = bug_id.replace("-", "_")
    proj, bid = bug_id.split('_')
    repodir = os.path.join(ROOT_DIR, "tmp")
    os.makedirs(repodir, exist_ok=True)
    if os.path.exists(os.path.join(repodir, bug_id)):
        shutil.rmtree(os.path.join(repodir, bug_id))
    execute(f"defects4j checkout -p {proj} -v {bid}b -w {repodir}/{bug_id}", repodir)
    start(bug_id, os.path.join(repodir, bug_id))
    
