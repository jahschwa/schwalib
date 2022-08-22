#!/usr/bin/env python3

from datetime import datetime as dt
from pathlib import Path
import re
from subprocess import run

import requests

URL_HOME = 'https://www.ups.com/track?loc=en_US&Requester=lasso/trackdetails'
URL_API = 'https://www.ups.com/track/api/Track/GetStatus?loc=en_US'

HOME = Path('~').expanduser()
FILE_CONFIG = HOME / Path('cron/config/ups.txt')
DIR_STATE = HOME / Path('cron/state/ups/')

def main():

  tracks = parse_config(FILE_CONFIG)
  cleanup_old_state(tracks, DIR_STATE)

  old = parse_state(tracks, DIR_STATE)
  new = fetch_state(tracks)

  to_delete = notify(tracks, old, new)
  update_config(to_delete, FILE_CONFIG)
  write_new_state(tracks, new, DIR_STATE)

def parse_config(config_file):

  if not config_file.is_file():
    config_file.parent.mkdir(parents=True, exist_ok=True)
    with open(config_file) as f:
      f.write('')

  tracks = {}
  with open(config_file) as f:
    for line in f:
      if line := line.strip():
        (track_id, label) = line.split(' ', maxsplit=1)
        tracks[track_id] = label

  return tracks

def cleanup_old_state(tracks, state_dir):

  if not state_dir.is_dir():
    state_dir.mkdir(parents=True, exist_ok=True)

  fnames = {label_to_fname(label) for label in tracks.values()}

  for f in state_dir.iterdir():
    if f.name not in fnames:
      f.unlink()

def parse_state(tracks, state_dir):

  fname_to_track_id = {
    label_to_fname(label): track_id for (track_id, label) in tracks.items()
  }

  state = {track_id: None for track_id in tracks}
  for fname in state_dir.iterdir():
    track_id = fname_to_track_id[fname.name]
    state[track_id] = UPSPackage(track_id=track_id, file_name=fname)

  return state

def fetch_state(tracks):

  state = {}
  for track_id in tracks:
    state[track_id] = UPSPackage(track_id=track_id)

  return state

def notify(tracks, old_infos, new_infos):

  to_delete = set()

  for track_id in old_infos:
    (label, old, new) = (d[track_id] for d in (tracks, old_infos, new_infos))
    if old != new:
      send = lambda s: send_txt(label, s)
      send('[{timestamp:%m/%d/%Y %I:%M %p}] {location} = {activity}'.format(
          **vars(new.log[-1])
      ))
      if 'delivered' in new.status.lower():
        to_delete.add(track_id)
      else:
        if old:
          if new.eta != old.eta:
            send('ETA CHANGED! {} --> {}'.format(old.eta_str(), new.eta_str()))
        elif new.eta:
          send('ETA: {}'.format(new.eta_str()))

  return to_delete

def send_txt(label, msg):

  run([
    '/home/laptopdude/bin/send-txt',
    f'UPS:{label}',
    msg,
  ])

def update_config(to_delete, config_file):

  if not to_delete:
    return

  with open(config_file) as f:
    lines = f.readlines()

  with open(config_file, 'w') as f:
    f.writelines([
      line for line in lines if line.split(' ')[0] not in to_delete
    ])

def write_new_state(tracks, state, state_dir):

  for (track_id, pkg) in state.items():
    fname = label_to_fname(tracks[track_id])
    with open(state_dir / fname, 'w') as f:
      f.write(str(pkg))

def label_to_fname(s):

  return s.lower().replace(' ', '_') + '.txt'

class UPSPackage:

  FMT = {
    'eta': '%m/%d/%Y',
  }
  PARSE = {
    'eta': lambda s: None if s == 'None' else dt.strptime(s, UPSPackage.FMT['eta']),
  }

  KEYS_EQ = ('track_id', 'status', 'eta', 'log')

  @staticmethod
  def fetch(track_id):
    """returns UPS json details for the given package"""

    s = requests.Session()
    s.get(URL_HOME)

    kwargs = {
      'headers': {
        'X-XSRF-TOKEN': s.cookies['X-XSRF-TOKEN-ST'],
      },
      'json': {
        'TrackingNumber': [track_id],
      },
    }

    data = s.post(URL_API, **kwargs).json()['trackDetails'][0]

    return data

  @staticmethod
  def scrape(track_id=None, data=None):
    """returns dict(data, status, eta, log)"""

    if track_id is None and data is None:
      raise ValueError('one of track_id or data is required')

    if data is None:
      data = UPSPackage.fetch(track_id)

    eta = data['scheduledDeliveryDate']
    if eta.strip():
      eta = dt.strptime(eta, '%m/%d/%Y')
    else:
      eta = None

    log = [
      UPSPackageActivity(activity)
      for activity in data['shipmentProgressActivities'][::-1]
      if activity['date'].strip()
    ]

    return {
      'data': data,
      'status': data['packageStatus'],
      'eta': eta,
      'log': log,
    }

  @staticmethod
  def parse(file_name):

    with open(file_name) as f:
      lines = f.readlines()

    log = []
    current = None
    second = False
    for (i, line) in enumerate(lines):
      if not line.strip():
        continue
      if second:
        second = False
        current += line
        log.append(UPSPackageActivity(parse_str=current))
      elif line.startswith(UPSPackageActivity.FMT_STR[0]):
        second = True
        current = line
      else:
        break

    result = {'log': log}
    for line in lines[i:]:
      (key, value) = (x.strip() for x in line.split(':', maxsplit=1))
      if value.strip():
        key = key.lower()
        if func := UPSPackage.PARSE.get(key):
          value = func(value)
        result[key] = value

    return result

  def __init__(self, track_id, file_name=None, populate=True, data=None):

    self.track_id = track_id
    self.file_name = file_name

    self.data = {}
    self.status = ''
    self.eta = None
    self.log = []

    if populate:
      self._populate(data)

  def eta_str(self):

    if self.eta:
      return self.eta.strftime(UPSPackage.FMT['eta'])
    else:
      return 'None'

  def _populate(self, data):

    if self.file_name:
      result = UPSPackage.parse(self.file_name)
    else:
      result = UPSPackage.scrape(self.track_id, data)
    for (k, v) in result.items():
      setattr(self, k, v)

  def __eq__(self, other):

    if not isinstance(other, UPSPackage):
      return False

    return all(
      getattr(self, k) == getattr(other, k) for k in UPSPackage.KEYS_EQ
    )

  def __str__(self):

    lines = [str(activity) + '\n' for activity in self.log]
    lines.extend([
      'ETA    : {}'.format(self.eta_str()),
      'Status : {}'.format(self.status),
    ])

    return '\n'.join(lines) + '\n'

class UPSPackageActivity:

  PARSE_TS = '%m/%d/%Y %I:%M %p'

  FMT_STR = '[{timestamp:' + PARSE_TS + '}] {location}\n    {activity}'
  REGEX_PARSE = re.compile('^\[([^]]+)\] +(.*)    (.+)$')

  KEYS_KEEP = {
    'activityScan',
    'date',
    'location',
    'time',
  }

  KEYS_RENAME = {
    'activityScan': 'activity',
  }

  KEYS_MODIFY = {
    'time': lambda t: t.replace('.', ''),
  }

  KEYS_COMBINE = {
    'timestamp': (
      ('date', 'time'),
      lambda date, time: dt.strptime(
        date + ' ' + time, UPSPackageActivity.PARSE_TS
      ),
    )
  }

  PARSE = {
    'timestamp': lambda ts: dt.strptime(ts, UPSPackageActivity.PARSE_TS),
  }

  KEYS_EQ = ('timestamp', 'location', 'activity')

  @staticmethod
  def scrape(log_entry):

    data = {
      UPSPackageActivity.KEYS_RENAME.get(k, k): log_entry[k]
      for k in UPSPackageActivity.KEYS_KEEP
    }

    for (k, func) in UPSPackageActivity.KEYS_MODIFY.items():
      data[k] = func(data[k])

    for (new, (old, func)) in UPSPackageActivity.KEYS_COMBINE.items():
      kwargs = {k: data[k] for k in old}
      data[new] = func(**kwargs)
      for k in old:
        del data[k]

    return data

  @staticmethod
  def get_fields(s):

    fields = []
    start = None
    for (i, c) in enumerate(s):
      if start is None:
        if c == '{':
          start = i + 1
      elif c in ':}':
        fields.append(s[start:i])
        start = None

    return fields

  @staticmethod
  def parse(parse_str):

    parse_str = parse_str.replace('\n', '')

    keys = UPSPackageActivity.get_fields(UPSPackageActivity.FMT_STR)
    values = UPSPackageActivity.REGEX_PARSE.search(parse_str).groups()

    result = {}
    for (k, v) in zip(keys, values):
      if func := UPSPackageActivity.PARSE.get(k):
        v = func(v)
      result[k] = v

    return result

  def __init__(self, log_entry=None, parse_str=None):

    if log_entry is None and parse_str is None:
      raise ValueError('one of log_entry or parse_str is required')

    self.activity = ''
    self.location = ''
    self.timestamp = None

    if parse_str:
      result = UPSPackageActivity.parse(parse_str)
    else:
      result = UPSPackageActivity.scrape(log_entry)
    for (k, v) in result.items():
      setattr(self, k, v)

  def __eq__(self, other):

    if not isinstance(other, UPSPackageActivity):
      return False

    return all(
      getattr(self, k) == getattr(other, k) for k in UPSPackageActivity.KEYS_EQ
    )

  def __str__(self):

    return UPSPackageActivity.FMT_STR.format(**vars(self))

if __name__ == '__main__':
  main()
