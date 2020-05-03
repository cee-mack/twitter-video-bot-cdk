-include .envfile
export $(shell sed 's/=.*//' .envfile*)

test-requirements:
	pip3 install -r app/requirements/test.txt

test-unit: test-requirements
	pytest app/tests
