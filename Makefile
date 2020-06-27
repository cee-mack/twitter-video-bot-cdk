-include .envfile
export $(shell sed 's/=.*//' .envfile*)

test-requirements:
	pip3 install -r lambdas/requirements/test.txt

test-unit: test-requirements
	pytest lambdas/tests
