FROM python:3.8.1

WORKDIR /app

COPY setup.py setup.py
COPY README.md README.md
COPY betfairstreamer betfairstreamer

RUN  python setup.py sdist bdist_wheel

RUN pip install /app/dist/betfairstreamer-0.2.2.tar.gz

CMD ["betfairstreamer"]