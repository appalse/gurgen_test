#!/usr/bin/python3
from subprocess import Popen, PIPE
import os, time, sys
from queue import Queue, Empty
from threading import Thread

application_name = sys.argv[1] #"gurgen_6"
test_value = sys.argv[2]
print("GURGEN TEST %s. Test value = %s" % (application_name, test_value))

cur_dir = os.getcwd()
#out_log = open(os.path.join(cur_dir, "out.txt"), 'w+')
err_log = open(os.path.join(cur_dir, "err.txt"), 'w+')

proc = Popen([os.path.join(cur_dir, application_name)],\
    stdin = PIPE, stdout = PIPE, stderr = err_log, bufsize=1, close_fds=True)

proc.stdin.write(b'%s\n' % test_value.encode())
proc.stdin.flush()

def enqueue_output(out, queue):
  for line in iter(out.readline, b''):
    #print("enqueue_output=" + line.decode())
    queue.put(line)
  out.close()

q = Queue()
t = Thread(target=enqueue_output, args=(proc.stdout, q))
t.daemon = True
t.start()

def get_result(que, need_wait = True):
  while True:
    try:
      line = que.get_nowait()
    except Empty:
      #print('no output yet')
      if not need_wait:
        return b''
    else:
      #print('in else get_result = ' + line.decode())
      break
  return line

attempts = 5
welcomeLinesCount = 1

test_result = b''

for i in range(attempts):
  need_wait_stdin = i < welcomeLinesCount and True or False
  test_result += get_result(q, need_wait_stdin)
  
print('STDOUT=', test_result)
proc.kill()

def preproceess_data(result_line):
  lines = result_line.split('\n') 
  has_gurgen = False
  score = None
  dices = []
  for line in lines:
    if 'Welcome to' in line:
      continue
    if 'GURGEN!' in line:
      has_gurgen = True
      continue
    if 'score' in line:
      score = int(line[line.index(':')+1 : ]) #ValueError
    if 'dices' in line:
      dices = [int(dice) for dice in line[line.rindex(':')+1 : ].split(' ') if dice]
    # Invalid unknown string
  return score, has_gurgen, dices

score, has_gurgen, dices = preproceess_data(test_result.decode())
print('Score =', score, ', Has GURGEN =', has_gurgen, ', Dices =', dices)

def calculate_score_and_gurgen(dices):
  total = 0
  has_gurgen = False
  if dices == [1, 2, 3, 4, 5]:
    total = 150
  else:  
    for dice in dices:
      if dice == 1: total += 10
      if dice == 5: total += 5
    if not total: has_gurgen = True
  return total, has_gurgen


etalon_score, etalon_gurgen = calculate_score_and_gurgen(dices)
print('Etalon Score =', etalon_score, ', Etalon Has GURGEN =', etalon_gurgen)

if score == etalon_score and has_gurgen == etalon_gurgen:
  print('TEST OK')
else:
  print('TEST FAIL')
