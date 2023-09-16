CWD=$(shell pwd)
USER=$(shell id -u)
GROUP=$(shell id -g)

DOCKER_RUN=docker run \
	--volume "/etc/passwd:/etc/passwd:ro" \
	--volume "$(CWD)/config.yaml:/app/config.yaml:ro" \
	--volume "$(CWD)/teams.yaml:/app/teams.yaml:ro" \
	--volume "$(CWD)/generated/:/app/generated/" \
	--volume "$(CWD)/resources/:/app/resources/" \
	--volume "ad-infra-terraform:/app/terraform" \
	--volume "ad-infra-ansible:/app/ansible" \
	--volume "ad-infra-internal:/private" \
	--user "$(USER)" \
	--interactive \
	--tty \
	--rm
AD_INFRA=$(DOCKER_RUN) ad-infra

.PHONY: deploy
deploy:
	$(AD_INFRA) deploy
	
.PHONY: plan
plan:
	$(AD_INFRA) plan

.PHONY: destroy
destroy:
	$(AD_INFRA) destroy

.PHONY: shell
shell:
	$(DOCKER_RUN) --entrypoint="/bin/bash" ad-infra

.PHONY: docker-build
docker-build:
	DOCKER_BUILDKIT=1 docker build --tag ad-infra .

.PHONY: docker-pull
docker-pull:
	docker pull iamleksus/ad-infra:latest

.PHONY: docker-clean
docker-clean:
	docker rmi ad-infra 2>/dev/null || echo "Docker image doesn't exist"
	for volume in ad-infra-ansible ad-infra-terraform ad-infra-internal; do docker volume rm $$volume 2>/dev/null || echo "Volume $$volume doesn't exist"; done
