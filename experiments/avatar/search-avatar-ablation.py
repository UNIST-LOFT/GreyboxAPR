import os
import sys
import subprocess


def run(project,mode,seed):
    cur_dir=os.getcwd()
    if not cur_dir.endswith('experiments/avatar'):
        print('Please run this script in experiments/avatar',file=sys.stderr)
        sys.exit(1)

    cur_dirs=cur_dir.split('/')
    new_cur_dir=''
    for dir in cur_dirs[:-2]:
        new_cur_dir+=dir+'/'

    if mode=='vertical':
        print(f"Run {project}-w/o-vertical")
        result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-wo-vertical','-m','guided','--seed',f'{seed}',
                    '--tbar-mode','-w',f'{new_cur_dir}/Avatar/d4j/{project}','-t','180000','--use-simulation-mode',f'result/cache/{project}-cache.json',
                    '-T','18000','--not-use-guide', '--','python3',
                    f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/Avatar/buggy'])
    elif mode=='horizontal':
        print(f"Run {project}-w/o-horizontal")
        result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-wo-horizontal','-m','guided','--seed',f'{seed}',
                    '--tbar-mode','-w',f'{new_cur_dir}/Avatar/d4j/{project}','-t','180000','--use-simulation-mode',f'result/cache/{project}-cache.json',
                    '-T','18000','--not-use-epsilon', '--','python3',
                    f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/Avatar/buggy'])
    print(f'{project} ablation finish with return code {result.returncode}')
    exit(result.returncode)

if __name__ == '__main__':
    args=sys.argv
    if len(args)!=4:
        print('Usage: python3 search-avatar-ablation.py <project> <vertical|horizontal> <seed>')
        sys.exit(1)
    
    run(args[1],args[2],args[3])