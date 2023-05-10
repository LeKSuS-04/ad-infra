FROM python:3.10.11-bullseye

WORKDIR /app
COPY src/ .

RUN apt update -y && apt install unzip 

# Install Terraform 1.4.6
RUN wget -P /tmp https://hashicorp-releases.yandexcloud.net/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip
RUN unzip -d /tmp -o /tmp/terraform_1.4.6_linux_amd64.zip
RUN mv /tmp/terraform /bin/terraform

# Initialize terraform
VOLUME [ "/app/terraform" ]
ENV TF_CLI_CONFIG_FILE=/app/terraform/mirror.tfrc
RUN terraform -chdir=./terraform init

# Set up python
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --no-cache --upgrade pip setuptools

# Install Ansible 7.5.0
RUN python -m pip install --no-cache --upgrade ansible==7.5.0

# Set up OVPNGen
RUN git clone https://github.com/LeKSuS-04/OVPNGen.git
RUN python -m pip install --no-cache --upgrade -r OVPNGen/requirements.txt

# Install control script requirements
RUN pip install --no-cache --upgrade -r script/requirements.txt
