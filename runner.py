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

  def run_tested_app(self, test_data):
    # send test data to tested application
    self.proc.stdin.write(b'%s\n' % test_data.encode())
    self.proc.stdin.flush()
    #time.sleep(2)
    # create thread and queue to gather stdout from tested application
    self.q = Queue()
    t = Thread(target=self._enqueue_output, args=(self.proc.stdout, self.q))
    t.daemon = True
    t.start()

  def test_output_result(self, test_data):
    # gather data from queue
    # number of attemps to get data from queue = number of test cases * 3
    attempts = ((test_data.count('\n') + 1) * 3)
    welcomeLinesCount = 1
    tested_app_stdout = b''
    #print('attempts = ', attempts)

    for i in range(attempts):
      need_wait_stdin = i < welcomeLinesCount and True or False
      tested_app_stdout += self._get_result(self.q, need_wait_stdin)
  
    comprtr = GComparator(tested_app_stdout.decode())
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
  #import random
  #r = []
  #for i in range(1000):
  #  r.append(str(random.randint(1, 5)))
  #test_value = '\n'.join(r)
  print('----------------------------------')
  print("GURGEN TEST %s. Test value = %s" % (application_path, test_value))
  print('----------------------------------')
  test_value = test_value.replace("\\n", '\n')
  runner = TestRunner(application_path)
  runner.run_tested_app(test_value)
  runner.test_output_result(test_value)
