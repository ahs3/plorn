#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os
import sys
import unittest

from termcolor import colored

sys.stderr = open(os.devnull, 'w')

cumulative = open('test_stats', 'a+')

_testclass = ''
_count = 0
_errs  = 0
_fails = 0

def start(cls):
    global _testclass, _count, _errs, _fails

    print(colored(cls.__name__, 'yellow'), file=sys.stdout)
    if _testclass == '':
        _testclass = cls.__name__
    _count = 0
    _errs  = 0
    _fails = 0

def stop(cls):
    global _testclass, _count, _errs, _fails

    res = '\n'
    res += colored('Test Summary: ', 'yellow')
    res += colored(_testclass + '\n', 'cyan')
    res += '   ' + colored(f'Passed: ', 'yellow')
    res += str(_count - _errs - _fails) + '\n'
    res += '   ' + colored(f'Errors: ', 'yellow')
    res += str(_errs) + '\n'
    res += '   ' + colored(f'Failed: ', 'yellow')
    res += str(_fails) + '\n'
    res += '   ' + colored(f'Total:  ', 'yellow')
    res += str(_count)
    print(res + '\n', file=sys.stdout)

    res = f'{_testclass}\t{_count}\t{_errs}\t{_fails}'
    print(res, file=cumulative)

def get_test_name(utest):
    return utest.id().split('.')[-1]

def fmt_msg(text):
    msg = ''
    \
             for ii in text.split('\n'):
        msg += '      ' + ii + '\n'
    return colored(msg[0:len(msg)-1], 'cyan')

def echo_result(utest):
    global _count, _errs, _fails

    # python > 3.10
    res = utest._outcome.result
    ok = all(tst.id() != utest.id() \
             for tst, txt in ((res.errors) + (res.failures)))

    _count += 1
    if ok:
        print(colored('    OK', 'green'), file=sys.stdout, end='')
        print('...' + get_test_name(utest), file=sys.stdout)
    else:
        if len(res.errors) > 0:
            for tst, msg in res.errors:
                if tst.id() == utest.id():
                    out = colored('    ERROR => ', 'red') + get_test_name(utest)
                    print(out, file=sys.stdout)
                    print(fmt_msg(msg), file=sys.stdout)
                    _errs += 1
        if len(res.failures) > 0:
            for tst, msg in res.failures:
                if tst.id() == utest.id():
                    out = colored('    FAIL => ', 'red') + get_test_name(utest)
                    print(out, file=sys.stdout)
                    print(fmt_msg(msg), file=sys.stdout)
                    _fails += 1

