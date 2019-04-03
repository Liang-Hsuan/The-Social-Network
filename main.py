from cmd import Cmd
from datetime import date
from prettytable import PrettyTable

import MySQLdb
import shlex
import json
import pdb
import re

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
    print('topic [topic_name ("" if has space)] [parent_topic_name (optional; "" if has space)]\n' \
      'create a topic name and its optional parent topic')

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
      self.db_cursor.execute("INSERT INTO Posting(postID, userName) VALUES ((SELECT LAST_INSERT_ID()), '%s')" % self.username)

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
    print('post [content ("" if has space] [topics (separated by , and "" if has space)]\n' \
      'submit a post with given text content and topic(s)')

  def do_reply(self, input):
    args = shlex.split(input)

    if len(args) != 2:
      print("number or arguments should be 2, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT postID FROM Post WHERE postID = '%s'" % args[0])

    if self.db_cursor.rowcount == 0:
      print("post %s does not exist" % args[0])
      return

    try:
      self.db_cursor.execute("INSERT INTO Post(parentPostID, postText, createTime) VALUES ('%s',' %s', '%s')" % (args[0], args[1], str(date.today())))
      self.db_cursor.execute("INSERT INTO Posting(postID, userName) VALUES ((SELECT LAST_INSERT_ID()), '%s')" % self.username)
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while replying post: %s, please try again" % e)
      return

    print("reply to post %s with '%s' submitted successfully" % (args[0], args[1]))

  def help_reply(self):
    print('reply [post_id] [content ("" if has space)]\n' \
      'reply a response to a post with given post id and content text')

  def do_read(self, input):
    args = shlex.split(input)

    if len(args) != 1:
      print("number or arguments should be 1, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT postID FROM Post WHERE postID = '%s'" % args[0])

    if self.db_cursor.rowcount == 0:
      print("post %s does not exist" % args[0])
      return

    self.db_cursor.execute('SELECT postID, postText, likes, disliks, parentPostID, createTime, userName FROM Post INNER JOIN Posting USING (postID) ORDER BY createTime DESC')
    posts = self.db_cursor.fetchall()

    related_posts = list(filter(lambda x: SocialNetworkPrompt.__is_child(int(args[0]), 4, x[0], 0, posts), posts))

    table_header = ['post id', 'content', 'number of likes', 'number of dislikes', 'reply to post', 'date', 'user']

    SocialNetworkPrompt.__print_response(related_posts, table_header, int(args[0]), 4, 0)

    try:
      self.db_cursor.execute("INSERT INTO UserRead(userName, postID) VALUES ('%s', %s)" % (self.username, args[0]))
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while reading post: %s, please try again" % e)
      return

  def help_read(self):
    print('read [post_id]\n' \
      'read the details of the post with given post ID')

  @staticmethod
  def __is_child(parent_id, parent_id_field_index, id, id_field_index, rows, row = None):
    if row is None:
      row = filter(lambda x: x[id_field_index] == id, rows)[0]
      return SocialNetworkPrompt.__is_child(parent_id, parent_id_field_index, id, id_field_index, rows, row)

    if row[parent_id_field_index] is None:
      return row[id_field_index] == parent_id

    row = filter(lambda x: x[id_field_index] == row[parent_id_field_index], rows)[0]
    return SocialNetworkPrompt.__is_child(parent_id, parent_id_field_index, id, id_field_index, rows, row)

  @staticmethod
  def __print_response(posts, table_header, main_post_id, parent_id_field_index, id_field_index, main_post = None, level = 0, done = []):
    if main_post is None:
      main_post = filter(lambda x: x[id_field_index] == main_post_id, posts)[0]

      t = PrettyTable(table_header)
      t.add_row(main_post)
      print(t)

      posts.remove(main_post)

      return SocialNetworkPrompt.__print_response(posts, table_header, main_post_id, parent_id_field_index, id_field_index, main_post, 1)

    for post in posts:
      if (post[parent_id_field_index] == main_post_id) and (post[id_field_index] not in done):
        print('\t' * level + '|\n' + '\t' * level + '|\n')

        t = PrettyTable(table_header)
        t.add_row(post)
        table_string = re.sub('\n', '\n' + '\t' * level, str(t))
        print('\t' * level + table_string)

        done.append(post[id_field_index])

        if len(posts) > 0:
          SocialNetworkPrompt.__print_response(posts, table_header, post[id_field_index], parent_id_field_index, id_field_index, post, level + 1, done)

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

  def do_group(self, input):
    args = shlex.split(input)

    if len(args) != 1:
      print("number or arguments should be 1, %d given" % len(args))
      return

    try:
      self.db_cursor.execute("INSERT INTO Grouping (groupName) VALUES ('%s')" % args[0])
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while creating group: %s, please try again" % e)
      return

    print("%s group created successfully" % args[0])

  def help_group(self):
    print('group [groupname ("" if has space)]\ncreate a group with the given group name')

  def do_join(self, input):
    args = shlex.split(input)

    if len(args) != 1:
      print("number or arguments should be 1, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT groupID FROM Grouping WHERE groupID = %s" % args[0])

    if self.db_cursor.rowcount == 0:
      print("groupID %s cannot be found" % args[0])
      return

    try:
      self.db_cursor.execute("INSERT INTO GroupMember(userName, groupID) VALUES ('%s', %s)" % (self.username, args[0]))
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while joining group: %s, please try again" % e)
      return

    print("%s joined group successfully" % args[0])

  def help_join(self):
    print('join [groupID]\njoin to the group with the given group ID')

  def do_list(self, input):
    args = shlex.split(input)

    if not (0 < len(args) < 3):
      print("number or arguments should be 1 or 2, %d given" % len(args))
      return

    has_only_followed_flag = (len(args) == 2) and (args[1] == '--followed')

    if args[0] == '-p':
      self.db_cursor.execute('SELECT postID, postText, createTime FROM Post WHERE parentPostID IS NULL ORDER BY createTime DESC')
      posts = self.db_cursor.fetchall()

      t = PrettyTable(['post id', 'content', 'date'])
      for post in posts:
        t.add_row(post)

      print(t)

    elif args[0] == '-t':
      query = ("SELECT topicName, parentTopicName FROM UserFollowTopic LEFT JOIN ParentTopic USING (topicName) where userName = '%s'" % self.username) if has_only_followed_flag \
        else 'SELECT topicName, parentTopicName FROM Topic LEFT JOIN ParentTopic USING (topicName)'
      self.db_cursor.execute(query)
      topics = self.db_cursor.fetchall()

      t = PrettyTable(['Topic', 'Parent Topic'])
      for topic in topics:
        t.add_row(topic)

      print(t)

    elif args[0] == '-u':
      query = ("SELECT followee FROM Follow WHERE follower = '%s'" % self.username) if has_only_followed_flag else 'SELECT userName FROM User'
      self.db_cursor.execute(query)
      users = self.db_cursor.fetchall()

      t = PrettyTable(['User Name'])
      for user in users:
        t.add_row(user)

      print(t)

    elif args[0] == '-g':
      query = ("SELECT groupID, groupName FROM Grouping JOIN GroupMember USING (groupID) WHERE userName = '%s'" % self.username) if has_only_followed_flag \
        else 'SELECT groupID, groupName FROM Grouping'
      self.db_cursor.execute(query)
      groups = self.db_cursor.fetchall()

      t = PrettyTable(['Group ID', 'Group Name'])
      for group in groups:
        t.add_row(group)

      print(t)

    else:
      print("flag %s not available" % args[0])

  def help_list(self):
    print('list [-p | -t | -u | -g] [--followed (optional)]\n' \
      'list all the posts or topics or users or groups\n' \
      'list all the posts or topics or users or groups followed by the user if --followed flag is provided')

  def do_show(self, input):
    args = shlex.split(input)

    if len(args) != 2:
      print("number or arguments should be 2, %d given" % len(args))
      return

    if args[0] == '-u':
      self.db_cursor.execute("SELECT * FROM Follow WHERE followee = '%s' and follower = '%s'" % (args[1], self.username))

      if self.db_cursor.rowcount == 0:
        print("you did not follow user %s" % args[1])
        return

      self.db_cursor.execute("SELECT Post.postID, Post.postText, Post.createTime FROM Post JOIN Posting ON Post.postID = Posting.postID " \
        "WHERE Posting.userName = '%s' AND Post.postID NOT IN (SELECT postID FROM UserRead WHERE userName = '%s') AND Post.parentPostID IS NULL " \
        "ORDER BY createTime DESC" % (args[1], self.username))
      posts = self.db_cursor.fetchall()

      t = PrettyTable(['post id', 'content', 'date'])
      for post in posts:
        t.add_row(post)

      print(t)

    elif args[0] == '-t':
      self.db_cursor.execute("SELECT * FROM UserFollowTopic WHERE userName = '%s' AND topicName = '%s'" % (self.username, args[1]))

      if self.db_cursor.rowcount == 0:
        print("you did not follow topic %s" % args[1])
        return

      self.db_cursor.execute("SELECT Post.postID, Post.postText, Post.createTime FROM Post JOIN PostTagTopic ON Post.postID = PostTagTopic.postID " \
        "WHERE PostTagTopic.topicName = '%s' AND Post.postID NOT IN (SELECT postID FROM UserRead WHERE userName = '%s' AND Post.parentPostID IS NULL) " \
        "ORDER BY createTime DESC" % (args[1], self.username))
      posts = self.db_cursor.fetchall()

      t = PrettyTable(['post id', 'content', 'date'])
      for post in posts:
        t.add_row(post)

      print(t)
    else:
      print("flag %s not available" % args[0])

  def help_show(self):
    print('show [-u | -t] [username]\nshow all the posts by followed users or topics')

  def do_logout(self, input):
    print('logging out...')
    return True

  def help_logout(self):
    print('exit the application')

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
