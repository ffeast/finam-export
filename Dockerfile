FROM python:3.11

# Install all requirements
RUN apt update \
    && apt install -y xvfb default-jdk dbus

# Download chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
RUN bash -c "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' >> /etc/apt/sources.list.d/google-chrome.list"
RUN apt -y update
RUN apt -y install google-chrome-stable

# Install lib as module
RUN mkdir -p /usr/src/finam_export
WORKDIR /usr/src/finam_export
COPY . .
# RUN pip install -r requirements.txt
RUN pip install .

# Run
CMD xvfb-run -a --server-args="-screen 0 1280x800x24 -ac -nolisten tcp -dpi 96 +extension RANDR" python -m unittest discover -s "./tests" -p "tests_*.py" -f