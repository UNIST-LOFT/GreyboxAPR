import os
import sys
import subprocess


def run(project,seed,trial):
    cur_dir=os.getcwd()
    if not cur_dir.endswith('experiments/selfapr'):
        print('Please run this script in experiments/selfapr',file=sys.stderr)
        sys.exit(1)

    cur_dirs=cur_dir.split('/')
    new_cur_dir=''
    for dir in cur_dirs[:-2]:
        new_cur_dir+=dir+'/'

    print(f"Run {project}-genprog-{trial}")
    result=subprocess.run(['python3',f'{new_cur_dir}/SimAPR/simapr.py','-o',f'result/{project}-genprog-{trial}','-m','genprog',
                           '--seed',f'{seed}','-k','learning','-w',f'{new_cur_dir}/SelfAPR/d4j/{project}','-t','180000',
                           '--use-simulation-mode',f'result/cache/{project}-cache.json','-E','3000','--skip-valid',
                           '--','python3',f'{new_cur_dir}/SimAPR/script/d4j_run_test.py',f'{new_cur_dir}/SelfAPR/buggy'])
    
    print(f'{project} genprog-{trial} finish with return code {result.returncode}')
    exit(result.returncode)

if __name__ == '__main__':
    args=sys.argv
    if len(args)!=4:
        print('Usage: python3 search-selfapr-genprog.py <project> <seed> <trial>')
        sys.exit(1)
    
    run(args[1],args[2],args[3])