FROM python:2

RUN pip install -U "pip>=1.4" "setuptools>=0.9" "wheel>=0.21"

COPY .pypirc /root/
COPY register.sh /root/

RUN chmod +x /root/register.sh
