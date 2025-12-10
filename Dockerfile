FROM ubuntu:22.04

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python3 python3-pip ranger vim openjdk-8-jre openjdk-17-jre openjdk-21-jre

COPY ./vimrc /root/.vimrc

ENV EDITOR="nvim"

RUN mkdir -p /root/.config/ranger/
RUN echo "set show_hidden true" >> /root/.config/ranger/rc.conf

RUN pip3 install requests rich getch

# EXPOSE 25565
# Default server port

COPY ./run.py /run.py

CMD [ "python3", "/run.py" ]
