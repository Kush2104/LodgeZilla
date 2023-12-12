FROM python:3.11-slim

WORKDIR /myapp

COPY . /myapp

COPY clean_and_ingest_data.py /myapp

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000

#RUN python clean_and_ingest_data.py
CMD ["python", "run.py"]