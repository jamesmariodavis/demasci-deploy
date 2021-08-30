IMAGE_NAME=python_base
ABSOLUTE_PATH=$(abspath .)

######################
# Docker Development #
######################
.PHONY: build-image
build:
	docker build \
		--tag $(IMAGE_NAME):latest  \
		--file docker/Dockerfile .

.PHONY: enter-container
docker-ssh:
	docker run -it \
       --entrypoint="" \
       --rm \
       --net=host \
       --workdir=/python_base \
	--env PYTHONPATH=/python_base \
	--volume $(ABSOLUTE_PATH):/python_base \
       --env-file docker/env_file \
       $(IMAGE_NAME):latest \
       /bin/bash