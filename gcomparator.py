
class GComparator:
  test_case_splitter = 'Number of dices:'
  special_case = {'result' : [1, 2, 3, 4, 5], 'score' : 150}
  scores_table = { 1 : 10, 5 : 5}

  def __init__(self, test_input, test_case_stdout, test_idx = 0, version_name = ''):
    self.test_name = 'TEST #%i' % test_idx
    self.version = version_name
    self.test_output = self._preprocess_test_output(test_case_stdout)
    #print(self.test_output)

  def _preprocess_test_output(self, test_case_stdout):
    test_case_stdout_lines = []
    for line in test_case_stdout.split(self.test_case_splitter):
      if 'Welcome to' in line or not line or line == '\n':
        continue
      test_case_stdout_lines.append(line)
    if len(test_case_stdout_lines) != 1:
      raise Exception("Invalid stdout: should contain only 1 result of 1 test (text begining from 'Number of dices:' before the next 'Number of dices:') = " + test_case_stdout + self.test_name)
    return test_case_stdout_lines[0]

  def _preprocess(self, test_case_stdout):
    lines = test_case_stdout.split('\n') 
    score = None; has_gurgen = False; dices = []
    for line in lines:
      if 'GURGEN!' in line:
        has_gurgen = True
        continue
      if 'score' in line:
        #TODO: catch ValueError 
        score = int(line[line.index(':')+1 : ])
      if 'dices:' in line and not "error" in line:
        #TODO: catch ValueError 
        dices = [int(dice) for dice in line[line.rindex(':')+1 : ].split(' ') if dice]
      # Invalid unknown string
    return score, has_gurgen, dices

  def _calculate_etalon(self, dices):
    self.sorted_dices = list(dices)
    self.sorted_dices.sort()
    etalon_has_gurgen = False
    etalon_score = 0
    if self.sorted_dices == self.special_case['result']:
      etalon_score = self.special_case['score']
    else:
      tmp_has_gurgen = True
      for dice in self.sorted_dices:
        if dice in self.scores_table.keys(): 
          etalon_score += self.scores_table[dice]
          tmp_has_gurgen = False
      if len(self.sorted_dices) != 0: etalon_has_gurgen = tmp_has_gurgen

    if etalon_score == 0:
      etalon_score = None
    return etalon_score, etalon_has_gurgen

  def _get_dices_str(self, dices):
    if self.sorted_dices:
      return "tested dices = %s" % str(self.sorted_dices)
    else:
      return "tested dices = %s" % str(dices)

  def _get_message(self, name, real, etalon):
    return "%s : %s instead of %s" % (name, str(real), str(etalon))

  def _check(self, ok_condition, error_message):
    if not ok_condition:
      print(error_message)
      #with open("errors.txt", 'a') as f:
      #  f.write(self.version + ';' + 
      #    error_message.replace('\n', ';').replace(' - ', ';').replace('  ', '') + ';STDOUT=' + 
      #    self.test_output.replace('\n', '   ') + '\n')

  def compare_valid_data(self):    
    score, has_gurgen, dices = self._preprocess(self.test_output)
    #print('Score =', score, ', Has GURGEN =', has_gurgen, ', Dices =', dices)
    etalon_score, etalon_gurgen = self._calculate_etalon(dices)
    #print('Etalon Score =', etalon_score, ', Etalon Has GURGEN =', etalon_gurgen)

    self._check( score == etalon_score, 
      '%s FAIL - score\n  %s\n  %s' % (self.test_name, self._get_dices_str(dices), 
      self._get_message('score', score, etalon_score)))
    self._check( has_gurgen == etalon_gurgen,
      '%s FAIL - gurgen\n  %s\n  %s' % (self.test_name, self._get_dices_str(dices), 
      self._get_message('gurgen', has_gurgen, etalon_gurgen)))

    if score == etalon_score and has_gurgen == etalon_gurgen:
      print('%s OK\n  %s' % (self.test_name, self._get_dices_str(dices)))
    return score, dices

  def compare_invalid_data(self, etalon_message):
    self._check( self.test_output == etalon_message, 
      '%s FAIL - invalid output message\n  %s' % (self.test_name, 
      self._get_message('invalid output', self.test_output, etalon_message)))

  def check_for_dices_values(self, dices, input_dices_count):
    self._check( input_dices_count == len(dices), 
      '%s FAIL - dices count\n  %s\n  %s' % (self.test_name, self._get_dices_str(dices), 
      self._get_message('invalid dices count', len(dices), input_dices_count)))
    for dice in dices:
      self._check( dice < 7 and dice > 0, 
      '%s FAIL - dices\n  %s\n  %s' % (self.test_name, self._get_dices_str(dices), 
      self._get_message('invalid dice', dice, '[1 or 2 or 3 or 4 or 5 or 6]')))


if __name__ == "__main__":
  comprtr = GComparator('Welcome to GURGEN world!\nNumber of dices:dices: 3 \nGURGEN!', 1)
  score, dices = comprtr.compare_valid_data()
  comprtr.check_for_dices_values(dices)
  
