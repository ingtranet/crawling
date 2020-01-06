#!/bin/bash

docker build -t crawling . && docker run -it --rm --net host crawling $@