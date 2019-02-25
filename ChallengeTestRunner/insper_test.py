#!/usr/bin/env python

import argparse
from challenge_test_lib import challenge_test as ch


parser = argparse.ArgumentParser()
parser.add_argument('target_filename', help='Name of the target file that contains code to be tested')
parser.add_argument('test_filename', help='Name of the test file')
parser.add_argument('-f', '--function_name', help='Name of the function to be tested', default=None)
parser.add_argument("-v", "--verbose", help="Increase output verbosity", action="store_true")
args = parser.parse_args()


def load_code(filename):
    code = None
    try:
        with open(filename) as f:
            code = f.read()
    except FileNotFoundError:
        print('File {} not found'.format(filename))
    return code



target_code = load_code(args.target_filename)
test_code = load_code(args.test_filename)

result = None
if target_code is not None and test_code is not None:
    result = ch.run_tests(target_code, test_code, args.function_name)

if result:
    if result.success:
        print('Passed all tests!')
    else:
        print('Did not pass all tests :(')
        print('Failure messages:')
        for msg in result.failure_msgs:
            print(msg)
        if args.verbose:
            print('\nStack traces:')
            for st in result.stack_traces:
                print(st)
        print()
else:
    print('Cannot run tests')
