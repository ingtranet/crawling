IMAGE=harbor.ingtra.net/library/crawling

build:
	docker build --platform amd64 -t ${IMAGE} .

push: build
	docker push ${IMAGE}