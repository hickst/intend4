# Tests of the IntendedFor module.
#   Written by: Tom Hicks and Dianne Patterson. 10/19/2021.
#   Last Modified: Add tests for validate_modality and rewrite_sidecar.
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
