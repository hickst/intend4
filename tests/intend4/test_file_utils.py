# Tests for the file utilities module.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Move test_get_permissions to here.
#
import os
import tempfile
from pathlib import Path

import intend4.file_utils as utils
from tests import TEST_DATA_DIR, TEST_RESOURCES_DIR


class TestFileUtils(object):

  tmpPath = '/tmp'
  dirPath = '/tmp/MadeUpDIR'
  dirLink = '/tmp/linkToMadeUpDIR'
  fylPath = '/tmp/HiGhLy_UnLiKeLy'
  fylLink = '/tmp/linkToHiGhLy_UnLiKeLy'

  dsdescr_fyl    = f"{TEST_DATA_DIR}/dataset_description.json"
  empty_test_fyl = f"{TEST_RESOURCES_DIR}/empty.txt"
  bold_test_fyl  = f"{TEST_RESOURCES_DIR}/bold_test.tsv"


  def test_copy_tree(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      print(f"tmpdir={tmpdir}")
      utils.copy_tree(TEST_RESOURCES_DIR, tmpdir)
      tr_files = os.listdir(TEST_RESOURCES_DIR)
      tmp_files = os.listdir(tmpdir)
      print(f"TR_FILES={tr_files}")
      print(f"TMP_FILES={tmp_files}")
      assert tmp_files is not None
      assert len(tmp_files) == len(tr_files)


  def test_filename_core(self):
    assert utils.filename_core(None) == ''
    assert utils.filename_core('') == ''
    assert utils.filename_core('/tmp') == 'tmp'
    assert utils.filename_core('/tmp/somefile') == 'somefile'
    assert utils.filename_core('/tmp/somefile.py') == 'somefile'


  def test_full_path(self):
    home = str(Path.home())
    assert utils.full_path('~') == home
    assert utils.full_path('~/.bashrc') == f'{home}/.bashrc'
    assert utils.full_path(self.tmpPath) == self.tmpPath
    assert utils.full_path('/tmp/somefile') == '/tmp/somefile'
    assert utils.full_path('/tmp/somefile.py') == '/tmp/somefile.py'


  def test_gather_file_info(self):
    finfo = utils.gather_file_info(self.empty_test_fyl)
    assert finfo is not None
    assert finfo != {}
    assert len(finfo) == 3
    assert finfo.get('file_size') == 0


  def test_gen_file_paths(self):
    paths = [ p for p in utils.gen_file_paths(os.getcwd()) ]
    assert len(paths) != 0, "The generated path list for PWD is not empty."

    paths = [ p for p in utils.gen_file_paths(self.fylPath) ]
    assert len(paths) == 0, "The generated path list for non-existant directory is empty."


  def test_get_permissions(self):
    perms = utils.get_permissions(self.dsdescr_fyl)
    print(perms)
    assert perms is not None
    assert type(perms) == int
    assert perms == 33188


  def test_good_dir_path(self):
    # also tests is_readable
    assert utils.good_dir_path('dummy') is False
    assert utils.good_dir_path(self.fylPath) is False
    assert utils.good_dir_path(self.dirPath) is False

    assert utils.good_dir_path('.') is True
    assert utils.good_dir_path('/') is True
    assert utils.good_dir_path(self.tmpPath) is True

    # setup directories and links
    try:
      os.mkdir(self.dirPath, mode=0o444)
      dirp = Path(self.dirPath)
      dlnk = Path(self.dirLink)
      dlnk.symlink_to(dirp)

      assert utils.good_dir_path(self.dirPath) is True
      assert utils.good_dir_path(self.dirLink) is True
    finally:
      # cleanup directories and links
      os.rmdir(self.dirPath)
      os.remove(self.dirLink)


  def test_good_dir_path_write(self):
    # also tests is_writable
    assert utils.good_dir_path('dummy', True) is False
    assert utils.good_dir_path(self.fylPath, True) is False
    assert utils.good_dir_path(self.dirPath, True) is False

    assert utils.good_dir_path('.', True) is True
    assert utils.good_dir_path(self.tmpPath, True) is True

    try:
      # setup directories and links
      os.mkdir(self.dirPath, mode=0o775)
      dirp = Path(self.dirPath)
      dlnk = Path(self.dirLink)
      dlnk.symlink_to(dirp)

      assert utils.good_dir_path(self.dirPath) is True
      assert utils.good_dir_path(self.dirPath, True) is True
      assert utils.good_dir_path(self.dirLink) is True
      assert utils.good_dir_path(self.dirLink, True) is True

    finally:
      # cleanup directories and links
      os.rmdir(self.dirPath)
      os.remove(self.dirLink)


  def test_good_file_path(self):
    # also tests is_readable
    assert utils.good_file_path('.') is False
    assert utils.good_file_path('/') is False
    assert utils.good_file_path(self.tmpPath) is False
    assert utils.good_file_path('dummy') is False
    assert utils.good_file_path('/dummy') is False
    assert utils.good_file_path('/images/JADES/NONE.fits') is False

    # setup files and links
    fylp = Path(self.fylPath)
    fylp.touch(mode=0o444)
    flnk = Path(self.fylLink)
    flnk.symlink_to(fylp)               # ln -s fylPath fylLink

    assert utils.good_file_path(self.fylPath) is True
    assert utils.good_file_path(self.fylLink) is True

    # cleanup directories and links
    os.remove(self.fylPath)
    os.remove(self.fylLink)


  def test_good_file_path_write(self):
    # also tests is_writable
    assert utils.good_file_path('.', True) is False
    assert utils.good_file_path('/', True) is False
    assert utils.good_file_path('dummy') is False
    assert utils.good_file_path(self.tmpPath, True) is False
    assert utils.good_file_path(self.fylPath) is False
    assert utils.good_file_path(self.fylLink) is False

    # setup files and links
    fylp = Path(self.fylPath)
    fylp.touch(mode=0o444)
    flnk = Path(self.fylLink)
    flnk.symlink_to(fylp)               # ln -s fylPath fylLink

    assert utils.good_file_path(self.fylPath) is True
    assert utils.good_file_path(self.fylLink) is True

    # cleanup directories and links
    os.remove(self.fylPath)
    os.remove(self.fylLink)


  def test_is_acceptable_filename(self):
    FILE_EXTS = ['.tsv', '.tsv.gz']
    assert utils.is_acceptable_filename('.tsv', FILE_EXTS) is True
    assert utils.is_acceptable_filename('.tsv.tsv', FILE_EXTS) is True
    assert utils.is_acceptable_filename('x.tsv', FILE_EXTS) is True
    assert utils.is_acceptable_filename('X.Y.tsv', FILE_EXTS) is True
    assert utils.is_acceptable_filename('XXX-YYY_.tsv', FILE_EXTS) is True
    assert utils.is_acceptable_filename('.tsv.gz', FILE_EXTS) is True
    assert utils.is_acceptable_filename('.tsv.tsv.gz', FILE_EXTS) is True
    assert utils.is_acceptable_filename('x.tsv.gz', FILE_EXTS) is True
    assert utils.is_acceptable_filename('X.Y.tsv.gz', FILE_EXTS) is True
    assert utils.is_acceptable_filename('XXX-YYY_.tsv.gz', FILE_EXTS) is True

    assert utils.is_acceptable_filename('.', FILE_EXTS) is False
    assert utils.is_acceptable_filename('.tsvy', FILE_EXTS) is False
    assert utils.is_acceptable_filename('.tsv.tsvy', FILE_EXTS) is False
    assert utils.is_acceptable_filename('tsv', FILE_EXTS) is False
    assert utils.is_acceptable_filename('tsv.gz', FILE_EXTS) is False
    assert utils.is_acceptable_filename('X.fit', FILE_EXTS) is False
    assert utils.is_acceptable_filename('X.tsvgz', FILE_EXTS) is False
    assert utils.is_acceptable_filename('bad.tsv_gz', FILE_EXTS) is False
    assert utils.is_acceptable_filename('yyy.exe', FILE_EXTS) is False
    assert utils.is_acceptable_filename('YYY.EXE', FILE_EXTS) is False
    assert utils.is_acceptable_filename('BAD.ONE', FILE_EXTS) is False
    assert utils.is_acceptable_filename('BAD.ONE.gz', FILE_EXTS) is False


  def test_path_has_dots(self):
    assert utils.path_has_dots('.') is True
    assert utils.path_has_dots('..') is True
    assert utils.path_has_dots('./..') is True
    assert utils.path_has_dots('./usr/dummy/') is True
    assert utils.path_has_dots('../usr/dummy/') is True
    assert utils.path_has_dots('/usr/dummy/./smarty') is True
    assert utils.path_has_dots('/usr/dummy/../smarty') is True
    assert utils.path_has_dots('/usr/dummy/.') is True
    assert utils.path_has_dots('/usr/dummy/..') is True

    assert utils.path_has_dots(None) is False
    assert utils.path_has_dots('') is False
    assert utils.path_has_dots('dummy') is False
    assert utils.path_has_dots('dummy.txt') is False
    assert utils.path_has_dots('dummy.file.txt') is False
    assert utils.path_has_dots('/') is False
    assert utils.path_has_dots('/dummy') is False
    assert utils.path_has_dots('/usr/dummy') is False
    assert utils.path_has_dots('/usr/dummy/') is False


  def test_validate_path_strings(self):
    FILE_EXTENTS = ['.txt']
    testpaths = [ '.', '/', '/NoSuch',
                  self.tmpPath,
                  '/tmp/NoSuch',
                  self.empty_test_fyl,
                  self.bold_test_fyl,
                  '/images/JADES/NONE.fits',
                  '', None ]
    pathlst = utils.validate_path_strings(testpaths, FILE_EXTENTS)
    print("PATHLIST={}".format(pathlst))
    assert len(pathlst) == 4
    assert self.tmpPath in pathlst
    assert self.empty_test_fyl in pathlst
    assert self.bold_test_fyl not in pathlst
    assert '/images/JADES/NONE.fits' not in pathlst


  def test_validate_path_strings_tsv(self):
    FILE_EXTENTS = ['.tsv', '.TSV']
    testpaths = [ '.', '/', '/NoSuch',
                  self.tmpPath,
                  '/tmp/NoSuch',
                  self.empty_test_fyl,
                  self.bold_test_fyl,
                  '/images/JADES/NONE.fits',
                  '', None ]
    pathlst = utils.validate_path_strings(testpaths, FILE_EXTENTS)
    print("PATHLIST={}".format(pathlst))
    assert len(pathlst) >= 1
    assert self.tmpPath in pathlst
    assert self.bold_test_fyl in pathlst
    assert '/images/JADES/NONE.fits' not in pathlst
    assert self.empty_test_fyl not in pathlst
