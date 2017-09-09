
class TestLogger:
  """Logger to write messages about implemented steps and any failures"""

  def __init__(self, info_path, error_path):
    """create logger"""
    self.info_log_path = info_path
    self.error_log_path = error_path

  def write_info(self, line):
    """append line in log, which contain general info about test implementation"""
    print(line)
    self._write_line(self.info_log_path, line)

  def write_error(self, line):
    """append line in log, which contain only failed test info"""
    print(line)
    self._write_line(self.error_log_path, line)

  def _write_line(self, log_file_path, line):
    """append line in file"""
    with open(log_file_path, 'a') as f:
      f.write(line)
      f.write('\n')
