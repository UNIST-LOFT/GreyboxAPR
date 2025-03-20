from getopt import getopt
import os
import shutil
from sys import argv
import multiprocessing as mp
import d4j
import subprocess


def draw_plot(result:str, mode:str):
    print(f'Drawing {result}')
    res=subprocess.run(['python3','scripts/rq1-single.py',mode,result],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if res.returncode!=0:
        print(f'Error: {result}')

if __name__ == '__main__':
    o,a=getopt(argv[1:],'j:',['with-mockito'])
    for opt,arg in o:
        if opt=='--with-mockito':
            WITH_MOCKITO=True
        elif opt=='-j':
            processes=int(arg)
    
    if os.path.exists('scripts/rq1-single'):
        shutil.rmtree('scripts/rq1-single')
    os.mkdir('scripts/rq1-single')

    pool=mp.Pool(processes)
    for result in d4j.D4J_1_2_LIST:
        pool.apply_async(draw_plot,(result,a[0]))
    
    pool.close()
    pool.join()