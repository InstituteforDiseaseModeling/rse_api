# This dockerfile is only for building and testing

FROM python:3

RUN mkdir -p /app
WORKDIR /app

ADD requirements_dev.txt setup.py README.rst HISTORY.rst ./
RUN pip install sphinx && pip install -e .
RUN pip install -e .[dev]
