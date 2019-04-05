from cmd import Cmd
from datetime import date
from prettytable import PrettyTable

import MySQLdb
import shlex
import json
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
    print('create [username] [name ("firstName lastName")] [birthday (YYYY-MM-DD)] [gender (m/f)]\n' \
      'create a new user with given user name, first name and last name, birthday, and gender')

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
    print('post [content ("" if has space)] [topics (separated by comma; "" if has space)]\n' \
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
      'reply a response to a post with given post ID and content text')

  def do_like(self, input):
    args = shlex.split(input)

    if len(args) != 1:
      print("number or arguments should be 1, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT postID FROM Post WHERE postID = '%s'" % args[0])

    if self.db_cursor.rowcount == 0:
      print("post %s does not exist" % args[0])
      return

    try:
      self.db_cursor.execute("UPDATE Post SET likes = likes + 1 WHERE postID = %s" % args[0])
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while liking post: %s, please try again" % e)
      return

    print("like post %s successfully" % args[0])

  def help_like(self):
    print('like [post_id]\n' \
      'like a post with the given post ID to increase its likes number')

  def do_dislike(self, input):
    args = shlex.split(input)

    if len(args) != 1:
      print("number or arguments should be 1, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT postID FROM Post WHERE postID = '%s'" % args[0])

    if self.db_cursor.rowcount == 0:
      print("post %s does not exist" % args[0])
      return

    try:
      self.db_cursor.execute("UPDATE Post SET dislikes = dislikes + 1 WHERE postID = %s" % args[0])
      self.db.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
      self.db.rollback()
      print("error while disliking post: %s, please try again" % e)
      return

    print("dislike post %s successfully" % args[0])

  def help_dislike(self):
    print('dislike [post_id]\n' \
      'dislike a post with the given post ID to increase its dislike number')

  def do_read(self, input):
    args = shlex.split(input)

    if len(args) != 1:
      print("number or arguments should be 1, %d given" % len(args))
      return

    self.db_cursor.execute("SELECT postID FROM Post WHERE postID = '%s'" % args[0])

    if self.db_cursor.rowcount == 0:
      print("post %s does not exist" % args[0])
      return

    self.db_cursor.execute('SELECT postID, postText, likes, dislikes, parentPostID, createTime, GROUP_CONCAT(PostTagTopic.topicName SEPARATOR \', \') AS topics, userName ' \
      'FROM Post LEFT JOIN Posting USING (postID) LEFT JOIN PostTagTopic USING(postID) GROUP BY Post.postID ORDER BY createTime DESC')

    posts = self.db_cursor.fetchall()

    related_posts = list(filter(lambda x: SocialNetworkPrompt.__is_child(int(args[0]), 4, x[0], 0, posts), posts))
    table_header = ['post id', 'content', 'likes', 'dislikes', 'reply to post', 'date', 'topics', 'user']
    SocialNetworkPrompt.__print_response(related_posts, table_header, int(args[0]), 4, 0)

    self.db_cursor.execute("SELECT * FROM UserRead WHERE userName = '%s' AND postID = %s" % (self.username, args[0]))
    if self.db_cursor.rowcount == 0:
      try:
        self.db_cursor.execute("INSERT INTO UserRead(userName, postID) VALUES ('%s', %s)" % (self.username, args[0]))
        self.db.commit()
      except (MySQLdb.Error, MySQLdb.Warning) as e:
        self.db.rollback()
        print("error while reading post: %s, please try again" % e)
        return

  def help_read(self):
    print('read [post_id]\n' \
      'read the details of a post with given post ID')

  @staticmethod
  def __is_child(parent_id, parent_id_field_index, id, id_field_index, rows, row = None):
    if row is None:
      row = filter(lambda x: x[id_field_index] == id, rows)[0]
      return SocialNetworkPrompt.__is_child(parent_id, parent_id_field_index, id, id_field_index, rows, row)

    if (row[parent_id_field_index] is None) or (row[id_field_index] == parent_id):
      return row[id_field_index] == parent_id

    row = filter(lambda x: x[id_field_index] == row[parent_id_field_index], rows)[0]
    return SocialNetworkPrompt.__is_child(parent_id, parent_id_field_index, id, id_field_index, rows, row)

  @staticmethod
  def __print_response(posts, table_header, main_post_id, parent_id_field_index, id_field_index, main_post = None, level = 0):
    if main_post is None:
      main_post = filter(lambda x: x[id_field_index] == main_post_id, posts)[0]

      t = PrettyTable(table_header)
      t.add_row(main_post)
      print(t)

      posts.remove(main_post)

      return SocialNetworkPrompt.__print_response(posts, table_header, main_post_id, parent_id_field_index, id_field_index, main_post, 1)

    for post in posts:
      if post[parent_id_field_index] == main_post_id:
        print('\t' * level + '|\n' + '\t' * level + '| replied from ' + post[-1] + '\n')

        t = PrettyTable(table_header)
        t.add_row(post)
        table_string = re.sub('\n', '\n' + '\t' * level, str(t))
        print('\t' * level + table_string)

        posts_copy = posts[:]
        posts_copy.remove(post)

        if len(posts) > 0:
          SocialNetworkPrompt.__print_response(posts_copy, table_header, post[id_field_index], parent_id_field_index, id_field_index, post, level + 1)

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
    print('login [username]\n' \
      'log in to the account of the given user name')

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
    print('follow [-u | -t] [username | topic_name]\n' \
      'follow a user or a topic')

  def do_unfollow(self, input):
    args = shlex.split(input)

    if len(args) != 2:
      print("number or arguments should be 2, %d given" % len(args))
      return

    if args[0] == '-u':
      if self.username == args[1]:
        print('cannot unfollow yourself')
        return

      self.db_cursor.execute("SELECT * FROM User WHERE userName = '%s'" % args[1])

      if self.db_cursor.rowcount == 0:
        print("username %s does not exist" % args[1])
        return

      try:
        self.db_cursor.execute("DELETE FROM Follow WHERE followee = '%s' AND follower = '%s'" % (args[1], self.username))
        self.db.commit()
      except (MySQLdb.Error, MySQLdb.Warning) as e:
        self.db.rollback()
        print("error while unfollowing user: %s, please try again" % e)
        return

      print("unfollow user %s succesfully" % args[1])
    elif args[0] == '-t':
      self.db_cursor.execute("SELECT topicName FROM Topic WHERE topicName = '%s'" % args[1])

      if self.db_cursor.rowcount == 0:
        print("topic %s does not exist" % args[1])
        return

      try:
        self.db_cursor.execute("DELETE FROM UserFollowTopic WHERE userName = '%s' AND topicName = '%s'" % (self.username, args[1]))
        self.db.commit()
      except (MySQLdb.Error, MySQLdb.Warning) as e:
        self.db.rollback()
        print("error while unfollowing topic: %s, please try again" % e)
        return

      print("unfollow topic %s succesfully" % args[1])
    else:
      print("flag %s not available" % args[0])

  def help_unfollow(self):
    print('unfollow [-u | -t] [username | topic_name]\n' \
      'unfollow a user or a topic')

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
    print('group [groupname ("" if has space)]\n' \
      'create a group with the given group name')

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
    print('join [groupID]\n' \
      'join to a group with the given group ID')

  def do_list(self, input):
    args = shlex.split(input)

    if not (0 < len(args) < 3):
      print("number or arguments should be 1 or 2, %d given" % len(args))
      return

    has_only_followed_flag = (len(args) == 2) and (args[1] == '--followed')

    if args[0] == '-p':
      query = ("SELECT postID, postText, createTime, GROUP_CONCAT(PostTagTopic.topicName SEPARATOR ', ') AS topics, userName FROM Post " \
        "INNER JOIN Posting USING (postID) " \
        "LEFT JOIN PostTagTopic USING (postID) " \
        "INNER JOIN Follow ON Posting.userName = Follow.followee " \
        "WHERE parentPostID IS NULL AND Posting.userName IN (SELECT followee FROM Follow WHERE follower = '%s') " \
        "GROUP BY Post.postID ORDER BY createTime DESC" % self.username) if has_only_followed_flag \
      else 'SELECT postID, postText, createTime, GROUP_CONCAT(PostTagTopic.topicName SEPARATOR \', \') AS topics, userName FROM Post ' \
        'INNER JOIN Posting USING (postID) ' \
        'LEFT JOIN PostTagTopic USING (postID) ' \
        'WHERE parentPostID IS NULL ' \
        'GROUP BY Post.postID ORDER BY createTime DESC'
      self.db_cursor.execute(query)
      posts = set(self.db_cursor.fetchall())

      if has_only_followed_flag:
        self.db_cursor.execute("SELECT topicName FROM UserFollowTopic WHERE userName = '%s'" % self.username)
        topics_followed = self.db_cursor.fetchall()

        for topic in topics_followed:
          posts_with_topic = self.__get_posts_from_topic(topic[0])
          posts.update(posts_with_topic)

      t = PrettyTable(['post id', 'content', 'date', 'topics', 'user'])
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
      query = ("SELECT userName, CONCAT(firstName, ' ', lastName) AS fullName, birthDay, gender FROM User INNER JOIN Follow ON User.userName = Follow.followee WHERE follower = '%s'" % self.username) if has_only_followed_flag \
        else 'SELECT userName, CONCAT(firstName, \' \', lastName) AS fullName, birthDay, gender FROM User'
      self.db_cursor.execute(query)
      users = self.db_cursor.fetchall()

      t = PrettyTable(['User', 'Name', 'Birthday', 'Gender'])
      for user in users:
        t.add_row(user)

      print(t)

    elif args[0] == '-g':
      query = ("SELECT groupID, groupName, COUNT(userName) AS members FROM Grouping INNER JOIN GroupMember USING (groupID) WHERE userName = '%s' GROUP BY groupID" % self.username) if has_only_followed_flag \
        else 'SELECT groupID, groupName, COUNT(userName) AS members FROM Grouping LEFT JOIN GroupMember USING (groupID) GROUP BY groupID'
      self.db_cursor.execute(query)
      groups = self.db_cursor.fetchall()

      t = PrettyTable(['Group ID', 'Group Name', 'Members Number'])
      for group in groups:
        t.add_row(group)

      print(t)

    else:
      print("flag %s not available" % args[0])

  def help_list(self):
    print('list [-p | -t | -u | -g] [--followed (optional)]\n' \
      'list all the posts or topics or users or groups\n' \
      'if --followed flag is provided then only show the followed posts or topics or users or groups\n' \
      'followed posts will show all the posts from the users or contain the topics you follow')

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

      self.db_cursor.execute("SELECT Post.postID, Post.postText, Post.createTime, GROUP_CONCAT(PostTagTopic.topicName SEPARATOR ', ') AS topics, userName FROM Post " \
        "INNER JOIN Posting USING (postID) " \
        "LEFT JOIN PostTagTopic USING (postID) " \
        "WHERE Posting.userName = '%s' AND Post.postID NOT IN (SELECT postID FROM UserRead WHERE userName = '%s') AND Post.parentPostID IS NULL " \
        "ORDER BY createTime DESC" % (args[1], self.username))
      posts = self.db_cursor.fetchall()

      t = PrettyTable(['post id', 'content', 'date', 'topics', 'user'])
      for post in posts:
        t.add_row(post)

      print(t)

    elif args[0] == '-t':
      self.db_cursor.execute("SELECT * FROM UserFollowTopic WHERE userName = '%s' AND topicName = '%s'" % (self.username, args[1]))

      if self.db_cursor.rowcount == 0:
        print("you did not follow topic %s" % args[1])
        return

      posts = self.__get_posts_from_topic(args[1])

      t = PrettyTable(['post id', 'content', 'date', 'topics', 'user'])
      for post in posts:
        t.add_row(post)

      print(t)
    else:
      print("flag %s not available" % args[0])

  def help_show(self):
    print('show [-u | -t] [username | topic_name] [--unread (optional)]\n' \
      'show all the new posts from followed user or topic since last read\n' \
      'if --unread flag is provided then show all the unread posts from followed user or topic')

  def __get_posts_from_topic(self, topic_name):
    self.db_cursor.execute("SELECT Post.postID, Post.postText, Post.createTime, GROUP_CONCAT(PostTagTopic.topicName SEPARATOR ', ') AS topics, userName FROM Post " \
        "INNER JOIN Posting USING (postID) " \
        "LEFT JOIN PostTagTopic USING (postID) " \
        "WHERE Post.postID NOT IN (SELECT postID FROM UserRead WHERE userName = '%s') AND Post.parentPostID IS NULL " \
        "GROUP BY Post.postID ORDER BY createTime DESC" % self.username)
    posts = self.db_cursor.fetchall()

    self.db_cursor.execute('SELECT topicName, parentTopicName FROM Topic LEFT JOIN ParentTopic USING (topicName)')
    topics = self.db_cursor.fetchall()

    filtered_topics = filter(lambda x: SocialNetworkPrompt.__is_child(topic_name, 1, x[0], 0, topics), topics)
    related_topics = map(lambda x: x[0], filtered_topics)
    related_posts = []
    for post in posts:
      if post[3] is None:
         continue
      post_topics = post[3].split(', ')
      if any(x for x in related_topics if x in post_topics):
        related_posts.append(post)

    return related_posts

  def do_logout(self, input):
    print('logging out...')
    return True

  def help_logout(self):
    print('exit the application')

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
