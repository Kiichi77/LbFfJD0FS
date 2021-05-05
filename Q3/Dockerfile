FROM        ubuntu:focal
RUN         apt-get update && apt-get install -y build-essential gnupg python3 python3-setuptools python3-pip
COPY        ./requirements.txt /webapp/requirements.txt
WORKDIR     /webapp

RUN         python3 -m pip install -r requirements.txt
COPY        [^docker]* /webapp/

ENV         LC_ALL C.UTF-8
ENV         LANG C.UTF-8

EXPOSE      5000
ENTRYPOINT  ["python3"]
CMD         ["main.py"]