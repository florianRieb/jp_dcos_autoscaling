FROM python:3.6.1-alpine
ADD autoscale.py /
ADD tokenfile /

RUN pip install requests

ENTRYPOINT ["python", "autoscale.py"]

