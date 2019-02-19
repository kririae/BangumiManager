import os
import sqlite3
import requests
from win32.win32crypt import CryptUnprotectData
from functools import wraps
import webbrowser
from bs4 import BeautifulSoup
import re
import requests


def is_login(func):
  @wraps(func)
  def wrapper(self, *args, **kwargs):
    if not self._is_login:
      raise BaseException("Please login first")
    else:
      return func(self, *args, **kwargs)
  return wrapper


class BangumiSession:

  _DOMAINS = ('http://bangumi.tv', 'http://bgm.tv', 'http://chii.in')
  _SUPPORT_BROWSER = ('chrome', 'firefox')

  def __init__(self, login=True, url='bgm.tv', browser_type='chrome'):
    self._url = 'http://' + self._convert_url(url)
    self._browser_type = browser_type
    self._cookies = self._get_cookies()
    self._session = requests.Session()
    self._session.cookies.update(self._cookies)
    self._session.headers.update({
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
    })
    self._userid, self._username = None, None
    # print(self._url in DOMAINS)
    if not self._url in self._DOMAINS:
      raise BaseException(
        "Url must be one of ('http://bangumi.tv', 'http://bgm.tv', 'http://chii.in')")
    if not browser_type in self._SUPPORT_BROWSER:
      raise BaseException(
        "Type must be one of ('chrome', 'firefox')")
    if login:
      if self._cookies.get('chii_auth') == None:
        raise BaseException("Login failed.")
      self._userid, self._username = self._get_name_from_html(
        self._get(self._url).text)
      self._gh = self._get_gh()
    print("init finished")

  def _change_rate_of_game(self, id, rate):
    print("qwq")
    data = { "rate": rate }
    self._post(
      f'{self._url}/subject/{str(id)}/rate.chii?gh={str(self._gh)}', data=data)

  def _convert_url(self, s):
    if s.startswith('https://'):
      s = s[8:]
    if s.startswith('http://'):
      s = s[7:]
    if s.endswith('/'):
      s = s[:-1]
    return s

  def _get_cookies(self):
    # Get cookie information from chrome
    if self._browser_type == 'chrome':
      username = os.environ.get('USERNAME')
      cookie_path = f'C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cookies'
      query = 'select name, encrypted_value from cookies where host_key=\'%s\' or host_key=\'%s\';' % (
        f'.{self._convert_url(self._url)}', self._convert_url(self._url))
      with sqlite3.connect(cookie_path) as conn:
        cu = conn.cursor()
        res = cu.execute(query).fetchall()
        cookies = {}
        for name, encrypted_value in res:
          cookies[name] = CryptUnprotectData(
            encrypted_value)[1].decode()
        return cookies

    if self._browser_type == 'firefox':
      username = os.environ.get('USERNAME')
      cookie_path = self._find_cookies_path_in_firefox(
        f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox", "storage.sqlite")
      query = 'select name, value from moz_cookies where host=\'.bgm.tv\' or host=\'bgm.tv\';'
      with sqlite3.connect(cookie_path) as conn:
        cu = conn.cursor()
        res = cu.execute(query).fetchall()
        cookies = {}
        for name, value in res:
          cookies[name] = value
        print(cookies)
        return cookies
        # 不知道火狐浏览器把会话级cookie存哪去了...这段先咕咕咕吧

  def _find_cookies_path_in_firefox(self, path, name):
    for root, dirs, files in os.walk(path):
      if name in files:
        return os.path.join(str(root), str(name))
    return -1

  def _get_name_from_html(self, text):
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('a', href=re.compile(r'/user/\w+'), class_="l")
    return node[0].get('href').split('/')[-1], node[0].get_text()

  def _get_gh_from_html(self, text):
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('a', href=re.compile(f'{self._url}/logout/\d+'))
    if len(node) == 0:
      raise BaseException("Html parse error.")
    return int(node[0].get('href').split('/')[-1])

  def _get_gh(self):
    rep = self._get(self._url)
    return self._get_gh_from_html(rep.text)

  @property
  def _is_login(self):
    self._get_cookies()
    return self._cookies.get('chii_auth') != None

  @is_login
  def _post(self, url, data):
    return self._session.post(url, data)

  @is_login
  def _get(self, url):
    ret = self._session.get(url)
    ret.encoding = 'utf-8'
    return ret


def main():
  b = BangumiSession()
  # b._change_rate_of_game(121971, 8)

if __name__ == '__main__':
  main()
