# Tests of the IntendedFor module.
#   Written by: Tom Hicks and Dianne Patterson. 10/19/2021.
#   Last Modified: Add some test stubs and tests for subjrelpath.
#
import os
import pytest
import tempfile

from tests import TEST_DATA_DIR
import intend4.intend4 as in4


@pytest.fixture
def popdir(request):
  yield
  os.chdir(request.config.invocation_dir)


class TestIntend4(object):

  contents = { "contents": "fake JSON contents" }
  dsdescr_fyl = f"{TEST_DATA_DIR}/dataset_description.json"

  def test_get_permissions(self):
    perms = in4.get_permissions(self.dsdescr_fyl)
    print(perms)
    assert perms is not None
    assert type(perms) == int
    assert perms == 33188


  def test_get_sidecar_and_modify(self):
    """
    DP test 96-113...TO DO.  See test_fetcher for example of pytest fixture JSON dictionary
    """
    pass


  def test_has_session_false(self):
    """
    DP test: 118: Return false if the subject has no sessions (e.g. resources/data/sub-188)
    subj = 'resources/data/sub-188'
    subj_id = in4.has_session(self.subj)
    """
    pass


  def test_has_session_true(self):
    """
    DP test: 118: Return true if the subject has sessions e.g., resources/data/sub-219: ses-ctbs & ses-itbs
    subj = 'resources/data/sub-219'
    subj_id = in4.has_session(self.subj)
    """
    pass


  def test_modify_intended_for_add(self):
    """
    DP test 128-130: I think we need a fixture which is a dictionary. See test_fetcher for example of pytest fixture JSON dictionary. After running this, one of two things will happen: the sorted dictionary will be returned with the added IntendedFor field (as in this test) OR with the contents of that field removed (next test)
    """
    pass

  def test_modify_intended_for_rm(self):
    """
    # DP test 128-130: Return sorted dictionary with IntendedFor field contents removed
    remove=in4.modify_intended_for(self.remove=True)
    """
    pass


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


  def test_sessions_for_subject_nosess(self):
    """
    DP test 158: this function gets the session ID (if any) out of the bids layout object, given the subject id.  The problem is creating or faking the bids layout object??
      a subject without sessions: resources/data/sub-188.
      subj_nosess = '188' # I don't recall whether we need sub-188 or 188 for the subj_id
      subj_id = in4.sessions_for_subject(self.subj_nosess)
    """
    pass


  def test_sessions_for_subject_sess(self):
    """
    DP test 158: this function gets the session ID (if any) out of the bids layout object, given the subject id.  The problem is creating or faking the bids layout object??
      It should probably be tested against:
      a subject with sessions: resources/data/sub-219/ses-ctbs and ses-itbs
      subj_sess = '219' # I don't recall whether we need sub-219 or 219 for the subj_id
      subj_id = in4.sessions_for_subject(self.subj_sess)
    """
    pass


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


  def test_update_fieldmap(self):
    """
    DP test 182-189: this function provides the arguments modality, args, layout subj_id, session_id (which defaults) to 2 other functions: get_image_paths, and then get_sidecar_and_modify.  There is also a verbose option.
      What to test: make sure verbose option works??

    Test verbose option (or maybe this should happen in cli?)
    First set a verbose option to be passed in (but it isn't the only item in the dictionary, so this worries me)

    sys.argv = ['-v']
    verbosity=in4.update_fieldmap(self.args.get)
    assert in4.update_fieldmap(verbosity) is True

    I think there is a reason we skipped this one: It mostly calls other functions
    """
    pass


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
