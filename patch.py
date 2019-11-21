#!/usr/bin/env python
#
# scary patch things that mess with internals
#
# Author: Joshua A Haas

import socket

class patch_dns:
  """DNS patch context manager"""

  def __init__(self, hosts):
    patch_dns.patch(hosts)

  def __enter__(self):
    return self

  def __exit__(self, *args, **kwargs):
    patch_dns.unpatch()

  @staticmethod
  def unpatch():
    """undo DNS patch"""

    socket.getaddrinfo = socket._real_getaddrinfo

  @staticmethod
  def patch(hosts):
    """patch DNS with a dict of overrides"""

    socket._real_getaddrinfo = socket.getaddrinfo
    socket._patch_dns_hosts = hosts

    def resolve(host, port, family=0, type=0, proto=0, flags=0):

      args = (host, port, family, type, proto, flags)

      real = None
      try:
        real = socket._real_getaddrinfo(*args)
        if host not in socket._patch_dns_hosts:
          return real
      except:
        if host not in socket._patch_dns_hosts:
          raise

      families = ['INET', 'INET6', 'UNIX']
      default = set([(type or socket.SOCK_STREAM, proto or socket.IPPROTO_TCP, '', port)])

      info = {}
      if real is not None:
        for r in real:
          info.setdefault(r[0], set()).add((r[1], r[2], r[3], r[4][1]))
        for f in families:
          f = getattr(socket, 'AF_' + f)
          if f in info:
            default = info[f]
            break
      for f in families:
        f = getattr(socket, 'AF_' + f)
        if f not in info:
          info[f] = default

      result = []
      ips = socket._patch_dns_hosts[host]
      if not isinstance(ips, list):
        ips = [ips]
      for ip in ips:

        if ip.count('.') == 3:
          family = socket.AF_INET
        elif ':' in ip:
          family = socket.AF_INET6
        else:
          raise ValueError('invalid ip "%s"' % ip)

        for x in info[family]:
          result.append((family, x[0], x[1], x[2], (ip, x[3])))

      return result

    socket.getaddrinfo = resolve

def unpatch_dns():
  """undo DNS patch"""

  patch_dns.unpatch()
