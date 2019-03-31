install:
	pip install MySQL-python
	pip install PrettyTable

database:
	mysql -u $(user) -h $(host) -p < createTables.sql && $(password)

run:
	python main.py
