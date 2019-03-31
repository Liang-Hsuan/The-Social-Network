from cmd import Cmd
from datetime import date

import MySQLdb
import shlex
import json
import pdb

class SocialNetworkPrompt(Cmd):

  db = None
  db_cursor = None
  login = False
  username = ''

  def preloop(self):
    with open('secret.json', 'r') as file:
      data = file.read()

    secret = json.loads(data)
    self.db = MySQLdb.connect(secret['host'], secret['user'], secret['password'], secret['database'])
    self.db_cursor = self.db.cursor()

  def postloop(self):
    if self.db_cursor is not None:
      self.db_cursor.close()

  def precmd(self, line):
    command = shlex.split(line)[0]

    if command not in ['login', 'create', 'logout', 'help']:
      if not self.login:
        print('please login first')
        return 'help login'

    return line

  def do_create(self, input):
    args = shlex.split(input)

    if len(args) != 4:
      print("number or arguments should be 4, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT * FROM User WHERE userName = '%s'" % args[0])

    if self.db_cursor.rowcount != 0:
      print("username %s has already been created, try another one" % args[0])
      return

    try:
      names = shlex.split(args[1])

      self.db_cursor.execute("INSERT INTO User(userName, firstName, lastName, birthDay, gender)" \
        "VALUES ('%s', '%s', '%s', '%s', '%s')" % (args[0], names[0], names[1], args[2], args[3]))
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while creating user: %s, please try again" % e)
      return

    self.username = args[0]
    self.login = True

    print("%s user created successfully" % args[0])

  def help_create(self):
    print('create [username] [name ("firstName lastName")] [birthday (YYYY-MM-DD)] [gender (m/f)]')

  def do_topic(self, input):
    args = shlex.split(input)

    if not (0 < len(args) < 3):
      print("number or arguments should be 1 or 2, %d given" % len(args))
      return

    has_parent_topic = len(args) == 2

    if has_parent_topic:
      self.db_cursor.execute("SELECT topicName FROM Topic WHERE topicName = '%s'" % args[1])

      if self.db_cursor.rowcount == 0:
        print("parent topic %s does not exist, please create it first" % args[1])
        return

    try:
      self.db_cursor.execute("INSERT INTO Topic(topicName) VALUES ('%s')" % args[0])

      if has_parent_topic:
        self.db_cursor.execute("INSERT INTO ParentTopic(topicName, parentTopicName) VALUES ('%s', '%s')" % (args[0], args[1]))

      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while creating topic: %s, please try again" % e)
      return

    print("%s topic created succesfully" % args[0])

  def help_topic(self):
    print('topic [topic_name ("" if has space)] [parent_topic_name ("" if has space)]')

  def do_post(self, input):
    args = shlex.split(input)

    if not (0 < len(args) < 3):
      print("number or arguments should be 1 or 2, %d given" % len(args))
      return

    has_topics = len(args) == 2

    if has_topics:
      topics = args[1].split(',')
      query = "SELECT * FROM Topic WHERE topicName IN ({})".format(','.join(['%s'] * len(topics)))
      self.db_cursor.execute(query, topics)

      if not (self.db_cursor.rowcount == len(topics)):
        print('topic does not exist')
        return

    try:
      self.db_cursor.execute("INSERT INTO Post(postText, createTime) VALUES ('%s', '%s')" % (args[0], str(date.today())))


      if has_topics:
        for topic in topics:
          self.db_cursor.execute("INSERT INTO PostTagTopic VALUES ((SELECT LAST_INSERT_ID()), '%s')" % topic)

      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while creating post: %s, please try again" % e)
      return

    print("post '%s' created successfully" % args[0])

  def help_post(self):
    print('post [content ("" if has space] [topics (separated by , and "" if has space)]')

  def do_login(self, input):
    if self.login:
      print('Already logged in, please logout first')
      return

    self.db_cursor.execute("SELECT * FROM User WHERE userName = '%s'" % input)
    row = self.db_cursor.fetchone()

    if self.db_cursor.rowcount == 0:
      print('no username found')
      return

    self.username = input
    self.login = True

    print('logged in successfully')

  def help_login(self):
    print('login [username]')

  def do_follow(self, input):
    args = shlex.split(input)

    if len(args) != 2:
      print("number or arguments should be 2, %d given" % len(args))
      return

    if args[0] == '-u':
      if self.username == args[1]:
        print('cannot follow yourself')
        return

      self.db_cursor.execute("SELECT * FROM User WHERE userName = '%s'" % args[1])

      if self.db_cursor.rowcount == 0:
        print("username %s does not exist" % args[1])
        return

      try:
        self.db_cursor.execute("INSERT INTO Follow(followee, follower) VALUES ('%s', '%s')" % (args[1], self.username))
        self.db.commit()
      except (MySQLdb.Error, MySQLdb.Warning) as e:
        self.db.rollback()
        print("error while following user: %s, please try again" % e)
        return

      print("follow user %s succesfully" % args[1])
    elif args[0] == '-t':
      self.db_cursor.execute("SELECT topicName FROM Topic WHERE topicName = '%s'" % args[1])

      if self.db_cursor.rowcount == 0:
        print("topic %s does not exist" % args[1])
        return

      try:
        self.db_cursor.execute("INSERT INTO UserFollowTopic(userName, topicName) VALUES ('%s', '%s')" % (self.username, args[1]))
        self.db.commit()
      except (MySQLdb.Error, MySQLdb.Warning) as e:
        self.db.rollback()
        print("error while following topic: %s, please try again" % e)
        return

      print("follow topic %s succesfully" % args[1])
    else:
      print("flag %s not available" % args[0])

  def help_follow(self):
    print('follow [-u | -t] [username | topic]')

  def do_logout(self, input):
    print('logging out...')
    return True

  def help_logout(self):
    print('exit the application')

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
