from cmd import Cmd

import MySQLdb
import json
import pdb

class SocialNetworkPrompt(Cmd):

  db = None
  login = False
  username = ''

  def do_create(self, input):
    

  def do_login(self, input):
    if self.login:
      print('Already logged in, please logout first')
      return

    self.db.execute("SELECT * FROM User WHERE userName = \"%s\"" % input)
    row = self.db.fetchone()

    if self.db.rowcount == 0:
      print('no username found')
      return

    self.username = input
    self.login = True

    print('logged in successfully')

  def do_logout(self, input):
    self.db.close()
    print('logging out...')

    return True

  def help_logout(self):
    print('exit the application')

  def preloop(self):
    with open('secret.json', 'r') as file:
      data = file.read()

    secret = json.loads(data)
    db_connector = MySQLdb.connect(secret['host'], secret['user'], secret['password'], secret['database'])

    self.db = db_connector.cursor()

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
