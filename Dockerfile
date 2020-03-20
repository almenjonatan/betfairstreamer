FROM python:3.8.2

workdir /app

RUN pip install tox
RUN git clone --branch backtest https://github.com/almenjonatan/betfairstreamer.git /app
RUN pip install -r requirements.txt
