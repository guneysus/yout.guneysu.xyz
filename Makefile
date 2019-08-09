PYTHON := ~/.virtualenvs/yout.guneysu.xyz/bin/python3.5

default: pack

build:
	$(PYTHON) src/setup.py bdist

pack:
	@docker build -t guneysu/youtube-downloader:latest .

push:
	@docker push guneysu/youtube-downloader:latest

.PHONY: default build pack push
