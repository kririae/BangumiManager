# by kririae
# 2019/02/19
import os
import requests
from functools import wraps
import re
import requests
import json
from bs4 import BeautifulSoup
import time
import math
import random
from PIL import Image
import pickle


def is_login(func):
  @wraps(func)
  def wrapper(self, *args, **kwargs):
    if not self._is_login:
      raise BaseException("Please login first")
    else:
      return func(self, *args, **kwargs)
  return wrapper

def init_data(func):
  @wraps(func)
  def wrapper(self, id, rating, tags, comment):
    return func(data = {
      "referer": "subject",
      "rating": rating,
      "interest": None,
      "tags": " ".join(tags),
      "comment": comment,
      "update": "保存"
    })
  return wrapper

class HTMLParseError(Exception): pass
class UrlError(Exception): pass
class LoginError(Exception): pass
class HttpError(Exception): pass

class BangumiSession:

  _DOMAINS = ('https://bangumi.tv', 'https://bgm.tv', 'https://chii.in')
  _SUPPORT_BROWSER = ('chrome', 'firefox')
  _API_URL = "https://api.bgm.tv"


  def __init__(self, login: bool = True, url: str = 'bgm.tv'):
    self._cache = os.getcwd() + '\\cache'
    if not os.path.exists(self._cache):
      os.mkdir(self._cache)
    self._f = open(f'{self._cache}\\tmp.pk', 'w')

    self._url = 'https://' + self._convert_url(url)
    if not self._url in self._DOMAINS:
      raise UrlError(
        "Url must be one of ('https://bangumi.tv', 'https://bgm.tv', 'https://chii.in')")
    self._cookies = self._get_cookies()
    self._session = requests.Session()
    self._session.headers.update({
      "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
    })

    self._userid = None
    self._username = None
    self._gh = None

    rep = self._get(self._url)
    rep.coding = 'utf-8'
    pickle.dump(rep.text, self._f)

    if login:
      captcha = self._get_captcha()
      with open(os.getcwd() + '\\cache\\captcha.gif', 'wb') as f:
        f.write(captcha.content)
      img = Image.open(os.getcwd() + '\\cache\\captcha.gif')
      img.show()
      self._userid, self._username = self._get_name_from_html(
        self._get(self._url).text)
      self._gh = self._get_gh()
    # print("init finished")

  def __del__(self):
    self._f.close()

  def _get_subject_information(self, id: str):
    ret = requests.get(f'{self._API_URL}/subject/{str(id)}')
    if ret.status_code != 200:
      raise HttpError("HTTP error. Failed to get game information")
    return json.loads(ret.text)

  def _get_user_information(self, id: str):
    ret = requests.get(f'{self._API_URL}/user/{str(id)}')
    if ret.status_code != 200:
      raise HttpError("HTTP error. Failed to get user information")
    return json.loads(ret.text)

  def _update_completion_degree(self, id: str, rate: str):
    data = {"referer": "subject", "submit": "更新", "watchedeps": rate}
    return self._post(f'{self._url}/subject/set/watched/{str(id)}', data=data)

  def _change_rate_of_subject(self, id: str, rate: int):
    data = {"rate": rate}
    return self._post(
      f'{self._url}/subject/{str(id)}/rate.chii?gh={str(self._gh)}', data=data)

  @init_data
  def _want_subject(self, **kwargs):
    data = kwargs["data"]
    data["interest"] = 1
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  @init_data
  def _finished_subject(self, **kwargs):
    data = kwargs["data"]
    data["interest"] = 2
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  @init_data
  def _doing_subject(self, **kwargs, ):
    data = kwargs["data"]
    data["interest"] = 3
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  @init_data
  def _pause_subject(self, **kwargs):
    data = kwargs["data"]
    data["interest"] = 4
    return self._post(
      f'{self._url}/subject/{str(id)}/interest/update?gh={self._gh}', data=data)

  @init_data
  def _stop_subject(self, **kwargs):
    data = kwargs["data"]
    data["interest"] = 5
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

  def _get_name_from_html(self, text: str) -> (str, str):
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('a', href=re.compile(r'/user/\w+'), class_="l")
    if len(node) == 0:
      raise HTMLParseError("Html parse error.")
    return node[0].get('href').split('/')[-1], node[0].get_text()

  def _get_gh_from_html(self, text: str) -> str:
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('a', href=re.compile(f'{self._url}/logout/\d+'))
    if len(node) == 0:
      raise HTMLParseError("Html parse error.")
    return node[0].get('href').split('/')[-1]

  def _get_formhash_from_html(self, text):
    soup = BeautifulSoup(text, 'html.parser')
    node = soup.find_all('input', attrs={"type": "hidden", "name": "formhash"})
    if len(node) == 0:
      raise HTMLParseError("Html parse error.")
    return node[0].get('value')

  def _get_captcha(self):
    time = math.floor(time.time() * 1000)
    randInt = 1 + math.floor(random.random() * 6)
    return self._session.get(f'{self._url}/signup/captcha?{str(time) + str(randInt)}')

  def _get_gh(self):
    rep = self._get(self._url)
    return self._get_gh_from_html(rep.text)

  # @property
  # def _is_login(self):
  #   # self._get_cookies()
  #   return self._cookies.get('chii_auth') != None

  # @is_login
  # def _post(self, url: str, data: list):
  #   return self._session.post(url, data)

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
