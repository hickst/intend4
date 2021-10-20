FROM python:3.9.7

LABEL maintainer="Tom Hicks hickst@email.arizona.edu"

ARG TESTS=notests

ENV RUNNING_IN_CONTAINER True
ENV INSTALL_PATH /intend4

RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY setup.py setup.py
COPY .bash_env /etc/trhenv
COPY intend4 intend4
COPY config config
COPY $TESTS $TESTS

# following line runs setup.py to setup CLI scripts:
RUN pip install .

ENTRYPOINT [ "intend4" ]
CMD [ "-v", "-h" ]
