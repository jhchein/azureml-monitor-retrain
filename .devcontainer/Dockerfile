FROM python:3.11-slim

# Make Python 3.11 the default
RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1

# Install pip for Python 3.11
RUN python -m ensurepip
RUN python -m pip install --upgrade pip

# Copy requirements.txt and install the packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Zsh and Oh My Zsh
RUN apt-get update && apt-get install -y zsh curl git
RUN apt-get install -y fonts-powerline
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Install autocomplete and syntax-highlighting plugins
RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
RUN git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
RUN git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-completions

# Copy .zshrc to the root user's home directory
COPY .zshrc /root/

# Set Zsh as the default shell
ENV SHELL /bin/zsh