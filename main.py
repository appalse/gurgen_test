#!/usr/bin/python3
import random
import argparse
import sys

from test_logger import TestLogger
from runner import TestRunner 

def main(application_path, test_cases_count, log):
  """generate random input values, run tests"""
  log.write_info('----------------------------------')
  log.write_info("GURGEN TEST %s" % application_path)
  log.write_info('----------------------------------')

  test_values_list = [str(random.randint(1, 5)) for i in range(test_cases_count)]
  log.write_info('Test values = %s' % test_values_list)
  log.write_info('----------------------------------')

  runner = TestRunner(application_path, log)
  runner.start_listening_output()

  # Valid input test
  runner.test_valid_cases(test_values_list)

  # Invalid input test (incorrect number of dices)
  invalid_dices_count_list = [str(s) for s in [-2147483648, -1, 0, 6, 2147483647]]
  runner.test_invalid_cases(invalid_dices_count_list, "\nnumber of dices error\n")

  # Invalid input test (invalid number of dices)
  invalid_input = [str(s) for s in [-sys.maxsize, -2147483649, 2147483648, sys.maxsize, 
    'A', 'z', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')[]', '-+=', ':', ';', '/', '\\' ]]
  runner.test_invalid_cases(invalid_input, "\ninput error\n")

#----------------------------------
parser = argparse.ArgumentParser(description='Run tests of GURGEN application.')
parser.add_argument('gurgen_path', help='absolute path to application to test. Put "%" before and after path if some parsing error occurs, e.g. "%/home/user/Documents/gurgen_0%" ', action = 'store')
parser.add_argument('test_cases_count', help='number of test cases that will generate test inputs (should be from 0 to intmax). 1000 cases is about 3 minutes duration', action = 'store')
parser.add_argument('info_log_path', default = 'test_info.txt', help='path to text file with general info about run tests', action = 'store')
parser.add_argument('error_log_path', default = 'test_errors.txt', help='path to text file with errors and failed tests', action = 'store')

if __name__ == "__main__":
  args = parser.parse_args()
  application_path = args.gurgen_path.replace('%', '') # "%/home/kar/.../gurgen_6%"
  test_cases_count = int(args.test_cases_count) # 5
  log = TestLogger(args.info_log_path, args.error_log_path)
  main(application_path, test_cases_count, log)
  
