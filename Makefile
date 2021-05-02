# environment variables for Docker container run parameters.
TOPLVL=${PWD}
DATADIR=${TOPLVL}/data

ARGS=
APP_ROOT=/intend4
CON_DATADIR=/data
ENVLOC=/etc/trhenv
IMG=intend4:latest
NAME=intend4
SHELL=/bin/bash

.PHONY: help bash cleancache docker exec run stop

help:
	@echo "Make what? Try: bash, cleancache, docker, exec, run, stop"
	@echo '  where:'
	@echo '     help       - show this help message'
	@echo '     bash       - run Bash in a ${NAME} container (for development)'
	@echo '     cleancache - REMOVE ALL __pycache__ dirs from the project directory!'
	@echo '     docker     - build a production container image'
	@echo '     exec       - exec into running development server (CLI arg: NAME=containerID)'
	@echo '     run        - start a container (CLI: ARGS=args)'
	@echo '     stop       - stop a running container'

bash:
	docker run -it --rm --name ${NAME} -v ${DATADIR}:${CON_DATADIR} --entrypoint ${SHELL} ${IMG} ${ARGS}

cleancache:
	find . -name __pycache__ -print | grep -v .venv | xargs rm -rf

docker:
	docker build -t ${IMG} .

exec:
	docker cp .bash_env ${NAME}:${ENVLOC}
	docker exec -it ${NAME} ${SHELL}

run:
	@docker run -it --rm --name ${NAME} -v ${DATADIR}:${CON_DATADIR} ${IMG} --verbose --bids_dir=${CON_DATADIR} ${ARGS}

stop:
	docker stop ${NAME}
