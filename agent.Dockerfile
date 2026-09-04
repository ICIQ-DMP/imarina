FROM jenkins/ssh-agent:latest-jdk21

RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean

