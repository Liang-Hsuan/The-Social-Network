install:
	pip install MySQL-python

database:
	mysql -u $(user) -h $(host) -p < createTables.sql && $(password)

run:
	python main.py
