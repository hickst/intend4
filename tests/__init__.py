import os

from config.settings import APP_ROOT

TEST_DIR = None
TEST_DBCONFIG_FILEPATH = None

if (os.environ.get('RUNNING_IN_CONTAINER') is not None):
    TEST_DIR = f"{APP_ROOT}/tests"
    TEST_RESOURCES_DIR = f"{TEST_DIR}/resources"
else:
    TEST_DIR = f"{os.getcwd()}/tests"
    TEST_RESOURCES_DIR = f"{TEST_DIR}/resources"
