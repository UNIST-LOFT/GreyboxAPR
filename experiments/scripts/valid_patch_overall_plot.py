from sys import argv
import matplotlib.pyplot as plt

import valid_patch

if __name__=='__main__':
    if len(argv)<4:
        print(f'Usage: valid_patch_overall_plot.py <result_dir> <max_exp> <algorithms...>')
        exit(1)
    
    result_dir=argv[1]
    max_exp=int(argv[2])
    algorithms=argv[3:]
    
    result=valid_patch.valid_patch_combine(result_dir,max_exp,use_casino=('casino' in algorithms),
                                                use_greybox=('greybox' in algorithms),use_orig=('orig' in algorithms),
                                                use_seapr=('seapr' in algorithms))
    
    sorted_algorithm=[]
    if 'greybox' in algorithms:
        sorted_algorithm.append('greybox')
    if 'casino' in algorithms:
        sorted_algorithm.append('casino')
    if 'seapr' in algorithms:
        sorted_algorithm.append('seapr')
    if 'orig' in algorithms:
        sorted_algorithm.append('orig')
    
    COLORS=['r','g','b','y']
    TIMEOUT=5*60
    plt.clf()
    for algorithm in sorted_algorithm:
        print(f'Algorithm: {algorithm}')
        current_result=sorted(result[algorithm])

        y=[0]
        for i in range(TIMEOUT):
            if i in current_result:
                if algorithm in ('casino','greybox'):
                    y.append(y[-1]+current_result.count(i)/max_exp)
                else:
                    y.append(y[-1]+current_result.count(i))
            else:
                y.append(y[-1])
        
        plt.plot(list(range(TIMEOUT+1)),y,color=COLORS.pop(0),label=algorithm)
    
    plt.legend()
    plt.xlabel('Time (min)')
    plt.ylabel('# of Valid patches')
    plt.savefig(f'valid_patch_overall_plot.png')