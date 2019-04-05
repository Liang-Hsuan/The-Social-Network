# The Social Network

A simple social network command line interface tool

---

You can **skip** Installations section if you want to use the complied executable `./main` instead of run `./main.py` yourself.

## Requirements

- [MySQL](https://dev.mysql.com/downloads/installer/)
- [Python](https://www.python.org/downloads/) (make sure [pip](https://pip.pypa.io/en/stable/installing/) is also installed) (skip this if you run `./main` directly)

**Possible dependencies improvement:**

Use docker as dependencies packaging and run the app on the container. However, due to time constrain dockerfile is not provided. All dependencies and app need to be installed and run locally for now.

## Installations

*Note: Make sure all the requirements been met to proceed to installations.*

Run `make install` to install all the necessary libraries for the client.

## Database

Run the SQL file provided (*createTables.sql*) to add necessary database and tables for the social network app. Alternately, you can run the make command below:

``` Bash
make database host=127.0.0.1 user=myusername password=mypassword
```

Also, please disable ONLY_FULL_GROUP_BY mode in MySQL:

``` SQL
-- MySQL console
mysql > SET GLOBAL sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));
```

---

Now you are good to go ;) see the Usages section below for interface commands overview.

## Usages

To run the app do `make run`.

**create**

create a new user with given user name, first name and last name, birthday, and gender

``` Bash
#  create [username] [name ("firstName lastName")] [birthday (YYYY-MM-DD)] [gender (m/f)]
(Cmd) create best_student "David Zhang" 2000-06-30 m
```

**login**

log in to the account of the given user name

``` Bash
# login [username]
(Cmd) login best_student
```

**topic**

create a topic name and its optional parent topic

``` Bash
# topic [topic_name ("" if has space)] [parent_topic_name (optional; "" if has space)]
topic "ECE 356" Classes
```

**follow**

follow a user or a topic

``` Bash
# follow [-u | -t] [username | topic_name]
follow -u second_best_student
follow -t "ECE 356"
```

**unfollow**

unfollow a user or a topic

``` Bash
# unfollow [-u | -t] [username | topic_name]
unfollow -u second_best_student
unfollow -t Clubbing
```

**post**

submit a post with given text content and topic(s)

``` Bash
# post [content ("" if has space)] [topics (separated by comma; "" if has space)]
post "I love ECE 356 course" "ECE 356",Study,Love
```

**reply**

reply a response to a post with given post ID and content text

``` Bash
# reply [post_id] [content ("" if has space)]
reply 33 "I agree with you, I also love ECE 356"
```

**read**

read the details of a post with given post ID

``` Bash
# read [post_id]
read 33
```

**like**

like a post with the given post ID to increase its likes number

``` Bash
# like [post_id]
like 33
```

**dislike**

dislike a post with the given post ID to increase its dislike number

``` Bash
# dislike [post_id]
dislike 33
```

**list**

list all the posts or topics or users or groups
if `--followed` flag is provided then only show the followed posts or topics or users or groups
followed posts will show all the posts from the users or contain the topics you follow

``` Bash
# list [-p | -t | -u | -g] [--followed (optional)]
list -p
list -p --followed
list -t
list -t --followed
list -u
list -u --followed
list -g
list -g --followed
```

**show**

show all the new posts from followed user or topic since last read
if `--unread` flag is provided then show all the unread posts from followed user or topic

``` Bash
# show [-u | -t] [username | topic_name] [--unread (optional)]
show -u best_student
show -u best_student --unread
show -t "ECE 356"
show -t "ECE 356" --unread
```

**group**

create a group with the given group name

``` Bash
# group [groupname ("" if has space)]
group "ECE 356 Fanboys"
```

**join**

join to a group with the given group ID

``` Bash
# join [groupID]
join 33
```

**logout**

exit the application

``` Bash
logout
```
