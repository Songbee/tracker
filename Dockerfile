FROM python:3.5

ENV FLASK_APP "/code/songbee_tracker/__init__.py"
EXPOSE 5000
RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
