from cmd import Cmd

import MySQLdb
import json
import pdb

class SocialNetworkPrompt(Cmd):

  db = None
  login = False

  def do_login(self, input):
    with open('secret.json', 'r') as file:
      data = file.read()

    secret = json.loads(data)
    db_connector = MySQLdb.connect(secret['host'], secret['user'], secret['password'], secret['database'])
    self.db = db_connector.cursor()

    self.login = True
    print('logged in successfully')

  def do_logout(self, input):
    if self.db is not None:
      self.db.close()

    print('logging out...')
    return True

  def help_logout(self):
    print('exit the application')

  def default(self, input):
    return self.do_help('')

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
