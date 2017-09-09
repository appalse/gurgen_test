#!/usr/bin/python3
import os
from subprocess import Popen, PIPE
from queue import Queue, Empty
from threading import Thread
import time

from gcomparator import GComparator

class TestRunner:
  """Run tested aplication, listen to testd app., test with valid and invalid data"""

  # max time to wait for response from tested applicatino
  # because in some cases tested application has no stdout data 
  #   and we are waiting for it on blocking 'readline' method
  max_timeout_in_sec = 5 

  def __init__(self, application_path, log):
    """start tested application and create queue for stdout exchange"""
    self.testlog = log
    self.proc = Popen([application_path], stdin = PIPE, stdout = PIPE, 
             stderr = PIPE, bufsize=1, close_fds=True)
    self.q = Queue()
    self.version_name = os.path.basename(application_path)

  def __del__(self):
    """kill process with tested application"""
    self.proc.kill()

  def start_listening_output(self):
    """ create thread to listen stdout from tested application and send it to queue"""
    t = Thread(target=self._enqueue_output, args=(self.proc.stdout, self.q))
    t.daemon = True
    t.start()

  def _enqueue_output(self, std_out, q):
    """put text from tested application into queue. Blocking readline method is used"""
    # It's better to use signals instead of blocking 'readline' but we cannot because:
    #  - tested application never terminates. We cannot use Popen.communicate. 
    #  - 'select' module in python may be a solution. But it is not fully supported on different OS
    #  - tested application could have no output or several output lines - difficult to capture results
    #  Most reliable way is reading via 'readline' in separate thread and passing to queue.
    for line in iter(std_out.readline, b''):
      self.testlog.write_info("gurgen_output=" + line.decode().replace('\n', ''))
      q.put(line)
    std_out.close()

  def test_valid_cases(self, test_values_list):
    """run tests with valid data and compare result to calculated etalon"""
    self.run(test_values_list, self._valid_data_checker)

  def test_invalid_cases(self, invalid_test_values_list, etalon_message):
    """run tests with invalid data and compare result to etalon error message"""
    self.run(invalid_test_values_list, self._invalid_data_checker, etalon_message)

  def run(self, test_values_list, test_checker, etalon_message=''):
    """run tests in loop for every test value (test case).
       write to tested application stdin and read from its stdout"""
    for test_idx, test_input in enumerate(test_values_list):
      # write 1 line to stdin of tested application
      self._write_data_to_stdin(test_input)

      # wait while tested application starts response and sending text lines
      start_time = time.time()
      while self.q.empty() and ( time.time() - start_time < self.max_timeout_in_sec ):
        self.testlog.write_info('run: no stdout yet')
        time.sleep(0.5)
      # if there is no response from tested app. during <max_timeout_in_sec>
      #   it is error - write it in error log and go to the next test value (test case) 
      if self.q.empty() and ( time.time() - start_time > self.max_timeout_in_sec ):
        self.testlog.write_error(self.version_name + ';TEST #' + str(test_idx) + 
          ' FAIL;;tested input = ' + test_input + ';ERROR - NO STDOUT;Stopped by timeuot;')
        continue
      # wait for tested application, while it finish writing to stdout 
      time.sleep(0.2)
      # read all stdout text lines from tested application
      output_result = b''
      while not self.q.empty():
        output_result += self.q.get()

      # Compare test case results with etalon
      comprtr = GComparator(test_input, output_result.decode(), test_idx, self.version_name, self.testlog)
      test_checker(comprtr, etalon_message)

  def _valid_data_checker(self, comprtr, msg=''):
    """steps to check whether generated test output is correct (with valid data)"""
    score, dices = comprtr.compare_valid_data()
    comprtr.check_for_dices_values(dices)

  def _invalid_data_checker(self, comprtr, etalon_message):
    """steps to check whether generated test output is correct (with invalid data)"""
    comprtr.compare_invalid_data(etalon_message)

  def _write_data_to_stdin(self, test_data):
    """ send test data to tested application via stdin"""
    self.proc.stdin.write(b'%s\n' % test_data.encode())
    self.proc.stdin.flush()

