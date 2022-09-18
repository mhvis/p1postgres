FROM python:3.10

# I add Tini for better init management. See https://github.com/krallin/tini.
#
# The dpkgArch is necessary to pick the correct binary for the current platform.
RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
    && tiniVersion=v0.19.0 \
    && wget -O /tini https://github.com/krallin/tini/releases/download/${tiniVersion}/tini-${dpkgArch} \
    && chmod +x /tini
ENTRYPOINT ["/tini", "--"]

ENV PYTHONUNBUFFERED=1
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY p1postgres.py ./

CMD ["python", "p1postgres.py"]
