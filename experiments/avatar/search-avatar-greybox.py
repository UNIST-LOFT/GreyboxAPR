import os
import sys
import subprocess


def run(project,seed,trial):
    cur_dir=os.getcwd()
    if not cur_dir.endswith('experiments/avatar'):
        print('Please run this script in experiments/avatar',file=sys.stderr)
        sys.exit(1)

    cur_dirs=cur_dir.split('/')
    new_cur_dir=''
    for dir in cur_dirs[:-2]:
        new_cur_dir+=dir+'/'

    print(f"Run {project}-greybox-{trial}")
    result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-greybox-{trial}','-m','greybox',
                           '--seed',f'{seed}','-k','template','-w',f'{new_cur_dir}/Avatar/d4j/{project}','-t','180000','--debug',
                           '--use-simulation-mode',f'result/cache/{project}-cache.json','--instr-cp','../../../JPatchInst',
                           '--branch-output',f'result/branch/{project}','-E','3000','--skip-valid','--optimized-instrumentation',
                           '--','python3',f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/Avatar/buggy'])

    print(f'{project} greybox-{trial} finish with return code {result.returncode}')
    exit(result.returncode)

if __name__ == '__main__':
    args=sys.argv
    if len(args)!=4:
        print('Usage: python3 search-avatar-greybox.py <project> <seed> <trial>')
        sys.exit(1)
    
    run(args[1],args[2],args[3])