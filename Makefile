# environment variables for Docker container run parameters.
TOPLVL=${PWD}
DATADIR=${TOPLVL}/data
TESTDIR=${TOPLVL}/tests

ARGS=
APP_ROOT=/intend4
CON_DATADIR=/data
ENVLOC=/etc/trhenv
EP=/bin/bash
IMG=hickst/intend4
NAME=intend4
ONLY=
SCOPE=intend4
SHELL=/bin/bash
TESTS=tests
TSTIMG=intend4:test

.PHONY: help bash cleancache docker dockert exec run runt stop test1 tests

help:
	@echo "Make what? Try: bash, cleancache, docker, dockert, exec, run, runt, stop, test1, tests"
	@echo '  where:'
	@echo '     help       - show this help message'
	@echo '     bash       - run Bash in a ${NAME} container (for development)'
	@echo '     cleancache - REMOVE ALL __pycache__ dirs from the project directory!'
	@echo '     docker     - build a production container image'
	@echo '     dockert    - build a container image with tests (for testing)'
	@echo '     exec       - exec into running development server (CLI arg: NAME=containerID)'
	@echo '     run        - start a container (CLI: ARGS=args)'
	@echo '     runt       - run the main program in a test container'
	@echo '     stop       - stop a running container'
	@echo '     test1     - run tests with a single name prefix (CLI: ONLY=tests_name_prefix)'
	@echo '     tests     - run one or all unit tests in the tests directory (CLI: TESTS=test_module)'

bash:
	docker run -it --rm --name ${NAME} -v ${DATADIR}:${CON_DATADIR} --entrypoint ${SHELL} ${TSTIMG} ${ARGS}

cleancache:
	find . -name __pycache__ -print | grep -v .venv | xargs rm -rf

docker:
	docker build -t ${IMG} .

dockert:
	docker build --build-arg TESTS=tests -t ${TSTIMG} .

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} ${EP}

run:
	@docker run -it --rm --name ${NAME} -v ${DATADIR}:${CON_DATADIR} ${IMG} --verbose --bids_dir=${CON_DATADIR} ${ARGS}

runt:
	@docker run -it --rm --name ${NAME} -v ${DATADIR}:${CON_DATADIR} ${TSTIMG} --verbose --bids_dir=${CON_DATADIR} ${ARGS}

stop:
	docker stop ${NAME}

testall:
	pytest -vv -x ${TESTS} ${ARGS} --cov-report term-missing --cov ${SCOPE}

test1:
	pytest -vv ${TESTS} -k ${ONLY} --cov-report term-missing --cov ${SCOPE}

tests:
	pytest -vv ${TESTS} ${ARGS} --cov-report term-missing --cov ${SCOPE}
