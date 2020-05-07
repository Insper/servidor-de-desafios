
# Pull base image
FROM python:3.7

# Set environment variable
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD . /servidor

WORKDIR /servidor/ChallengeTestRunner
RUN python setup.py install

# install dependencies
WORKDIR /servidor
RUN pip install -r requirements.txt

RUN ["chmod", "+x", "/servidor/docker-entrypoint.sh"]
ENTRYPOINT ["/servidor/docker-entrypoint.sh"]
