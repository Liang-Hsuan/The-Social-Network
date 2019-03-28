from cmd import Cmd

import MySQLdb
import shlex
import json
import pdb

class SocialNetworkPrompt(Cmd):

  db = None
  db_cursor = None
  login = False
  username = ''

  def do_create(self, input):
    args = shlex.split(input)

    if len(args) != 4:
      print("number or arguments should be 4, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT * FROM User WHERE userName = \"%s\"" % args[0])

    if self.db_cursor.rowcount != 0:
      print("username %s has already been created, try another one" % args[0])
      return

    try:
      names = args[1].split(' ')

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

  def do_login(self, input):
    if self.login:
      print('Already logged in, please logout first')
      return

    self.db_cursor.execute("SELECT * FROM User WHERE userName = \"%s\"" % input)
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
    if not self.login:
      print('please log in first')
      return

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

  def do_logout(self, input):
    self.db_cursor.close()
    print('logging out...')

    return True

  def help_logout(self):
    print('exit the application')

  def preloop(self):
    with open('secret.json', 'r') as file:
      data = file.read()

    secret = json.loads(data)
    self.db = MySQLdb.connect(secret['host'], secret['user'], secret['password'], secret['database'])
    self.db_cursor = self.db.cursor()

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
