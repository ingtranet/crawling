IMAGE=ingtranet/crawling

build:
	docker build -t ${IMAGE} .

push: build
	docker push ${IMAGE}