SHELL := /bin/bash

install:
	pip install MySQL-python
	pip install PrettyTable

database:
	mysql -u $(user) -h $(host) -p < createTables.sql
	source ./build_secret.sh $(host) $(user) $(password)

run:
	python main.py
