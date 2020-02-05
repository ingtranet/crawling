IMAGE=ingtranet/crawler

build:
	docker build -t ${IMAGE} .

push: build
	docker push ${IMAGE}