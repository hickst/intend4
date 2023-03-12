# Tests of the IntendedFor CLI module.
#   Written by: Tom Hicks and Dianne Patterson. 12/7/2021.
#   Last Modified: Update tests for required modality flag.
#
import os
import pytest
import sys
import tempfile

from tests import TEST_RESOURCES_DIR
from intend4 import BIDS_DIR
import intend4.intend4_cli as cli

DATA_SUBDIR = 'data'                   # subdirectory name for data root dir in temp directories
SYSEXIT_ERROR_CODE = 2                 # seems to be error exit code from argparse


@pytest.fixture
def clear_argv():
  sys.argv = []


@pytest.fixture
def popdir(request):
  yield
  os.chdir(request.config.invocation_dir)


class TestIntend4CLI(object):

  bids_test_dir = os.path.join(TEST_RESOURCES_DIR, DATA_SUBDIR)

  def test_check_bids_dir(self, capsys):
    """
    Check that the bids dir is writeable
    """
    if (os.environ.get('RUNNING_IN_CONTAINER') is None):
      with tempfile.TemporaryDirectory() as tmpdir:
        print(f"tmpdir={tmpdir}")

        # change permissions on directory to readonly
        os.chmod(tmpdir, 0o0444)
        print(f"NOWRITE_PERM={os.stat(tmpdir).st_mode}")

        # test method with non-writeable dir and check for error
        with pytest.raises(SystemExit) as se:
          cli.check_bids_dir('TEST', tmpdir)

        assert se.value.code == cli.BIDS_DIR_EXIT_CODE
        _, syserr = capsys.readouterr()
        print(f"CAPTURED SYS.ERR:\n{syserr}")
        assert 'A writeable BIDS data directory must be specified' in syserr
    else:
      assert True


  def test_main_no_modality(self, capsys, clear_argv):
    with pytest.raises(SystemExit) as se:
      sys.argv = ['intend4']
      cli.main()
    assert se.value.code == SYSEXIT_ERROR_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert 'the following arguments are required: -m/--modality' in syserr


  def test_main_bad_modality(self, capsys):
    with pytest.raises(SystemExit) as se:
      sys.argv = ['intend4', '-m', 'fMRI' ]
      cli.main()
    assert se.value.code == SYSEXIT_ERROR_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert 'argument -m/--modality: invalid choice' in syserr


  def test_main_noargs(self, capsys, clear_argv):
    with pytest.raises(SystemExit) as se:
      cli.main()
    assert se.value.code == SYSEXIT_ERROR_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert f"usage: {cli.PROG_NAME}" in syserr


  def test_main_help(self, capsys, clear_argv):
    with pytest.raises(SystemExit) as se:
      sys.argv = ['intend4', '-h']
      cli.main()
    assert se.value.code == 0          # help is not an error for parseargs
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert f"usage: {cli.PROG_NAME}" in sysout


  def test_main_nosubjnums(self, capsys, clear_argv):
    with pytest.raises(SystemExit) as se:
      sys.argv = ['intend4', '-v', '-m', 'bold', '--bids-dir', self.bids_test_dir, '--participant-label']
      cli.main()
    assert se.value.code == cli.SUBJ_NUMS_EXIT_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert f"one or more subject numbers must be specified" in syserr


  def test_main_badbidsdir(self, capsys, clear_argv, popdir):
    """
    Invalid but writeable BIDS_DIR specified => bids validator error.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")
      # copy of data omitted: not valid BIDS directory
      os.chdir(tmpdir)
      sys.argv = ['intend4', '-v', '-m', 'bold', '--bids-dir', tmpdir, '--participant-label', '188']
      with pytest.raises(RuntimeError) as rte:
        cli.main()
      assert 'BIDS validator got an error while processing the BIDS Data directory' in str(rte)


  def test_main_defaultbidsdir(self, capsys, clear_argv):
    """
    Default BIDS_DIR and in container => success.
    """
    if (os.environ.get('RUNNING_IN_CONTAINER') is not None):
      os.system(f"cp -Rp {self.bids_test_dir}/* {BIDS_DIR}")
      sys.argv = ['intend4', '-v', '-m', 'bold', '--participant-label', '188']
      cli.main()
      # os.system(f"rm -rf {BIDS_DIR}")  # clean up
      sysout, syserr = capsys.readouterr()
      print(f"CAPTURED SYS.ERR:\n{syserr}")
      assert "IntendedFor field in sidecar files for modality 'bold'" in syserr
      assert 'IntendedFor fields in' in syserr
    else:
      assert True


  def test_main_verbose(self, capsys, clear_argv, popdir):
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")
      os.system(f"cp -Rp {self.bids_test_dir} {tmpdir}")
      os.chdir(tmpdir)
      sys.argv = ['intend4', '-v', '-m', 'bold', '--bids-dir', os.path.join(tmpdir, DATA_SUBDIR), '--participant-label', '188']
      cli.main()
      sysout, syserr = capsys.readouterr()
      print(f"CAPTURED SYS.ERR:\n{syserr}")
      assert "IntendedFor field in sidecar files for modality 'bold'" in syserr
      assert 'IntendedFor fields in' in syserr
