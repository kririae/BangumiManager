# by kririae
# 2019/02/19
import os
import sqlite3
import requests
from functools import wraps
import webbrowser
import re
import requests
import json
from bs4 import BeautifulSoup
from win32.win32crypt import CryptUnprotectData


def is_login(func):
  @wraps(func)
  def wrapper(self, *args, **kwargs):
    if not self._is_login:
      raise BaseException("Please login first")
    else:
      return func(self, *args, **kwargs)
  return wrapper


def type_check(func):
  @wraps(func)
  def wrapper(self, *args, **kwargs):
    # TODO...
    return func(self, *args, **kwargs)
  return wrapper


class BangumiSession:

  _DOMAINS = ('https://bangumi.tv', 'https://bgm.tv', 'https://chii.in')
  _SUPPORT_BROWSER = ('chrome', 'firefox')
  _API_URL = "https://api.bgm.tv"

  def __init__(self, login: bool = True, url: str = 'bgm.tv', browser_type: str = 'chrome'):
    self._url = 'https://' + self._convert_url(url)
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
        "Url must be one of ('https://bangumi.tv', 'https://bgm.tv', 'https://chii.in')")
    if not browser_type in self._SUPPORT_BROWSER:
      raise BaseException(
        "Type must be one of ('chrome', 'firefox')")
    if login:
      if self._cookies.get('chii_auth') == None:
        raise BaseException("Login failed.")
      self._userid, self._username = self._get_name_from_html(
        self._get(self._url).text)
      self._gh = self._get_gh()
    # print("init finished")

  def _get_subject_information(self, id: str):
    ret = requests.get(f'{self._API_URL}/subject/{str(id)}')
    if ret.status_code != 200:
      raise BaseException("HTTP error. Failed to get game information")
    return json.loads(ret.text)

  def _get_user_information(self, id: str):
    ret = requests.get(f'{self._API_URL}/user/{str(id)}')
    if ret.status_code != 200:
      raise BaseException("HTTP error. Failed to get user information")
    return json.loads(ret.text)

  def _update_completion_degree(self, id: str, rate: str):
    data = {"referer": "subject", "submit": "更新", "watchedeps": rate}
    return self._post(f'{self._url}/subject/set/watched/{str(id)}', data=data)

  def _change_rate_of_subject(self, id: str, rate: int):
    data = {"rate": rate}
    return self._post(
      f'{self._url}/subject/{str(id)}/rate.chii?gh={str(self._gh)}', data=data)

  def _want_subject(self, id: int, tags: list = [], comment: str = ""):
    data = {
      "referer": "subject",
      "interest": 1,
      "tags": " ".join(tags),
      "comment": comment,
      "update": "保存"
    }
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  def _finished_subject(self, id: int, rating: int, tags: list = [], comment: str = ""):
    data = {
      "referer": "subject",
      "rating": rating,
      "interest": 2,
      "tags": " ".join(tags),
      "comment": comment,
      "update": "保存"
    }
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  def _doing_subject(self, id: int, rating: int, tags: list = [], comment: str = "", ):
    data = {
      "referer": "subject",
      "rating": rating,
      "interest": 3,
      "tags": " ".join(tags),
      "comment": comment,
      "update": "保存"
    }
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  def _pause_subject(self, id: int, rating: int, tags: list = [], comment: str = ""):
    data = {
      "referer": "subject",
      "rating": rating,
      "interest": 4,
      "tags": " ".join(tags),
      "comment": comment,
      "update": "保存"
    }
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  def _stop_subject(self, id: int, rating: int, tags: list = [], comment: str = ""):
    data = {
      "referer": "subject",
      "rating": rating,
      "interest": 5,
      "tags": " ".join(tags),
      "comment": comment,
      "update": "保存"
    }
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  def _convert_url(self, s: 'str') -> 'str':
    if s.startswith('https://'):
      s = s[8:]
    if s.startswith('http://'):
      s = s[7:]
    if s.endswith('/'):
      s = s[:-1]
    return s

  def _get_cookies(self) -> dict:
    # Get cookie information from chrome
    username = os.environ.get('USERNAME')
    if self._browser_type == 'chrome':
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
      cookie_path = self._find_cookies_path_in_firefox(
        f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox", "storage.sqlite")
      query = 'select name, value from moz_cookies where host=\'.bgm.tv\' or host=\'bgm.tv\';'
      with sqlite3.connect(cookie_path) as conn:
        cu = conn.cursor()
        res = cu.execute(query).fetchall()
        cookies = {}
        for name, value in res:
          cookies[name] = value
        # print(cookies)
        return cookies
        # 不知道火狐浏览器把会话级cookie存哪去了...这段先咕咕咕吧

  def _find_cookies_path_in_firefox(self, path: str, name: str) -> str:
    for root, dirs, files in os.walk(path):
      if name in files:
        return os.path.join(str(root), str(name))
    return -1

  def _get_name_from_html(self, text: str) -> (str, str):
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('a', href=re.compile(r'/user/\w+'), class_="l")
    if len(node) == 0:
      raise BaseException("Html parse error.")
    return node[0].get('href').split('/')[-1], node[0].get_text()

  def _get_gh_from_html(self, text: str) -> str:
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('a', href=re.compile(f'{self._url}/logout/\d+'))
    if len(node) == 0:
      raise BaseException("Html parse error.")
    return node[0].get('href').split('/')[-1]

  def _get_gh(self):
    rep = self._get(self._url)
    return self._get_gh_from_html(rep.text)

  @property
  def _is_login(self):
    self._get_cookies()
    return self._cookies.get('chii_auth') != None

  @is_login
  def _post(self, url: str, data: list):
    return self._session.post(url, data)

  @is_login
  def _get(self, url: str):
    ret = self._session.get(url)
    ret.encoding = 'utf-8'
    return ret


def main():
  b = BangumiSession()
  # b._change_rate_of_game(121971, 8)
  # b._update_completion_degree(175404, 2)


if __name__ == '__main__':
  main()
