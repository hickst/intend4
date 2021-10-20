# Tests of the IntendedFor module.
#   Written by: Tom Hicks and Dianne Patterson. 10/19/2021.
#   Last Modified: Initial creation.
#
import os
import pytest
import tempfile

from tests import TEST_RESOURCES_DIR
import intend4.intend4 as in4


@pytest.fixture
def popdir(request):
  yield
  os.chdir(request.config.invocation_dir)


class TestIntend4(object):

  def test_dummy(self):
    return True
