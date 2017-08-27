FROM python:3.6

ADD . /code
WORKDIR /code

RUN pip3 install --upgrade pip
RUN pip3 install -r /code/dev-requirements.txt
RUN pip3 install -e .

EXPOSE 8000

CMD ["python", "examples/cars/main.py"]
