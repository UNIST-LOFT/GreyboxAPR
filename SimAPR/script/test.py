import os
from d4j_run_test_fd import instrument_patched_project

os.environ['GREYBOX_INSTR_ROOT'] = '/root/project/ASMFieldChange'

if __name__ == "__main__":
  # simple_test()
  print('Hello World!')
