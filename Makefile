CWD=$(shell pwd)
USER=$(shell id -u)
GROUP=$(shell id -g)

DOCKER_FLAGS = docker run \
	--volume "$(CWD)/config.yaml:/app/config.yaml:ro" \
	--volume "$(CWD)/teams.yaml:/app/teams.yaml:ro" \
	--volume "$(CWD)/generated/:/app/generated/" \
	--volume "$(CWD)/resources/:/app/resources/" \
	--volume "ad-infra-terraform:/app/terraform" \
	--volume "ad-infra-ansible:/app/ansible" \
	--interactive \
	--tty \
	--rm
IMAGE = $(DOCKER_FLAGS) ad-infra

.PHONY: deploy
deploy:
	$(IMAGE) deploy

.PHONY: shell
shell:
	$(DOCKER_FLAGS) --entrypoint="/bin/bash" ad-infra

.PHONY: docker-build
docker-build:
	docker build --tag ad-infra .

.PHONY: docker-clean
docker-clean:
	docker rmi ad-infra
	docker volume rm ad-infra-ansible ad-infra-terraform
