#!/usr/bin/python3
import os, sys, argparse
from subprocess import Popen, PIPE, STDOUT
from queue import Queue, Empty
from threading import Thread
from gcomparator import GComparator
import time

class TestRunner:
  def __init__(self, application_path):
    self.proc = Popen([application_path], stdin = PIPE, stdout = PIPE, stderr = STDOUT, 
             bufsize=1, close_fds=True)
    self.q = Queue()
    self.version_name = os.path.basename(application_path)

  def __del__(self):
    self.proc.kill()

  def _get_result(self, q, need_wait = True):
    while True:
      try:
        line = q.get_nowait()
      except Empty:
        #print('no output yet')
        if not need_wait:
          return b''
      else:
        #print('in else get_result = ' + line.decode())
        break
    return line

  def _enqueue_output(self, out, q):
    #TODO better to use signals instead of blocking 'readline'
    for line in iter(out.readline, b''):
      #print("gurgen_output=" + line.decode().replace('\n', ''))
      q.put(line)
    out.close()

  def write_data(self, test_data):
    # send test data to tested application
    self.proc.stdin.write(b'%s\n' % test_data.encode())
    self.proc.stdin.flush()
    #time.sleep(2)

  def start_listening_output(self):
    # create thread and queue to gather stdout from tested application
    t = Thread(target=self._enqueue_output, args=(self.proc.stdout, self.q))
    t.daemon = True
    t.start()

  def read_data(self, test_data):
    # gather data from queue
    # number of attemps to get data from queue = number of test cases * 4
    attempts = ((test_data.count('\n') + 3) * 4)
    welcomeLinesCount = 2
    tested_app_stdout = b''
    #print('attempts = ', attempts)
    for i in range(attempts):
      need_wait_stdin = i < welcomeLinesCount and True or False
      #print(need_wait_stdin)
      tested_app_stdout += self._get_result(self.q, need_wait_stdin)
    return tested_app_stdout

  def test_valid_cases(self, test_values_list):
    for test_idx, test_input in enumerate(test_values_list):
      #print('-------------------------------' + test_input)
      self.write_data(test_input)
      output_result = self.read_data(test_input)
      comprtr = GComparator(test_input, output_result.decode(), test_idx, self.version_name)
      score, dices = comprtr.compare_valid_data()
      comprtr.check_for_dices_values(dices, int(test_input))

  def test_invalid_cases(self, invalid_test_values_list, etalon_message):
    for test_idx, test_input in enumerate(invalid_test_values_list):
      self.write_data(test_input)
      output_result = self.read_data(test_input)
      comprtr = GComparator(test_input, output_result.decode(), test_idx, self.version_name)
      comprtr.compare_invalid_data(etalon_message)

#----------------------------------
parser = argparse.ArgumentParser(description='Run set of tests of GURGEN application.', prefix_chars = "/")
parser.add_argument('gurgen_path', help='absolute path to application to test', action = 'store')
parser.add_argument('test_cases_count', help='number of test cases that will generate test inputs (from 0 to intmax)',
                    action = 'store')

if __name__ == "__main__":
  args = parser.parse_args()
  application_path = args.gurgen_path.replace('%', '') #"/home/kar/.../gurgen_6"
  test_cases_count = args.test_cases_count #'5'
  import random
  test_values_list = []
  for i in range(int(test_cases_count)):
    test_values_list.append(str(random.randint(1, 5)))
  print('----------------------------------')
  print("GURGEN TEST %s" % application_path)
  #print('Test values = ', test_values_list)
  print('----------------------------------')
  runner = TestRunner(application_path)
  runner.start_listening_output()
  # Valid input test
  runner.test_valid_cases(test_values_list)
  # Invalid input test
  invalid_dices_count_list = [str(s) for s in [-2147483648, -1, 0, 6, 2147483647]]
  runner.test_invalid_cases(invalid_dices_count_list, "\nnumber of dices error\n")
  invalid_input = [str(s) for s in [-sys.maxsize, -2147483649, 2147483648, sys.maxsize, 'A', 'z', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')[]', '-+=', ':', ';', '/', '\\' ]]
  runner.test_invalid_cases(invalid_input, "\ninput error\n")
