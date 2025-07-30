import pytest
from pathlib import Path
from json import loads
from jsurl import URL


class ValidCase:

  def __init__(self, params: dict):
    self.url: str = params['url']
    self.description: str = params['description']
    self.protocol: str = params['expected']['protocol']
    self.hostname: str = params['expected']['hostname']
    self.host: str = params['expected']['host']
    self.port: str = params['expected']['port']
    self.pathname: str = params['expected']['pathname']
    self.search: str = params['expected']['search']
    self.hash: str = params['expected']['hash']
    self.username: str = params['expected']['username']
    self.password: str = params['expected']['password']
    self.origin: str = params['expected']['origin']
    self.href: str = params['expected']['href']


class InvalidCase:

  def __init__(self, params: dict):
    self.url: str = params['url']
    self.description: str = params['description']


def load_cases():
  file = Path(__file__).parent / 'cases.json'

  data: dict = loads(file.read_text())

  valid = data['validURLs']
  invalid = data['invalidURLs']

  valid_cases = [ValidCase(params) for params in valid]
  invalid_cases = [InvalidCase(params) for params in invalid]

  return valid_cases + invalid_cases


@pytest.mark.parametrize("case", load_cases(), ids=lambda case: case.description)
def test_parse_urls(case: ValidCase | InvalidCase):

  if isinstance(case, ValidCase):
    url = URL(case.url)

    assert url.protocol == case.protocol
    assert url.hostname == case.hostname
    assert url.host == case.host
    assert url.port == case.port
    assert url.pathname == case.pathname
    assert url.search == case.search
    assert url.hash == case.hash
    assert url.username == case.username
    assert url.password == case.password
    assert url.origin == case.origin
    assert url.href == case.href

  else:
    with pytest.raises(Exception):
      URL(case.url)


def test_modify_url():
  url = URL('https://example.com:8080/')
  copy = URL(url)

  assert url == copy
  assert url is not copy

  url.protocol = 'http'

  assert url.protocol == 'http:'
  assert url.href == 'http://example.com:8080/'
  assert url.origin == 'http://example.com:8080'
  assert copy.protocol == 'https:'
  assert url != copy

  url.protocol = 'rtsp:'

  assert url.protocol == 'rtsp:'
  assert url.href == 'rtsp://example.com:8080/'
  assert url.origin == 'rtsp://example.com:8080'

  url.username = 'user'

  assert url.username == 'user'
  assert url.href == 'rtsp://user@example.com:8080/'
  assert url.origin == 'rtsp://example.com:8080'

  url.password = 'password'
  assert url.password == 'password'
  assert url.href == 'rtsp://user:password@example.com:8080/'
  assert url.origin == 'rtsp://example.com:8080'

  url.hostname = 'localhost'
  assert url.hostname == 'localhost'
  assert url.href == 'rtsp://user:password@localhost:8080/'
  assert url.origin == 'rtsp://localhost:8080'
  assert url.host == 'localhost:8080'

  url.port = '80'
  assert url.port == '80'
  assert url.href == 'rtsp://user:password@localhost:80/'
  assert url.origin == 'rtsp://localhost:80'
  assert url.host == 'localhost:80'

  url.host = 'example.com'
  assert url.host == 'example.com'
  assert url.href == 'rtsp://user:password@example.com/'
  assert url.origin == 'rtsp://example.com'
  assert url.hostname == 'example.com'
  assert url.port is None

  url.host = 'example.com:8080'
  assert url.host == 'example.com:8080'
  assert url.href == 'rtsp://user:password@example.com:8080/'
  assert url.origin == 'rtsp://example.com:8080'
  assert url.hostname == 'example.com'
  assert url.port == '8080'

  with pytest.raises(ValueError):
    url.host = 'localhost:8080:80'

  assert url.host == 'example.com:8080'
  assert url.hostname == 'example.com'
  assert url.port == '8080'
  assert url.href == 'rtsp://user:password@example.com:8080/'

  with pytest.raises(ValueError):
    url.host = 'localhost:-100'

  assert url.host == 'example.com:8080'
  assert url.hostname == 'example.com'
  assert url.port == '8080'
  assert url.href == 'rtsp://user:password@example.com:8080/'

  with pytest.raises(ValueError):
    url.host = 'localhost:1000000'

  assert url.host == 'example.com:8080'
  assert url.hostname == 'example.com'
  assert url.port == '8080'
  assert url.href == 'rtsp://user:password@example.com:8080/'
