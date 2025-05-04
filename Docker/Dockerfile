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

CMD ["zsh"]