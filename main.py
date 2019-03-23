from cmd import Cmd

import pdb

class SocialNetworkPrompt(Cmd):

  login = False

  def do_login(self, input):
    self.login = True
    print("logged in successfully")

  def do_logout(self, input):
    print("logging out...")
    return True

  def help_logout(self):
    print('exit the application')

  def default(self, input):
    return self.do_help('')

  def precmd(self, line):
    pdb.set_trace()
    if not self.login:
      print('not login yet')

  do_EOF = do_logout
  help_EOF = help_logout

if __name__ == '__main__':
  SocialNetworkPrompt().cmdloop()
