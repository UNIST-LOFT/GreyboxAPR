import d4j_tbar
import subprocess
import multiprocessing as mp
import seeds

def run(project):
    print(f'Run {project}-orig')
    result=subprocess.run(['python3','search-tbar-orig.py',project],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    with open(f'result/{project}-orig.log','w') as f:
        f.write(result.stdout.decode("utf-8"))
    print(f'Finish {project}-orig with returncode {result.returncode}')

    for i in range(10):
        print(f'Run {project}-casino-{i}')
        result=subprocess.run(['python3','search-tbar-casino.py',project,str(seeds.SEEDS[i]),str(i)],
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        with open(f'result/{project}-casino-{i}.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
        print(f'Finish {project}-casino-{i} with returncode {result.returncode}')

        print(f'Run {project}-greybox-{i}')
        result=subprocess.run(['python3','search-tbar-greybox.py',project,str(seeds.SEEDS[i]),str(i)],
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        with open(f'result/{project}-greybox-{i}.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
        print(f'Finish {project}-greybox-{i} with returncode {result.returncode}')

        print(f'Run {project}-greyboxfd-{i}')
        result=subprocess.run(['python3','search-tbar-greyboxfd.py',project,str(seeds.SEEDS[i]),str(i)],
                                stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        with open(f'result/{project}-greyboxfd-{i}.log','w') as f:
            f.write(result.stdout.decode("utf-8"))
        print(f'Finish {project}-greyboxfd-{i} with returncode {result.returncode}')

from sys import argv

if len(argv)!=2:
    print(f'Usage: {argv[0]} <num of processes>')
    exit(1)
    
pool=mp.Pool(int(argv[1]))

for i in range(1,d4j_tbar.CLI_SIZE+1):
    if i in d4j_tbar.CLI_SKIP: continue
    pool.apply_async(run,(f'Cli_{i}',))
for i in range(1,d4j_tbar.CODEC_SIZE+1):
    pool.apply_async(run,(f'Codec_{i}',))
for i in range(1,d4j_tbar.COLLECTIONS_SIZE+1):
    if i in d4j_tbar.COLLECTIONS_SKIP: continue
    pool.apply_async(run,(f'Collections_{i}',))
for i in range(1,d4j_tbar.COMPRESS_SIZE+1):
    pool.apply_async(run,(f'Compress_{i}',))
for i in range(1,d4j_tbar.CSV_SIZE+1):
    pool.apply_async(run,(f'Csv_{i}',))
for i in range(1,d4j_tbar.GSON_SIZE+1):
    pool.apply_async(run,(f'Gson_{i}',))
for i in range(1,d4j_tbar.JACKSON_CORE_SIZE+1):
    pool.apply_async(run,(f'JacksonCore_{i}',))
for i in range(1,d4j_tbar.JACKSON_DATABIND_SIZE+1):
    if i in d4j_tbar.JACKSON_DATABIND_SKIP: continue
    pool.apply_async(run,(f'JacksonDatabind_{i}',))
for i in range(1,d4j_tbar.JACKSON_XML_SIZE+1):
    pool.apply_async(run,(f'JacksonXml_{i}',))
for i in range(1,d4j_tbar.JSOUP_SIZE+1):
    pool.apply_async(run,(f'Jsoup_{i}',))
for i in range(1,d4j_tbar.JXPATH_SIZE+1):
    pool.apply_async(run,(f'JxPath_{i}',))
for i in d4j_tbar.CLOSURE_NEW:
    pool.apply_async(run,(f'Closure_{i}',))

pool.close()
pool.join()
