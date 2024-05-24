#!/usr/bin/python3
import sys, os, subprocess,fnmatch, shutil, csv, re, datetime

def getDiagnosis(project,bug):
    failingtest = ''
    faildiag = ''
    project_info="defects4j info -p "+ project +" -b " +bug
    project_info="defects4j test"

    result = os.popen(project_info).read()
    if 'Root cause in triggering tests:' in str(result):
        result=str(result).split('Root cause in triggering tests:')[1]
    if 'List of modified sources' in str(result):
        result=str(result).split('List of modified sources')[0]
    
    resultLines = str(result).split('\\')
    for l in resultLines:
        if '-' in l and '::' in l and failingtest  in '':
            failingtest = l.split('::')[1]
            if '-->' in failingtest:
                failingtest = failingtest.split('-->')[0]
            failingtest=failingtest.strip()
            print('failingtest******'+failingtest)

            break
    for l in resultLines:
        if '-->' in l and faildiag in '':
            faildiag = l.split('-->')[1]
            if '-' in faildiag:
                faildiag = faildiag.split('-')[0]
            if ':' in faildiag:
                faildiag = faildiag.split(':')[0]
            if '.' in faildiag:
                faildiag = faildiag.split('.')[-1]
                break
    
    diagnosis = ' [FE] ' + faildiag +' '+failingtest 
    diagnosis = diagnosis.replace("\r","").replace("\n","")
    return diagnosis


def getDiagnosis_fromFL(test_path):
    fail_count=0
    diagnosis=""
    with open(test_path) as testfails:
        lines = testfails.readlines()
        for l in lines:
            if "FAIL" in l:
                fail_count+=1
                if diagnosis in "":
                    failingtest=l.split(",")[0]
                    failingtest=failingtest.split("#")[1]
                    diagnosis=l.split(",")[3]
                    if "at" in diagnosis:
                        diagnosis = diagnosis.split(" at")[0]
                        diagnosis=str(diagnosis)
                        if ":" in diagnosis:
                            diagnosis = diagnosis.split(":")[0]
                        if "." in diagnosis:
                            diagnosis = diagnosis.split(".")[-1]

    diagnosis = ' [FE] ' + diagnosis  
    diagnosis = diagnosis.replace("\r","").replace("\n","")
    return fail_count,diagnosis


    
def getContext(buggy_class,buggy_line,start_no,end_no):
    
    buggycode = ""
    contextcode_replace = ""
    contextcode_add=""
    endbuggyline= 0
    if int(buggy_line) - int(start_no)>10:
        start_no=int(buggy_line)-10
    if int(end_no) - int(buggy_line)>10:
        end_no=int(buggy_line)+10
        
    if not os.path.exists(buggy_class):
        print(f"### ERROR!!! {buggy_class} does not exist! ###")
        return
    with open(buggy_class,'r') as buggyFile:
        lines = buggyFile.readlines()
        for i in range(0,len(lines)):
            if i > int(start_no)-2 and i < int(end_no):
                l = lines[i]
                l = l.strip()
                #remove comments
                if  l.startswith('/') or l.startswith('*'):
                    l = ' '
                l = l.replace('  ','').replace('\r','').replace('\n','')
                l_add = l
                if i == int(buggy_line)-1:
                    if buggycode in "":
                        buggycode=l
                        buggycode=buggycode.strip()
                        buggycode=buggycode.replace("  "," ")
                        if not buggycode.endswith(";") and not buggycode.endswith("{") and not buggycode.endswith("}") :
                            buggycode+=lines[i+1]
                            endbuggyline=1
                            buggycode=buggycode.strip()
                            buggycode=buggycode.replace("  "," ")
                            if not buggycode.endswith(";") and not buggycode.endswith("{") and not buggycode.endswith("}") :
                                buggycode+=lines[i+2]
                                endbuggyline=2
                        
                    l='[BUGGY] '+buggycode + ' [BUGGY] '
                    l_add = '[BUGGY]  [BUGGY] '+buggycode

                
                contextcode_replace+=l+' '
                contextcode_add+=l_add+' '

    
    return buggycode,contextcode_replace,contextcode_add, endbuggyline


if __name__ == '__main__':
    bug_id = sys.argv[1]
    project, bug = bug_id.split('_')
    suspiciousness_threshold = 0.0
    rounds = '0'

    
    FL_file = os.path.join("SuspiciousCodePositions", bug_id, "Ochiai.txt")
    if not os.path.exists(FL_file):
        FL_file = os.path.join("SuspiciousCodePositions", bug_id, "ochiai.txt")
        if not os.path.exists(FL_file):
            print(f"ERROR!!! {FL_file} does not exists")
            sys.exit
    TEST_file = "./projects/"+project+bug+"/build/sfl/txt/tests.csv"
    if not os.path.exists(FL_file):
        print("This path does not exist: " + FL_file)
        sys.exit()
    else:
        bug_representation_path="./repair_iteration/"+project+bug
        os.system(f"rm -rf {bug_representation_path}")
        if not os.path.exists(bug_representation_path):
            os.system("mkdir -p "+bug_representation_path)
        os.system(f"cp {FL_file} {bug_representation_path}/Ochiai.txt")
        os.system("cp "+TEST_file + " "+bug_representation_path)

        failing_test_number, diagnosis = getDiagnosis_fromFL(TEST_file)
        
        print('failing_test_number: '+str(failing_test_number))
        with open(bug_representation_path+'/bugs.csv', 'w') as csvfile:
            csvfile.write('bugid\tpatch\tbuggy\tid\tbuglineNo\tremoveNo\tfilepath\n')
        
        MAX_LOCATIONS = 40
        
        with open(bug_representation_path+'/Ochiai.txt',"r") as fl:
            lines = fl.readlines()
            count=0
            loc = 0
            for line in lines:
                loc += 1
                if loc > MAX_LOCATIONS:
                    break
                line = line.strip()
                if line.startswith('#') or line == "":
                    continue
                count=count+1
                tokens = line.split("@")
                suspiciousness = tokens[2]
                if float(suspiciousness) <= suspiciousness_threshold:
                    break
                buggy_class = tokens[0]
                buggy_class=buggy_class.replace(".","/").replace("$","/")
                buggy_class=buggy_class+".java" 
                buggy_line = tokens[1]
                if os.path.exists("projects/"+project+bug+"/source/"+buggy_class):
                    buggy_class = "projects/"+project+bug+"/source/"+buggy_class
                elif os.path.exists("projects/"+project+bug+"/src/java/"+buggy_class):
                    buggy_class = "projects/"+project+bug+"/src/java/"+buggy_class
                elif os.path.exists("projects/"+project+bug+"/src/main/java/"+buggy_class):
                    buggy_class = "projects/"+project+bug+"/src/main/java/"+buggy_class
                elif os.path.exists("projects/"+project+bug+"/gson/src/main/java/"+buggy_class):
                    buggy_class = "projects/"+project+bug+"/gson/src/main/java/"+buggy_class
                elif os.path.exists("projects/"+project+bug+"/src/"+buggy_class):
                    buggy_class = "projects/"+project+bug+"/src/"+buggy_class
                    
                
                utils_path = "./utils/context.jar "
                try:
                    results = os.popen("java -jar "+utils_path +buggy_class +" test-"+buggy_line).read()
                    results = str(results)
                except:
                    results=' [CLASS] startline:'+ str(int(buggy_line)-5) + ' endline: '+str(int(buggy_line)+5)
                if "[CLASS]" in results and "startline:" in results:
                    results = results.split("[CLASS]")[1]
                    meta = " [CLASS] " + results.split("startline:")[0]
                    if 'NullPointerException' in diagnosis:
                        start_no = buggy_line
                    else:
                        start_no =  results.split("startline:")[1].split("endline:")[0]
                    end_no =  results.split("endline:")[1].replace("\n","").replace("\r","")
                    
                    buggycode,contextcode_replace,contextcode_add,endbuggycode = getContext(buggy_class,buggy_line,start_no,end_no)
                    # endbuggycode=int(buggy_line)+int(endbuggycode)
                    remove_lines = int(endbuggycode)
                    buggycode = buggycode.replace("  "," ")
                    buggycode = buggycode.replace("\t"," ")
                    buggycode = buggycode.replace("\r"," ")
                    buggycode = buggycode.replace("\n"," ")
                    
                    #representation of replace
                    if 'NullPointerException' in diagnosis:
                        sample_replace=f'[BUG] {buggycode} [BUGGY] {buggycode} {diagnosis} [CONTEXT] ' + contextcode_replace + meta.split('[VARIABLES]')[0]
                    else:
                        sample_replace=f'[BUG] {buggycode} [BUGGY] {buggycode} {diagnosis} [CONTEXT] ' + contextcode_replace + meta 
                    sample_replace = sample_replace.replace('\r','').replace('\n','').replace('\t','').replace('  ',' ')
                    patch_code = '[PATCH] ' + buggycode
                    current_id_rep = f"{bug_id}_{count}_{buggy_line}_replace"
                    # sample_replace = str(count)+'\t'+patch_code+'\t'+sample_replace+'\t'+current_id+'\t'+buggy_class+'\t'+suspiciousness+'\t'+buggy_line+'\t'+str(endbuggycode)+'\t'+str(failing_test_number)+'\t'+'replace'+'\t'  
                    sample_replace = f"{count}\t{patch_code}\t{sample_replace}\t{current_id_rep}\t{buggy_line}\t{remove_lines+1}\t{buggy_class}"

                    #representation of add
                    count+=1
                    if 'NullPointerException' in diagnosis:
                        sample_add='[BUG] [BUGGY] ' + diagnosis+ ' [CONTEXT] ' + contextcode_add + meta.split('[VARIABLES]')[0]
                    else:
                        sample_add='[BUG] [BUGGY] ' + diagnosis+ ' [CONTEXT] ' + contextcode_add + meta
                    current_id_add = f"{bug_id}_{count}_{buggy_line}_add"
                    sample_add = sample_add.replace('\r','').replace('\n','').replace('\t','').replace('  ',' ')
                    # sample_add = str(count)+'\t'+patch_code+'\t'+sample_add+'\t'+current_id+'\t'+buggy_class+'\t'+suspiciousness+'\t'+buggy_line+'\t'+str(endbuggycode)+'\t'+str(failing_test_number)+'\t'+'add'+'\t'
                    sample_add = f"{count}\t{patch_code}\t{sample_add}\t{current_id_add}\t{buggy_line}\t0\t{buggy_class}"

                    print(f"done line {count // 2}: {buggy_class} {buggy_line} {suspiciousness}")
                    with open(bug_representation_path+'/bugs.csv','a') as bugrep:
                        bugrep.write(sample_replace+'\n')
                        bugrep.write(sample_add+'\n')
                    with open(bug_representation_path+'/fl.csv','a') as bugrep:
                        source_file = buggy_class.replace(f"projects/{project}{bug}/", "")
                        bugrep.write(f"{current_id_rep}\t{count - 1}\t{loc}\t{remove_lines + 1}\t{source_file}\t{buggy_line}\t{suspiciousness}\treplace\n")
                        bugrep.write(f"{current_id_add}\t{count}\t{loc}\t0\t{source_file}\t{buggy_line}\t{suspiciousness}\tadd\n")

