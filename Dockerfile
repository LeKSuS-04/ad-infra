FROM python:3.12.8-bookworm

ARG TERRAFORM_VERSION=1.10.5

WORKDIR /app

RUN apt update -y && apt install unzip wireguard-tools rsync -y

# Install Terraform
RUN wget -P /tmp https://hashicorp-releases.yandexcloud.net/terraform/1.10.5/terraform_1.10.5_linux_amd64.zip
RUN unzip -d /tmp -o /tmp/terraform_1.10.5_linux_amd64.zip
RUN mv /tmp/terraform /bin/terraform

# Install Packer
RUN wget -P /tmp https://hashicorp-releases.yandexcloud.net/packer/1.9.4/packer_1.9.4_linux_amd64.zip
RUN unzip -d /tmp -o /tmp/packer_1.9.4_linux_amd64.zip
RUN mv /tmp/packer /bin/packer

# Set up python
ENV PYTHONUNBUFFERED=1

# Install control script requirements
COPY ./requirements.txt .
RUN pip install --no-cache --upgrade -r requirements.txt

# Initialize terraform
COPY --chmod=777 terraform/ ./terraform/
ENV TF_CLI_CONFIG_FILE=/app/terraform/mirror.tfrc
RUN terraform -chdir=./terraform init

# Initialize packer
COPY packer/ ./packer
RUN packer init ./packer/config.pkr.hcl

# Copy other source files
COPY --chmod=755 script/ ./script/
COPY --chmod=777 ansible/ ./ansible/
COPY --chmod=777 services/ ./services/

# Manage permissions on directories used to write files
RUN mkdir /private
RUN chmod 777 /private ./terraform ./ansible

ENTRYPOINT [ "./script/main.py" ]
