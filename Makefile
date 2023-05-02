CWD=$(shell pwd)
USER=$(shell id -u)
GROUP=$(shell id -g)


.PHONY: all
all: container resources init apply

.PHONY: clean
clean: rm-container rm-resources

#################### RESOURCES ####################

PYTHON_BIN = docker run \
	--workdir "/workdir" \
	--volume "$(CWD):/workdir" \
	--entrypoint="/usr/local/bin/python" \
	--user="$(USER):$(GROUP)" \
	-it --rm ad-infra

.PHONY: resources
resources: configs archives

.PHONY: archives
archives:
	$(PYTHON_BIN) scripts/archive/main.py

.PHONY: configs
configs: 
	$(PYTHON_BIN) scripts/config/main.py

.PHONY: rm-resources
rm-resources:
	find ./resources/* ! -name 'README.md' -exec rm -rf {} +
	rm -rf terraform/*.auto.tfvars.json

#################### TERRAFORM ####################

TERRAFORM_BIN = docker run \
	--workdir "/data" \
	--volume "$(CWD)/terraform:/data" \
	--env "TF_CLI_CONFIG_FILE=/data/.terraformrc" \
	--entrypoint="/bin/terraform" \
	--user="$(USER):$(GROUP)" \
	-it --rm ad-infra

.PHONY: init
init:
	$(TERRAFORM_BIN) init

.PHONY: plan
plan:
	$(TERRAFORM_BIN) plan

.PHONY: validate
validate:
	$(TERRAFORM_BIN) validate

.PHONY: apply
apply:
	$(TERRAFORM_BIN) apply -auto-approve

.PHONY: destroy
destroy:
	$(TERRAFORM_BIN) destroy -auto-approve

.PHONY: fmt
fmt:
	$(TERRAFORM_BIN) fmt

#################### DOCKER ####################

.PHONY: container
container:
	docker build --tag ad-infra .

.PHONY: rm-container
rm-container:
	docker rmi ad-infra
