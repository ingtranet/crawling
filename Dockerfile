FROM python:3.7.7

WORKDIR /tmp
RUN apt-get update -y && apt-get install -y --no-install-recommends firefox-esr
RUN wget -nv https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz && \
    tar zxf geckodriver-v0.26.0-linux64.tar.gz && \
    mv geckodriver /usr/bin/geckodriver && \
    rm geckodriver-v0.26.0-linux64.tar.gz

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENTRYPOINT [ "/app/entrypoint.sh" ]