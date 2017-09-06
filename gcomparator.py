
class GComparator:
  test_case_splitter = 'Number of dices:'
  special_case = {'result' : [1, 2, 3, 4, 5], 'score' : 150}
  scores_table = { 1 : 10, 5 : 5}

  def __init__(self, tests_output):
    self.test_cases_stdout = []
    self._split_tests_output(tests_output)
    #print('STDOUT =', tests_output)
    #print(self.test_cases_stdout)

  def _split_tests_output(self, tests_output):
    for test_output in tests_output.split(self.test_case_splitter):
      if 'Welcome to' in test_output or not test_output or test_output == '\n':
        continue
      self.test_cases_stdout.append(test_output)

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
    etalon_has_gurgen = False
    etalon_score = 0
    if dices == self.special_case['result']:
      etalon_score = self.special_case['score']
    else:
      tmp_has_gurgen = True
      for dice in dices:
        if dice in self.scores_table.keys(): 
          etalon_score += self.scores_table[dice]
          tmp_has_gurgen = False
      if len(dices) != 0: etalon_has_gurgen = tmp_has_gurgen

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
    for idx, test_case_stdout in enumerate(self.test_cases_stdout):
      test_name = 'TEST #%i' % idx
      score, has_gurgen, dices = self._preprocess(test_case_stdout)
      #print('Score =', score, ', Has GURGEN =', has_gurgen, ', Dices =', dices)
      etalon_score, etalon_gurgen = self._calculate_etalon(dices)
      #print('Etalon Score =', etalon_score, ', Etalon Has GURGEN =', etalon_gurgen)

      self._check( score == etalon_score, 
        '%s FAIL\n  %s\n  %s' % (test_name, self._get_dices_str(dices), 
        self._get_message('score', score, etalon_score)))
      self._check( has_gurgen == etalon_gurgen,
        '%s FAIL\n  %s\n  %s' % (test_name, self._get_dices_str(dices), 
        self._get_message('gurgen', has_gurgen, etalon_gurgen)))

      if score == etalon_score and has_gurgen == etalon_gurgen:
        print('%s OK\n  %s' % (test_name, self._get_dices_str(dices)))


if __name__ == "__main__":
  comprtr = GComparator('Welcome to GURGEN world!\nNumber of dices:dices: 3 \nGURGEN!\nNumber of dices:dices: 4 4 \nGURGEN!\nNumber of dices:dices: 2 2 5 \nscore: 5\nNumber of dices:dices: 6 4 2 5 \nscore: 5\nNumber of dices:dices: 2 5 2 5 5 \nscore: 15\nNumber of dices:\n')
  comprtr.compare()
  
