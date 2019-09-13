ROOT_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

all: run

clean:
	rm -rf env

env:
	virtualenv --python=python3 env
	env/bin/pip install -r requirements
	#env/bin/pip install -e $(ROOT_DIR)

test: env
	env/bin/python -m unittest discover -s tests
