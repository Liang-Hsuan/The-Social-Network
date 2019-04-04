# The Social Network

A simple social network command line interface tool

TODO: provide exec program and direct reader to jump to installations section if don't want to run the code

## Requirements

- [MySQL](https://dev.mysql.com/downloads/installer/)
- [Python](https://www.python.org/downloads/) (make sure [pip](https://pip.pypa.io/en/stable/installing/) is also installed)

**Possible dependencies improvement:**

Use docker as dependencies packaging and run the app on the container. However, due to time constrain dockerfile is not provided. All dependencies and app need to be installed and run locally for now.

## Installations

*Note: Make sure all the requirements been met to proceed to installations.*

- Run the SQL file provided (*createTables.sql*) to add necessary database and tables for the social network app. Alternately, you can run the make command below:

``` Bash
make database host=127.0.0.1 user=myusername password=mypassword 
# or do it manually
mysql -h 127.0.0.1 -u myusername -p < createTables.sql
```

Also, please disable ONLY_FULL_GROUP_BY mode in MySQL:

``` SQL
-- MySQL console
mysql > SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
```

- Run `make install` to install all the necessary libraries for the client.

Now you are good to go ;)

## Usages

To run the app do `make run`.

TODO: add commands usages
