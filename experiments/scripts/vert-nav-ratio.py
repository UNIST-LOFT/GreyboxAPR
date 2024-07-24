from getopt import getopt
from os import path
from sys import argv
from typing import Dict, List
import json

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn

import d4j

MAX_EXP=10
WITH_MOCKITO=False
MAX_ITERATION=3000

def plot_patches_ci_java(mode='tbar'):
    # Greybox
    first_nav_count=0
    second_nav_count=0
    for i in range(MAX_EXP):
        for result in d4j.D4J_1_2_LIST:
            if not path.exists(f'{mode}/result/{result}-greybox-{MAX_EXP-1}/simapr-finished.txt'):
                # Skip if experiment not end
                continue
            if not WITH_MOCKITO and 'Mockito' in result:
                continue
            try:
                result_file=open(f'{mode}/result/{result}-greybox-{i}/simapr-search.log','r')
            except:
                continue

            for line in result_file:
                if 'during second vertical search.' in line:
                    second_nav_count+=1
                elif 'Try basic patch with' in line:
                    first_nav_count+=1

            result_file.close()

    print(f'First navigation: {first_nav_count}')
    print(f'Second navigation: {second_nav_count}')

o,a=getopt(argv[1:],'',['with-mockito'])
for opt,arg in o:
    if o=='--with-mockito':
        WITH_MOCKITO=True

plot_patches_ci_java(a[0])