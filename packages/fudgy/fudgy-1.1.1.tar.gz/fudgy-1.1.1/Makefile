.DEFAULT_GOAL := all

all: test lint build

build:
	python -m flit build

deps:
	python -m pip install --upgrade pip
	python -m pip install black flake8 flit

lint:
	python -m flake8 fudge

publish:
	python -m flit publish

test:
	python -m unittest discover
