FROM python:3.10.11-bullseye

WORKDIR /app
COPY --chown=1000:1000 --chmod=755 script/ ./script/
COPY --chown=1000:1000 --chmod=777 ansible/ ./ansible/
COPY --chown=1000:1000 --chmod=777 terraform/ ./terraform/
RUN mkdir -p /internal

RUN apt update -y && apt install unzip openvpn -y

# Install Terraform 1.4.6
RUN wget -P /tmp https://hashicorp-releases.yandexcloud.net/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip
RUN unzip -d /tmp -o /tmp/terraform_1.4.6_linux_amd64.zip
RUN mv /tmp/terraform /bin/terraform

# Initialize terraform
ENV TF_CLI_CONFIG_FILE=/app/terraform/mirror.tfrc
RUN terraform -chdir=./terraform init

# Set up python
ENV PYTHONUNBUFFERED=1

# Install control script requirements
COPY ./requirements.txt .
RUN pip install --no-cache --upgrade -r requirements.txt

WORKDIR /app
ENTRYPOINT [ "./script/main.py" ]
