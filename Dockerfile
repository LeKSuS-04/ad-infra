FROM python:3.10.11-bullseye

RUN apt update -y && apt install unzip 

# Install Terraform 1.4.6
RUN wget https://hashicorp-releases.yandexcloud.net/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip
RUN unzip terraform_1.4.6_linux_amd64.zip && rm terraform_1.4.6_linux_amd64.zip
RUN mv terraform /bin/terraform

# Set up python
ENV PYTHONUNBUFFERED=1
RUN python -m pip install --no-cache --upgrade pip setuptools

# Install Ansible 7.5.0
RUN python -m pip install --no-cache --upgrade ansible==7.5.0

# Set up OVPNGen
RUN git clone https://github.com/LeKSuS-04/OVPNGen.git
RUN python -m pip install --no-cache --upgrade -r OVPNGen/requirements.txt

# Set up custom scripts
COPY scripts/requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT [ "/bin/sh" ]
