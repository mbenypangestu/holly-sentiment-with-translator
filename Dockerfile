FROM python:3

ADD . /

RUN pip3 install -r requirements.txt

CMD ["python3", "./start_translate_sentiment.py"]