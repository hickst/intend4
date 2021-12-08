# Tests of the IntendedFor CLI module.
#   Written by: Tom Hicks and Dianne Patterson. 12/7/2021.
#   Last Modified: Minor reindent.
#
import os
import pytest
import sys
import tempfile

# from tests import TEST_DATA_DIR
from tests import TEST_RESOURCES_DIR
import intend4.intend4_cli as cli

SYSEXIT_ERROR_CODE = 2                 # seems to be error exit code from argparse


@pytest.fixture
def clear_argv():
  sys.argv = []


@pytest.fixture
def popdir(request):
  yield
  os.chdir(request.config.invocation_dir)


class TestIntend4CLI(object):

  bids_test_dir = f"{TEST_RESOURCES_DIR}/data"

  def test_check_bids_dir(self, capsys):
    """
    Check that the bids dir is writeable
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")

      # change permissions on directory to readonly
      os.chmod(tmpdir, 0o0444)
      print(f"NOWRITE_PERM={os.stat(tmpdir).st_mode}")

      # test method with non-writeable dir and check for error
      with pytest.raises(SystemExit) as se:
        cli.check_bids_dir('TEST', tmpdir)

      assert se.value.code == cli.BIDS_DIR_EXIT_CODE
      sysout, syserr = capsys.readouterr()
      print(f"CAPTURED SYS.OUT:\n{sysout}")
      print(f"CAPTURED SYS.ERR:\n{syserr}")
      assert 'A writeable BIDS data directory must be specified' in syserr


  def test_main_no_modality(self, capsys, clear_argv):
    "Test of argparse"
    with pytest.raises(SystemExit) as se:
      sys.argv = ['intend4']
      cli.main()
    assert se.value.code == SYSEXIT_ERROR_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert 'the following arguments are required: modality' in syserr


  def test_main_bad_modality(self, capsys):
    with pytest.raises(SystemExit) as se:
      sys.argv = ['intend4', 'fMRI' ]
      cli.main()
    assert se.value.code == SYSEXIT_ERROR_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert 'argument modality: invalid choice' in syserr


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
      sys.argv = ['intend4', '-v', 'bold', '--bids-dir', self.bids_test_dir, '--participant-label']
      cli.main()
    assert se.value.code == cli.SUBJ_NUMS_EXIT_CODE
    sysout, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert f"one or more subject numbers must be specified" in syserr


  def test_main_verbose(self, capsys, clear_argv, popdir):
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")
      os.system(f"cp -Rp {self.bids_test_dir} {tmpdir}")
      os.chdir(tmpdir)
      sys.argv = ['intend4', '-v', 'bold', '--bids-dir', os.path.join(tmpdir, 'data'), '--participant-label', '188']
      cli.main()
      sysout, syserr = capsys.readouterr()
      print(f"CAPTURED SYS.ERR:\n{syserr}")
      assert "IntendedFor field in sidecar files for modality 'bold'" in syserr
      assert 'IntendedFor fields in' in syserr
