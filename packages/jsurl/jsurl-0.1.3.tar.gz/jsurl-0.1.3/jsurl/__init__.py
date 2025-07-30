from collections.abc import MutableMapping
from typing import Iterable
from urllib.parse import quote as qt_urllib, unquote as uq_urllib


def _parse_query_item(item: str) -> tuple[str, str | None]:
  if '=' in item:
    key, value = item.split('=', 1)
    return key, _unquote(value)

  return item, None


def _unquote(value: str | None) -> str | None:
  if value is None:
    return None

  return uq_urllib(value, encoding='utf-8', errors='replace')


def _quote(value: str) -> str:
  return qt_urllib(value, encoding='utf-8', errors='replace', safe='')


class URLSearchParams(MutableMapping[str, list[str | None]]):
  __slots__ = ('_params', '_keys')

  def __init__(self, params: Iterable[tuple[str, str | None]]):
    self._params = [*params]
    self._keys = {k for k, _ in self._params}

  @classmethod
  def from_string(cls, query: str) -> 'URLSearchParams':
    query = query.lstrip('?')

    return cls(_parse_query_item(item) for item in query.split('&'))

  def __contains__(self, item: str) -> bool:
    return item in self._keys

  def get(self, key: str) -> str | None:
    for k, v in self._params:
      if k == key:
        return _unquote(v)

    return None

  def get_all(self, key: str) -> list[str | None]:
    return [_unquote(v) for k, v in self._params if k == key]

  def append(self, key: str, value: str | None) -> None:
    self._params.append((key, _unquote(value)))
    self._keys.add(key)

  def set(self, key: str, value: str | None) -> None:
    self._params = [(k, v) for k, v in self._params if k != key]
    self._params.append((key, _unquote(value)))
    self._keys.add(key)

  def delete(self, key: str) -> None:
    self._params = [(k, v) for k, v in self._params if k != key]
    self._keys.discard(key)

  def __iter__(self) -> Iterable[str]:
    yield from self._keys

  def __getitem__(self, key: str) -> list[str | None]:
    return self.get_all(key)

  def __setitem__(self, key: str, value: str | None) -> None:
    self.set(key, value)

  def __delitem__(self, key: str) -> None:
    self.delete(key)

  def __len__(self) -> int:
    return len(self._keys)

  def __str__(self) -> str:
    return '&'.join(
      _quote(k) if v is None else f"{_quote(k)}={_quote(v)}" for k,
      v in self._params
    )

  def __bool__(self) -> bool:
    return bool(self._params)

  def __repr__(self) -> str:
    return f"URLSearchParams.from_string({repr(str(self))})"


class URL:
  __slots__ = ('_params',
              )

  def __init__(self, url: 'str | URL'):
    self._params: tuple[
        str,  # protocol
        str | None,  # username
        str | None,  # password
        str | None,  # hostname
        str | None,  # port
        str | None,  # pathname
        str | None,  # hash
        URLSearchParams | None,  # search params
    ] = (
        '',
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )

    if isinstance(url, URL):
      self._params = url._params
    elif isinstance(url, str):
      self._parse_string(url)

  def _parse_string(self, url: str):
    scheme, *latter = url.split(':', 1)

    if not scheme:
      raise ValueError(f"Invalid URL: {repr(url)}")

    if not latter:
      raise ValueError(f"Invalid URL: {repr(url)}")

    if latter[0].startswith('//'):  # https://example.com/...
      nl, *path = latter[0][2:].split('/', 1)

      if '?' in nl or '#' in nl:
        if path:
          raise ValueError(f"Invalid URL: {repr(url)}")

        split = min(nl.index('?'), nl.index('#'))
        nl, path = nl[:split], [nl[split:]]

      a, *b = nl.split('@', 1)

      if b:  # https://authenticate@example.com/...
        username, *pw = a.split(':', 1)
        password = pw[0] if pw else None
        a = b[0]
      else:
        username, password = None, None

      if a.startswith('['):  # https://[::1]:8080/...
        if ']:' not in a and not a.endswith(']'):
          raise ValueError(f"Invalid URL: {repr(url)}")

        h, *p = a.split(']:', 1)
        hostname = h if h.endswith(']') else f'{h}]'
        port = p[0] if p else None

      else:  # https://example.com:8080/...
        if a.count(':') > 1:
          raise ValueError(f"Invalid URL: {repr(url)}")

        hostname, *p = a.split(':', 1)
        port = p[0] if p else None

        if port is not None and not (0 <= int(port) < 65536):
          raise ValueError(f"Invalid URL: {repr(url)}")

      path = f'/{path[0]}' if path else '/'

    elif latter[0].startswith('/'):
      raise ValueError(f"Invalid URL: {repr(url)}")

    else:  # javascript:...
      username, password, hostname, port = None, None, None, None
      path = latter[0]

    pathname, *params = path.split('?', 1)

    if params:
      search, *hash_ = params[0].split('#')

      if hash_[1:]:
        raise ValueError(f"Invalid URL: {repr(url)}")

      hash_ = hash_[0] if hash_ else None
    else:
      pathname, *fragment = path.split('#')

      if fragment[1:]:
        raise ValueError(f"Invalid URL: {repr(url)}")

      search, hash_ = None, fragment[0] if fragment else None

    self._params = (
      scheme,
      username,
      password,
      hostname,
      port,
      pathname,
      hash_,
      URLSearchParams.from_string(search) if search else None,
    )

  @property
  def protocol(self) -> str:
    proto = self._params[0]
    if proto is None or proto.endswith(':'):
      return proto

    return f"{proto}:"

  @protocol.setter
  def protocol(self, protocol: str) -> None:
    if protocol.endswith(':'):
      protocol = protocol[:-1]

    self._params = (protocol, *self._params[1:])

  @property
  def username(self) -> str | None:
    return self._params[1]

  @username.setter
  def username(self, username: str) -> None:
    self._params = (self._params[0], username, *self._params[2:])

  @property
  def password(self) -> str | None:
    return self._params[2]

  @password.setter
  def password(self, password: str) -> None:
    self._params = (self._params[0], self._params[1], password, *self._params[3:])

  @property
  def hostname(self) -> str | None:
    return self._params[3]

  @hostname.setter
  def hostname(self, hostname: str) -> None:
    self._params = (self._params[0], *self._params[1:3], hostname, *self._params[4:])

  @property
  def port(self) -> str | None:
    return self._params[4]

  @port.setter
  def port(self, port: str | int | None) -> None:
    if port is not None:
      port = str(port)

    self._params = (self._params[0], *self._params[1:4], port, *self._params[5:])

  @property
  def pathname(self) -> str | None:
    return self._params[5]

  @pathname.setter
  def pathname(self, pathname: str) -> None:
    self._params = (self._params[0], *self._params[1:5], pathname, *self._params[6:])

  @property
  def search(self) -> str | None:
    params = self._params[7]
    return f"?{params}" if self._params[7] else None

  @search.setter
  def search(self, search: str) -> None:
    search_params = URLSearchParams.from_string(search)
    self._params = (
      self._params[0],
      *self._params[1:7],
      search_params,
    )

  @property
  def hash(self) -> str | None:
    return f"#{self._params[6]}" if self._params[6] else None

  @hash.setter
  def hash(self, hash_: str) -> None:
    if hash_.startswith('#'):
      hash_ = hash_[1:]

    self._params = (self._params[0], *self._params[1:6], hash_, self._params[7])

  @property
  def search_params(self) -> URLSearchParams:
    params = self._params[7]

    if params is None:
      params = URLSearchParams([])
      self._params = (self._params[0], *self._params[1:7], params)

    return params

  @search_params.setter
  def search_params(self, search_params: URLSearchParams) -> None:
    self._params = (self._params[0], *self._params[1:7], search_params)

  @property
  def host(self) -> str | None:
    if self.hostname and self.port:
      return f"{self.hostname}:{self.port}"

    return self.hostname

  @host.setter
  def host(self, host: str) -> None:
    if ':' in host:
      if host.count(':') > 1:
        raise ValueError(f"Invalid Host: {repr(host)}")

      hostname, port = host.split(':', 1)

      try:
        if not (0 <= int(port) < 65536):
          raise ValueError(f"Invalid Host: {repr(host)}")
      except ValueError:
        raise ValueError(f"Invalid Host: {repr(host)}") from None

      self.hostname = hostname
      self.port = port
    else:
      self.hostname = host
      self.port = None

  @property
  def origin(self) -> str:
    host = self.host
    return f"{self.protocol}//{self.host}" if self.host is not None else self.protocol

  @property
  def href(self) -> str:
    url = self.protocol

    if self.hostname is not None:
      url += '//'

    if self.username:
      url += f"{self.username}"

      if self.password is not None:
        url += f":{self.password}"

      url += '@'

    if self.hostname:
      url += self.hostname

    if self.port:
      url += f":{self.port}"

    if self.pathname:
      url += self.pathname

    if self.search:
      url += self.search

    if self.hash:
      url += self.hash

    return url

  def __str__(self) -> str:
    return self.href

  def __repr__(self) -> str:
    return f"URL({repr(self.href)})"

  def __eq__(self, other: object) -> bool:
    if isinstance(other, str):
      return self.href == URL(other).href

    if isinstance(other, URL):
      return self.href == other.href

    return NotImplemented

  def __hash__(self) -> int:
    return hash(self.href)

  def __truediv__(self, other: object) -> 'URL':
    if isinstance(other, str):
      copy = type(self)(self)

      if not copy.pathname:
        copy.pathname = other
        return copy

      if copy.pathname.endswith('/'):
        copy.pathname = f"{copy.pathname}{other}"
      else:
        copy.pathname = f"{self.pathname}/{other}"

      return copy

    return NotImplemented
