IMAGE_NAME=python_base
ABSOLUTE_PATH=$(abspath .)
DOCKER_RUN_ENTRY_POINT=	docker run -it \
       --entrypoint="" \
       --rm \
       --net=host \
       --workdir=/python_base \
	   --env PYTHONPATH=/python_base \
	   --volume $(ABSOLUTE_PATH):/python_base \
       --env-file docker/env_file \
       $(IMAGE_NAME):latest \

######################
# Docker Development #
######################
.PHONY: build
build:
	docker build \
		--tag $(IMAGE_NAME):latest  \
		--file docker/Dockerfile .

.PHONY: docker-ssh
docker-ssh:
	$(DOCKER_RUN_ENTRY_POINT) \
       /bin/bash