#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 22:25:34 2021

@author: cristianjunge
"""

import numpy as np
from datetime import datetime
import multiprocessing as mp
from multiprocessing import Process
import os

print('oli')
# Prepare data
np.random.RandomState(100)
arr = np.random.randint(0, 10, size=[200000, 5])
data = arr.tolist()
data[:5]


def howmany_within_range(row, minimum, maximum):
    """Returns how many numbers lie within `maximum` and `minimum` in a given `row`"""
    count = 0
    for n in row:
        if minimum <= n <= maximum:
            count = count + 1
    return count

def howmany_within_range_rowonly(row, minimum=4, maximum=8):
    """Returns how many numbers lie within `maximum` and `minimum` in a given `row`"""
    count = 0
    for n in row:
        if minimum <= n <= maximum:
            count = count + 1
    return count



now = datetime.now()



# %% Regular computing

print('---------------- \n REGULAR COMPUTING')

now = datetime.now()

results = []
for row in data:
    results.append(howmany_within_range(row, minimum=4, maximum=8))

print(results[:10])


print('Total Time Reg Computing:',(datetime.now()-now).microseconds/1000,'miliseconds')


# %% Paralell computing

print('---------------- \n PARALELL COMPUTING')

now = datetime.now()
pool = mp.Pool(mp.cpu_count())

# Step 2: `pool.apply` the `howmany_within_range()`

results = pool.starmap(howmany_within_range, [(row, 4, 8) for row in data])

# Step 3: Don't forget to close
pool.close()    



print(results[:10])


print('Total Time Paralell:',(datetime.now()-now).microseconds/1000,'miliseconds')
