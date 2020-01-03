#!/bin/bash

docker build -t crawling . && docker run -it --rm crawling $@