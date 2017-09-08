#!/usr/bin/python3
import os, argparse
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
    for line in iter(out.readline, b''):
      #print("gurgen_output=" + line.decode().replace('\n', ''))
      q.put(line)
    out.close()

  def write_data(self, test_data):
    # send test data to tested application
    #self.proc.stdin.open()
    self.proc.stdin.write(b'%s\n' % test_data.encode())
    self.proc.stdin.flush()
    #self.proc.stdin.close()
    #time.sleep(2)

  def start_listening_output(self):
    # create thread and queue to gather stdout from tested application
    t = Thread(target=self._enqueue_output, args=(self.proc.stdout, self.q))
    t.daemon = True
    t.start()

  def read_data(self, test_data):
    # gather data from queue
    # number of attemps to get data from queue = number of test cases * 4
    attempts = ((test_data.count('\n') + 1) * 4)
    welcomeLinesCount = 1
    tested_app_stdout = b''
    #print('attempts = ', attempts)
    for i in range(attempts):
      need_wait_stdin = i < welcomeLinesCount and True or False
      tested_app_stdout += self._get_result(self.q, need_wait_stdin)
    return tested_app_stdout

  def test_output_result(self, output_result, test_index = 0):  
    comprtr = GComparator(output_result.decode(), test_index)
    comprtr.compare()

#----------------------------------
parser = argparse.ArgumentParser(description='Run set of tests of GURGEN application.', prefix_chars = "/")
parser.add_argument('gurgen_path', help='absolute path to application to test', action = 'store')
parser.add_argument('test_data', help='integer numbers for application testing, splitted by "\\n" character',
                    action = 'store')

if __name__ == "__main__":
  args = parser.parse_args()
  application_path = args.gurgen_path.replace('%', '') #"/home/kar/.../gurgen_6"
  test_value = args.test_data #'1\n2\n3\n4\n5'
  import random
  r = []
  for i in range(1000):
    r.append(str(random.randint(1, 5)))
  test_value = '\n'.join(r)
  test_value = test_value.replace("\\n", '\n')
  test_values_list = test_value.split('\n')
  print('----------------------------------')
  print("GURGEN TEST %s" % application_path)
  print('Test values = ', test_values_list)
  print('----------------------------------')
  runner = TestRunner(application_path)
  runner.start_listening_output()
  for test_idx, test_input in enumerate(test_values_list):
    runner.write_data(test_input)
    output_result = runner.read_data(test_input)
    runner.test_output_result(output_result, test_idx)
