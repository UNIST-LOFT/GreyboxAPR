import os
import subprocess
import shutil
import sys
from typing import List, Union, Tuple
import psutil
import xml.etree.ElementTree as ET

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
  
  # D4J 2.0
  elif project_name=='Cli':
    if 30 <= bug_id <= 40:
      return '/src/main/java/','/src/test/java/'
    else:
      return '/src/java/','/src/test/'
  elif project_name=='Codec':
    if bug_id <= 10:
      return '/src/java/','/src/test/'
    else:
      return '/src/main/java/','/src/test/java/'
  elif project_name=='Collections':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='Compress':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='Csv':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='Gson':
    return '/gosn/src/main/java/','/gson/src/test/java/'
  elif project_name=='JacksonCore':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='JacksonDatabind':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='JacksonXml':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='Jsoup':
    return '/src/main/java/','/src/test/java/'
  elif project_name=='JxPath':
    return '/src/java/','/src/test/'
  else:
    raise Exception("Unknown project: "+project_name)

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
  
  # D4J 2.0
  elif project_name == "Cli":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "Codec":
    if bug_id <=16:
      return "/target/classes/", "/target/tests/"
    return "/target/classes/", "/target/test-classes/"
  elif project_name == "Collections":
    return '/target/classes/', '/target/tests/'
  elif project_name == "Compress":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "Csv":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "Gson":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "JacksonCore":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "JacksonDatabind":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "JacksonXml":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "Jsoup":
    return '/target/classes/', '/target/test-classes/'
  elif project_name == "JxPath":
    return '/target/classes/', '/target/test-classes/'
  raise Exception("Unknown project: "+project_name)

def get_classpath(work_dir, buggy_project):
  # Todo for all defects4j projects
  classpath, _ = get_target_paths(buggy_project)
  return work_dir + classpath

def get_test_classpath(work_dir, buggy_project):
  # Todo for all defects4j projects
  _, test_classpath = get_target_paths(buggy_project)
  return work_dir + test_classpath

def copyfile(original, target):
  shutil.copyfile(original, target)

def createTempLocation(temp_location):
  os.makedirs(os.path.dirname(temp_location), exist_ok=True)

def deleteTempLocation(temp_location):
  os.remove(temp_location)

def deleteDirectory(dir):
  if os.path.exists(dir):
    shutil.rmtree(dir)

def instrument_patched_project(work_dir:str,buggy_project:str,buggy_path:str):
  instrumenter_root=os.environ['GREYBOX_INSTR_ROOT']
  if 'GREYBOX_TARGET_BRANCHES' not in os.environ:
    specified_branch_ids=''
  else:
    specified_branch_ids=os.environ["GREYBOX_TARGET_BRANCHES"]
  classpath=f'{instrumenter_root}/build/libs/JPatchInst.jar'

  src_path=work_dir+get_target_paths(buggy_project)[0]
  orig_src_path=work_dir+'b'+get_target_paths(buggy_project)[0]
  
  cmd=['java','-Xmx100G','-jar',classpath]
  if specified_branch_ids!='':
    cmd+=['-i',specified_branch_ids]
  cmd+=[orig_src_path,src_path]

  instrumentation_result=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  if instrumentation_result.returncode!=0:
    print(instrumentation_result.stdout.decode('utf-8'),file=sys.stderr)
    return False

  return True
  
def compile_project_updated(work_dir, buggy_project):
  if buggy_project.startswith('Mockito'):
    # Mockito should use modified project structure by Ali Ghanbari
    compile_proc = subprocess.Popen(["mvn", "install", '-DskipTests'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=work_dir)
  else:
    compile_proc = subprocess.Popen(["defects4j", "compile", "-w", work_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  result = True
  so = "".encode()
  se = "".encode()
  if "SIMAPR_TIMEOUT" in os.environ:
    timeout = int(os.environ["SIMAPR_TIMEOUT"])
    try:
      so, se = compile_proc.communicate(timeout=timeout/1000)
    except:
      pid=compile_proc.pid
      children=[]
      for child in psutil.Process(pid).children(False):
        if psutil.pid_exists(child.pid):
          children.append(child)

      for child in children:
        child.kill()
      compile_proc.kill()
      result = False
  else:
    so, se = compile_proc.communicate()
  result_str = so.decode('utf-8').strip()
  err_str = se.decode('utf-8').strip()
  print(err_str, file=sys.stderr)
  if "FAIL" in err_str:
    result = False
  return result

def run_single_test(work_dir: str, buggy_project: str, test: str = "") -> Tuple[int, List[str]]:
  if buggy_project.startswith('Mockito'):
    # Mockito should use modified project structure by Ali Ghanbari
    cmd=['mvn','test']
    if test!='':
      _test=test.split('.')[-1].replace('::','#')
      cmd+=['-Dtest='+_test]
    test_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=work_dir)
  else:
    cmd = ["defects4j", "test", "-w", work_dir]
    if test != "":
      cmd = ["defects4j", "test", "-w", work_dir, "-t", test]
    test_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  so = "".encode()
  se = "".encode()
  if "SIMAPR_TIMEOUT" in os.environ:
    timeout = int(os.environ["SIMAPR_TIMEOUT"])
    if test == "":
      timeout *= 3
    try:
      so, se = test_proc.communicate(timeout=timeout/1000)
    except:
      pid=test_proc.pid
      children=[]
      for child in psutil.Process(pid).children(False):
        if psutil.pid_exists(child.pid):
          children.append(child)

      for child in children:
        child.kill()
      test_proc.kill()
  else:
    so, se = test_proc.communicate()
  result_str = so.decode('utf-8').strip()
  err_str = se.decode('utf-8').strip()
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
      if test!='':
        cur_tests.append(test.split('::')[0])
      else:
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

def test_project(patch_location: str, buggy_location: str, work_dir: str, test: str, buggy_project: str, class_file: str = "", run_original: bool = False):
  print(f"Testing {test} with {patch_location} at {buggy_location}", file=sys.stderr)
  if run_original:
    test_original_project(work_dir, test, buggy_project)
  else:
    test_patched_project(patch_location, buggy_location, work_dir, test, buggy_project, class_file)

def test_patched_project(patch_location: str, buggy_location: str, work_dir: str, test: str, buggy_project: str, class_file: str):
  buggy_file = buggy_location[buggy_location.rindex("/") + 1:]
  temp_location = os.path.join(work_dir, "tmp", buggy_file)
  createTempLocation(temp_location)
  copyfile(buggy_location, temp_location)
  copyfile(patch_location, buggy_location)

  if os.path.exists(class_file):
    os.remove(class_file)
  else:
    deleteDirectory(get_classpath(work_dir, buggy_project))
    deleteDirectory(get_test_classpath(work_dir, buggy_project))
  try:
    if os.environ['GREYBOX_BRANCH']=='1':
      # Copy GlobalStates to source directory
      # We copy the GlobalStates before the instrumentation is success for the later patches
      src_path=work_dir+get_src_paths(buggy_project)[0]
      shutil.copytree(f'{os.environ["GREYBOX_INSTR_ROOT"]}/src/main/resources/kr',src_path+'/kr',dirs_exist_ok=True)
      # if not os.path.exists(src_path+'/kr'):
      #   os.makedirs(src_path+'/kr')
      # if not os.path.exists(src_path+'/kr/ac'):
      #   os.makedirs(src_path+'/kr/ac')
      # if not os.path.exists(src_path+'/kr/ac/unist'):
      #   os.makedirs(src_path+'/kr/ac/unist')
      # if not os.path.exists(src_path+'/kr/ac/unist/apr'):
      #   os.makedirs(src_path+'/kr/ac/unist/apr')
      # if not os.path.exists(src_path+'/kr/ac/unist/apr/GlobalStates.java'):
      #   copyfile(f'{os.environ["GREYBOX_INSTR_ROOT"]}/src/main/resources/kr/ac/unist/apr/GlobalStates.java',src_path+'/kr/ac/unist/apr/GlobalStates.java')

    if not compile_project_updated(work_dir, buggy_project):
      print("FAIL")
      print("---COMPILATION_FAILED")
      raise ValueError("Patch is not compiled")
    
    if os.environ['GREYBOX_BRANCH']=='1':
      instr_result=instrument_patched_project(work_dir, buggy_project, buggy_location)
      if not instr_result:
        print("FAIL")
        print("---INSTRUMENTATION_FAILED")
        raise ValueError("Patch is not instrumented")
      # if not compile_project_updated(work_dir, buggy_project):
      #   print("FAIL")
      #   print("---COMPILATION_FAILED")
      #   raise ValueError("Patch is not compiled after instrumentation")
      
      
    error_num, failed_test = run_single_test(work_dir, buggy_project, test)
    if error_num != 0:
      print("FAIL")
      for ft in failed_test:
        print(f"---{ft}")
    else:
      print("PASS")
  except Exception as e:
    print(e, file=sys.stderr)
    print("Patch is not applied", file=sys.stderr)
  finally:
    copyfile(temp_location, buggy_location)
    deleteTempLocation(temp_location)

def test_original_project(work_dir: str, test: Union[str, List[str]], buggy_project: str):

  deleteDirectory(get_classpath(work_dir, buggy_project))
  try:
    if os.environ['GREYBOX_BRANCH']=='1':
      # Copy GlobalStates to source directory
      # We copy the GlobalStates before the instrumentation is success for the later patches
      src_path=work_dir+get_src_paths(buggy_project)[0]
      shutil.copytree(f'{os.environ["GREYBOX_INSTR_ROOT"]}/src/main/resources/kr',src_path+'/kr',dirs_exist_ok=True)
      # if not os.path.exists(src_path+'/kr'):
      #   os.makedirs(src_path+'/kr')
      # if not os.path.exists(src_path+'/kr/ac'):
      #   os.makedirs(src_path+'/kr/ac')
      # if not os.path.exists(src_path+'/kr/ac/unist'):
      #   os.makedirs(src_path+'/kr/ac/unist')
      # if not os.path.exists(src_path+'/kr/ac/unist/apr'):
      #   os.makedirs(src_path+'/kr/ac/unist/apr')
      # if not os.path.exists(src_path+'/kr/ac/unist/apr/GlobalStates.java'):
      #   copyfile(f'{os.environ["GREYBOX_INSTR_ROOT"]}/src/main/resources/kr/ac/unist/apr/GlobalStates.java',src_path+'/kr/ac/unist/apr/GlobalStates.java')
        
    if not compile_project_updated(work_dir, buggy_project):
      raise ValueError("Original is not compilable")
    
    if os.environ['GREYBOX_BRANCH']=='1':
      instr_result=instrument_patched_project(work_dir, buggy_project, None)
      if instr_result:
        new_compile_result= compile_project_updated(work_dir, buggy_project)

    error_num, failed_test = run_single_test(work_dir, buggy_project, test)
    if error_num != 0:
      print("FAIL")
      for ft in failed_test:
        print(f"---{ft}")
    else:
      print("PASS")
  except Exception as e:
    print(e, file=sys.stderr)

def main(argv: List[str]) -> None:
  root_path = argv[1]
  buggy_project = os.environ["SIMAPR_BUGGY_PROJECT"]
  sep = "_"
  proj, pid = buggy_project.split(sep)
  buggy_dir = os.path.join(root_path, buggy_project)
  patch_location = os.environ["SIMAPR_LOCATION"]
  d4j_dir = os.environ["SIMAPR_WORKDIR"]
  run_original = patch_location == "original"
  patch_location = d4j_dir + os.path.sep + patch_location #os.path.join(d4j_dir, patch_location)
  buggy_location = os.environ["SIMAPR_BUGGY_LOCATION"]
  if buggy_location.startswith("buggy"):
    buggy_location = os.path.join(root_path, buggy_location)
  else:
    buggy_location = os.path.join(buggy_dir, buggy_location)
  class_file = ""
  if "SIMAPR_CLASS_NAME" in os.environ:
    class_file = os.environ["SIMAPR_CLASS_NAME"]
    class_file = os.path.join(buggy_dir, class_file)
  if not os.path.exists(buggy_location): # when original
    os.system(f"rm -rf {buggy_dir}")
    os.makedirs(buggy_dir, exist_ok=True)
    os.system(f"rm -rf {buggy_dir}b")
    os.makedirs(f'{buggy_dir}b', exist_ok=True)
    if len(pid)>=4:
      pid=pid[:-3]
    
    if buggy_project.startswith('Mockito'):
      version=buggy_project.split('_')[1]
      parent_dir='/'.join(buggy_dir.split('/')[:-1])
      pom_path='/'.join(__file__.split('/')[:-2])+f'/mockito/{version}-pom.xml'
      subprocess.run(['wget',f'https://github.com/ali-ghanbari/d4j-mockito/raw/master/Mockito-{version}.tar.gz'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=parent_dir)
      subprocess.run(['tar','-xf',f'Mockito-{version}.tar.gz'],stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=parent_dir)
      _temp=subprocess.run(f'cp -rf {version}/* {buggy_dir}',stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=parent_dir,shell=True)
      _temp=subprocess.run(f'cp -f {pom_path} {buggy_dir}/pom.xml',stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=parent_dir,shell=True)
      _temp=subprocess.run(f'mv {version}/* {buggy_dir}b',stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=parent_dir,shell=True)
      _temp=subprocess.run(f'cp -f {pom_path} {buggy_dir}b/pom.xml',stdout=subprocess.PIPE, stderr=subprocess.PIPE,cwd=parent_dir,shell=True)
      os.remove(f'{parent_dir}/Mockito-{version}.tar.gz')
      shutil.rmtree(f'{parent_dir}/{version}')
    else:
      _temp=subprocess.run(f"defects4j checkout -p {proj} -v {pid}b -w {buggy_dir}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
      subprocess.run(f"defects4j checkout -p {proj} -v {pid}b -w {buggy_dir}b", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    if not compile_project_updated(f'{buggy_dir}b', buggy_project):
      print("FAIL")
      print("---COMPILATION_FAILED")
      raise ValueError("Original is not compiled")
    
  workdir = buggy_dir
  test = os.environ["SIMAPR_TEST"]
  if test == "ALL":
    test = ""
  test_project(
    patch_location=patch_location, 
    buggy_location=buggy_location, 
    work_dir=workdir, 
    test=test, 
    buggy_project=buggy_project, 
    class_file=class_file, 
    run_original=run_original)

if __name__ == "__main__":
  # simple_test()
  main(sys.argv)