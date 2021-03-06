# Tests of the IntendedFor module.
#   Written by: Tom Hicks and Dianne Patterson. 10/19/2021.
#   Last Modified: Add tests for do_single_subject, some other uncovered lines.
#
import os
import pytest
import tempfile

from bids import BIDSLayout
from sqlalchemy import except_all
import intend4.intend4 as in4

from unittest.mock import MagicMock
from tests import TEST_RESOURCES_DIR


@pytest.fixture
def popdir(request):
  yield
  os.chdir(request.config.invocation_dir)


class TestIntend4(object):

  bids_test_dir = f"{TEST_RESOURCES_DIR}/data"
  bads_test_dir = f"{TEST_RESOURCES_DIR}/baddata"

  contents = { "contents": "fake JSON contents" }
  # dsdescr_fyl = f"{TEST_DATA_DIR}/dataset_description.json"

  def test_do_subjects_badbids(self, popdir):
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")
      os.chdir(tmpdir)
      with pytest.raises(RuntimeError) as rte:
        in4.do_subjects('bold', {'bids_dir': tmpdir})
      assert 'BIDS validator got an error while processing the BIDS Data directory' in str(rte)


  def test_do_subjects_count(self):
    do_ss = in4.do_single_subject
    mm = MagicMock()
    args = { 'bids_dir': self.bids_test_dir }
    try:
      in4.do_single_subject = mm
      in4.do_subjects('bold', args)
    except Exception as ex:
      raise ex
    finally:
      in4.do_single_subject = do_ss
    assert mm.call_count == 3


  def test_do_single_subject_no_sess(self):
    up_fm = in4.update_fieldmap
    args = { 'bids_dir': self.bids_test_dir, 'subj_ids': ['188'] }
    in4.update_fieldmap = MagicMock()
    cnt = in4.do_subjects('bold', args)
    in4.update_fieldmap = up_fm
    assert cnt == 1


  def test_do_single_subject_sess(self):
    up_fm = in4.update_fieldmap
    args = { 'bids_dir': self.bids_test_dir, 'subj_ids': ['219'] }
    in4.update_fieldmap = MagicMock()
    cnt = in4.do_subjects('bold', args)
    in4.update_fieldmap = up_fm
    assert cnt == 2


  def test_get_fieldmap_suffix(self):
    assert in4.get_fieldmap_suffix('bold') == "phasediff"
    assert in4.get_fieldmap_suffix('dwi') == "epi"


  def test_get_sidecar_and_modify_lt1(self, capsys):
    """
    There are 3 conditions to test: if num_sidecars < 1 => error; if num_sidecars > 1 => error;
    else there is one sidecar and it works.
    """
    testlayout = BIDSLayout(self.bids_test_dir, validate=True)
    in4.get_sidecar_and_modify('bold', {}, testlayout, [], '666')
    _, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert 'sidecar file is missing for subject 666' in syserr


  def test_get_sidecar_and_modify_gt1(self, capsys):
    """
    There are 3 conditions to test: if num_sidecars < 1 => error; if num_sidecars > 1 => error;
    else there is one sidecar and it works.
    """
    testlayout = BIDSLayout(self.bads_test_dir, validate=True)
    in4.get_sidecar_and_modify('bold', {}, testlayout, [], '188')
    _, syserr = capsys.readouterr()
    print(f"CAPTURED SYS.ERR:\n{syserr}")
    assert 'Found more than 1' in syserr
    assert 'sidecars for subject 188' in syserr


  def test_get_sidecar_and_modify_eq1(self, capsys, popdir):
    """
    There are 3 conditions to test: if num_sidecars < 1 => error; if num_sidecars > 1 => error;
    else there is one sidecar and it works.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")
      os.system(f"cp -Rp {self.bids_test_dir} {tmpdir}")
      os.chdir(tmpdir)
      testlayout = BIDSLayout(os.path.join(tmpdir, 'data'), validate=True)
      in4.get_sidecar_and_modify('bold', {}, testlayout, [], '188')
      _, syserr = capsys.readouterr()
      print(f"CAPTURED SYS.ERR:\n{syserr}")
      assert syserr == ''


  def test_has_session(self):
    testlayout = BIDSLayout(self.bids_test_dir, validate=True)
    in4.has_session(testlayout, '219') is True
    in4.has_session(testlayout, '078') is False


  def test_rewrite_sidecar(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")

      # create a single empty test
      testfile = os.path.join(tmpdir, 'testcontent.json')
      open(testfile, 'a').close()      # creates empty file
      print(f"START_PERM={os.stat(testfile).st_mode}")
      files = os.listdir(tmpdir)
      print(f"FILES_BEFORE={files}")
      assert files is not None
      assert len(files) == 1

      # change permissions on file to readonly
      os.chmod(testfile, 0o0222)
      mod_perm = os.stat(testfile).st_mode
      print(f"MOD_PERM={os.stat(testfile).st_mode}")

      # now rewrite the temp file we just created:
      in4.rewrite_sidecar(self.contents, testfile)
      print(f"RE_PERM={os.stat(testfile).st_mode}")

      # should still only be the one file, but no longer empty
      files = os.listdir(tmpdir)
      print(f"FILES_AFTER={files}")
      assert files is not None
      assert len(files) == 1

      modfile = os.path.join(tmpdir, 'testcontent.json')
      fsize = os.path.getsize(modfile)
      print(f"FSIZE={fsize}")
      assert fsize >= 1
      fileperm = os.stat(modfile).st_mode
      assert fileperm == mod_perm


  def test_output_JSON_stdout(self, capsys):
    in4.output_JSON({'test': 'This should be in the output'})
    sysout, _ = capsys.readouterr()
    print(f"CAPTURED SYS.OUT:\n{sysout}")
    assert 'This should be in the output' in sysout


  def test_subjrelpath_good(self):
    "Valid subject paths."
    assert in4.subjrelpath('sub-188/dwi/sub-188_acq-AP_dwi.nii.gz') == 'dwi/sub-188_acq-AP_dwi.nii.gz'
    assert in4.subjrelpath('sub-5/pink_elephants') == 'pink_elephants'


  def test_subjrelpath_notsrpath(self):
    "Path without a subject prefix."
    assert in4.subjrelpath('ses-ctbs/dwi/sub-188_task-nad1_run-01_bold.json') is None


  def test_subjrelpath_notapath(self):
    "Filename but not a path"
    with pytest.raises(TypeError) as te:
      in4.subjrelpath('sub-188_task-nad1_run-01_bold.json')


  def test_validate_modality_good(self):
    assert in4.validate_modality('bold') == 'bold'
    assert in4.validate_modality('dwi') == 'dwi'


  def test_validate_modality_fail(self):
    with pytest.raises(ValueError, match='Modality argument must be one of'):
      in4.validate_modality('')

    with pytest.raises(ValueError, match='Modality argument must be one of'):
      in4.validate_modality('BAD argument')

    with pytest.raises(ValueError, match='Modality argument must be one of'):
      in4.validate_modality('Dwi')

    with pytest.raises(ValueError, match='Modality argument must be one of'):
      in4.validate_modality('DWI')

    with pytest.raises(ValueError, match='Modality argument must be one of'):
      in4.validate_modality('BOLD')

    with pytest.raises(ValueError, match='Modality argument must be one of'):
      in4.validate_modality('Bold')
