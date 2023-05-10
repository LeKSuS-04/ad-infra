CWD=$(shell pwd)
USER=$(shell id -u)
GROUP=$(shell id -g)

#################### RESOURCES ####################

CONTAINER_MAKE = docker run \
	--volume "$(CWD)/config.yaml:/script/config.yaml" \
	--volume "$(CWD)/teams.yaml:/script/teams.yaml" \
	--volume "$(CWD)/generated/:/script/generated/" \
	--user="$(USER):$(GROUP)" \
	-it --rm ad-infra

.PHONY: deploy
deploy:
	$(SCRIPT) deploy

.PHONY: inspect
inspect:
	$(BASH)

.PHONY: container
container:
	docker build --tag ad-infra .

.PHONY: rm-container
rm-container:
	docker rmi ad-infra
