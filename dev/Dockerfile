FROM debian:12

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN apt update -y && apt upgrade -y

# MOVED HERE — before the RUN that uses this file
COPY 10-sudo /etc/sudoers.d/10-sudo

RUN apt install -y sudo nano curl wget \
    && chmod 440 /etc/sudoers.d/10-sudo \
    && useradd -m user \
    && usermod -aG sudo user \
    && chsh -s /bin/bash user


USER user
WORKDIR /app

ENV BASH_ENV="/home/user/.bash_env"
RUN touch "${BASH_ENV}"
RUN echo 'BASH_ENV="/home/user/.bash_env"' >> ~/.bashrc
RUN echo '. "${BASH_ENV}"' >> ~/.bashrc
RUN echo 'COREPACK_ENABLE_DOWNLOAD_PROMPT=0' >> ~/.bashrc

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | PROFILE="${BASH_ENV}" bash
RUN sudo chown user:user /app
RUN echo 24 > .nvmrc
RUN nvm install
RUN corepack enable pnpm && pnpm -v

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

WORKDIR /home/user

RUN sudo apt install -y openjdk-17-jre-headless tmux gcc libz-dev \
    && curl -O https://dlcdn.apache.org/kafka/4.3.1/kafka_2.13-4.3.1.tgz \
    && tar -xzf kafka_2.13-4.3.1.tgz

WORKDIR /app


CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]