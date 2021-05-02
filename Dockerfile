FROM python:3.9.4

LABEL maintainer="Dianne Patterson dkp@email.arizona.edu"

ARG TESTS=notests

ENV RUNNING_IN_CONTAINER True
ENV INSTALL_PATH /app

RUN mkdir -p $INSTALL_PATH $INSTALL_PATH/scripts /vos/catalogs /vos/images /work

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY setup.py setup.py
COPY code code
# COPY config config
# COPY $TESTS $TESTS

# following line runs setup.py to setup CLI scripts:
RUN pip install .

ENTRYPOINT [ "./code/add_intended4.py" ]
CMD [ "-v", "-h" ]