
class GComparator:
  test_case_splitter = 'Number of dices:'
  special_case = {'result' : [1, 2, 3, 4, 5], 'score' : 150}
  scores_table = { 1 : 10, 5 : 5}

  def __init__(self, test_case_stdout, test_idx = 0):
    self.test_output = self._preprocess_test_output(test_case_stdout)
    self.test_index = test_idx
    #print('STDOUT =', test_output)
    #print(self.test_output test_case_stdout)

  def _preprocess_test_output(self, test_case_stdout):
    test_case_stdout_lines = []
    for line in test_case_stdout.split(self.test_case_splitter):
      if 'Welcome to' in line or not line or line == '\n':
        continue
      test_case_stdout_lines.append(line)
    if len(test_case_stdout_lines) != 1:
      raise exception("Invalid stdout: should contain only 1 result of 1 test \
(text begining from 'Number of dices:' before the next 'Number of dices:')")
    return test_case_stdout_lines[0]

  def _preprocess(self, test_case_stdout):
    lines = test_case_stdout.split('\n') 
    score = None; has_gurgen = False; dices = []
    for line in lines:
      if 'GURGEN!' in line:
        has_gurgen = True
        continue
      if 'score' in line:
        score = int(line[line.index(':')+1 : ]) #ValueError can be
      if 'dices:' in line and not "error" in line:
        dices = [int(dice) for dice in line[line.rindex(':')+1 : ].split(' ') if dice]
      # Invalid unknown string
    return score, has_gurgen, dices

  def _calculate_etalon(self, dices):
    sorted_dices = list(dices)
    sorted_dices.sort()
    etalon_has_gurgen = False
    etalon_score = 0
    if sorted_dices == self.special_case['result']:
      etalon_score = self.special_case['score']
    else:
      tmp_has_gurgen = True
      for dice in sorted_dices:
        if dice in self.scores_table.keys(): 
          etalon_score += self.scores_table[dice]
          tmp_has_gurgen = False
      if len(sorted_dices) != 0: etalon_has_gurgen = tmp_has_gurgen

    if etalon_score == 0:
      etalon_score = None
    return etalon_score, etalon_has_gurgen

  def _get_dices_str(self, dices):
    return "tested dices = %s" % str(dices)

  def _get_message(self, name, etalon, real):
    return "%s : %s instead of %s" % (name, str(etalon), str(real))

  def _check(self, ok_condition, error_message):
    if not ok_condition:
      print(error_message)

  def compare(self):
    test_name = 'TEST #%i' % self.test_index
    score, has_gurgen, dices = self._preprocess(self.test_output)
    #print('Score =', score, ', Has GURGEN =', has_gurgen, ', Dices =', dices)
    etalon_score, etalon_gurgen = self._calculate_etalon(dices)
    #print('Etalon Score =', etalon_score, ', Etalon Has GURGEN =', etalon_gurgen)

    self._check( score == etalon_score, 
      '%s FAIL - score\n  %s\n  %s' % (test_name, self._get_dices_str(dices), 
      self._get_message('score', score, etalon_score)))
    self._check( has_gurgen == etalon_gurgen,
      '%s FAIL - gurgen\n  %s\n  %s' % (test_name, self._get_dices_str(dices), 
      self._get_message('gurgen', has_gurgen, etalon_gurgen)))

    #if score == etalon_score and has_gurgen == etalon_gurgen:
    #  print('%s OK\n  %s' % (test_name, self._get_dices_str(dices)))


if __name__ == "__main__":
  comprtr = GComparator('Welcome to GURGEN world!\nNumber of dices:dices: 3 \nGURGEN!', 1)
  comprtr.compare()
  
