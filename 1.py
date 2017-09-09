#!/usr/bin/python3

import os, sys, argparse
from queue import Queue, Empty
from threading import Thread
import time 
from subprocess import Popen, PIPE
"""
p = Popen(["/home/kar/Documents/VisionLabs/QA/gurgen_5"], stdin = PIPE, stdout = PIPE, stderr = PIPE, 
             bufsize=1, close_fds=True)
sys.stdin.flush()
sys.stdout.flush()
print("after Popen")
try:
  std_out = p.communicate(input = b'5\n', timeout = 10)[0]
  sys.stdin.flush() 
  sys.stdout.flush()
  print("after communicate")
  print(std_out)
except TimeoutExpired:
  proc.kill()
  print("TimeoutExpired")
"""
def write_from_gurgen_to_queue(q):
  for i in ['score: 5', 'GURGEN!', 'score: 10', 'score: 20']:
    q.put(str(i))
    #print("WRITE 1=", str(i))
  time.sleep(3)
  for i in ['GURGEN!', 'score: 20']:
    q.put(str(i))
    #print("WRITE 2=", str(i))
  time.sleep(3)
  for i in ['GURGEN!', 'score: 20']:
    q.put(str(i))
    #print("WRITE 3=", str(i))
  time.sleep(10)
  for i in ['score: 5', 'GURGEN!', 'score: 10', 'score: 20']:
    q.put(str(i))
  time.sleep(2)

q = Queue()
t = Thread(target=write_from_gurgen_to_queue, args=(q, ))
t.daemon = True
t.start()

max_timeout_in_sec = 5

while True:
  start_time = time.time()
  while q.empty() and ( time.time() - start_time < max_timeout_in_sec ):
    print('no input yet')
    time.sleep(1)
  if q.empty() and ( time.time() - start_time > max_timeout_in_sec ):
    print('ERROR - NO STDOUT. Stopped by timeuot')
    continue
  time.sleep(0.2)
  while not q.empty():
    line = q.get()
    print("    READ=", line)

t.join()
t2.join()
print('END')
