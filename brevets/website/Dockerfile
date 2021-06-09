FROM python:3.8
LABEL maintainer="jlavagni@uoregon.edu"
COPY . /website
WORKDIR /website
RUN pip install -r requirements.txt
CMD ["python -u website.py"]
