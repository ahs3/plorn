
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os
import sys

from termcolor import colored

cumulative = open('test_stats', 'r')

class_results = {}
raw_data = ''

with open('test_stats', 'r') as fd:
    raw_data = fd.read()

for ii in raw_data.split('\n'):
    if len(ii) < 1:
        break

    data = ii.split('\t')
    if len(data) == 4:
        testclass = data[0]
        count = data[1]
        errs  = data[2]
        fails = data[3]
        if testclass not in class_results:
            class_results[testclass] = [count, errs, fails]
    else:
        print('? bad data in test_stats:')
        print('   ' + ii)

total_count = 0
total_errs  = 0
total_fails = 0
for ii in sorted(class_results.keys()):
    c, e, f = class_results[ii]
    total_count += int(c)
    total_errs  += int(e)
    total_fails += int(f)


res = ''
res += colored('For All Tests:\n', 'yellow')
res += '   ' + colored(f'Classes:    ', 'yellow')
res += str(len(class_results)) + '\n'
res += '   ' + colored(f'Test Cases: ', 'yellow')
res += str(total_count) + '\n'
res += '   ' + colored(f'Passed:     ', 'yellow')
res += str(total_count - total_errs - total_fails) + '\n'
res += '   ' + colored(f'Errors:     ', 'yellow')
res += str(total_errs) + '\n'
res += '   ' + colored(f'Failed:     ', 'yellow')
res += str(total_fails)
print(res, file=sys.stdout)

