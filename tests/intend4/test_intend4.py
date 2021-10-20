# Tests of the IntendedFor module.
#   Written by: Tom Hicks and Dianne Patterson. 10/19/2021.
#   Last Modified: Add test for get_permissions.
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

  dsdescr_fyl = f"{TEST_DATA_DIR}/dataset_description.json"

  def test_get_permissions(self):
    perms = in4.get_permissions(self.dsdescr_fyl)
    print(perms)
    assert perms is not None
    assert type(perms) == int
    assert perms == 33188
