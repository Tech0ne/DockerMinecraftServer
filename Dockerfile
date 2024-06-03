FROM ubuntu:22.04

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y python3 python3-pip ranger cmake make git gettext openjdk-8-jre openjdk-17-jre openjdk-21-jre

RUN git clone https://github.com/neovim/neovim /tmp/nvim
RUN bash -c "cd /tmp/nvim/ && make CMAKE_BUILD_TYPE=RelWithDebInfo"
RUN bash -c "cd /tmp/nvim/build/ && cpack -G DEB"
RUN bash -c "cd /tmp/nvim/build/ && apt-get install -y ./nvim-linux64.deb"

RUN sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'

RUN mkdir -p /root/.config/nvim/
RUN mkdir -p /root/.config/ranger/

COPY ./init.vim /root/.config/nvim/init.vim
RUN nvim -c ":PlugInstall" -c ":q" -c ":q"

ENV EDITOR="nvim"

RUN echo "set show_hidden true" >> /root/.config/ranger/rc.conf

RUN pip3 install requests rich getch

# EXPOSE 25565
# Default server port

COPY ./run.py /run.py

CMD [ "python3", "/run.py" ]
