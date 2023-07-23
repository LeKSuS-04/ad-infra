FROM python:3.10.11-bullseye

WORKDIR /app

RUN apt update -y && apt install unzip openvpn rsync -y

# Install Terraform 1.4.6
RUN wget -P /tmp https://hashicorp-releases.yandexcloud.net/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip
RUN unzip -d /tmp -o /tmp/terraform_1.4.6_linux_amd64.zip
RUN mv /tmp/terraform /bin/terraform

# Set up python
ENV PYTHONUNBUFFERED=1

# Install control script requirements
COPY ./requirements.txt .
RUN pip install --no-cache --upgrade -r requirements.txt

# Initialize terraform
COPY --chmod=777 terraform/ ./terraform/
ENV TF_CLI_CONFIG_FILE=/app/terraform/mirror.tfrc
RUN terraform -chdir=./terraform init

# Copy other source files
COPY --chmod=755 script/ ./script/
COPY --chmod=777 ansible/ ./ansible/
COPY --chmod=777 services/ ./services/

# Manage permissions on directories used to write files
RUN mkdir /private
RUN chmod 777 /private ./terraform ./ansible

ENTRYPOINT [ "./script/main.py" ]
