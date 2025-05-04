FROM ubuntu:latest

# # Update and upgrade the package list
RUN apt-get update && apt-get upgrade -y

# Install Valgrind
RUN apt-get install -y \
    valgrind \
    make \
    g++ \
    git \
    curl \
    zsh \
    nano

RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" && zsh


# Change default shell to Zsh
RUN chsh -s $(which zsh)

COPY script.sh script.sh
RUN chmod +x script.sh
# RUN [ "./script.sh" ]

CMD ["zsh"]