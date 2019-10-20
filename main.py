#!/usr/bin/env python2

import asana
import PyRSS2Gen
from flask import Flask

import ConfigParser
import StringIO
import datetime
import os
import sys

app = Flask(__name__)

@app.route('/asana/rss.xml')
def hello():
  config = ConfigParser.ConfigParser()
  cfg_file = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/.asana.ini')
  config.read(cfg_file)
  client = asana.Client.access_token(os.environ['ASANA_TOKEN'])
  client.headers={'asana-enable': 'string_ids'}

  project_gid = os.environ['ASANA_PROJECT_GID']
  items = []
  for task in client.tasks.find_all({'project': project_gid, 'completed_since': 'now'}):
    items.append(PyRSS2Gen.RSSItem(
      title=task['name'],
      link = "http://www.dalkescientific.com/news/030906-PyRSS2Gen.html",
      description=task['name'],
      guid=task['gid'],
      pubDate=datetime.datetime.now()))

  rss = PyRSS2Gen.RSS2(
    title="Asana project RSS",
    link="http://www.dalkescientific.com/Python/PyRSS2Gen.html",
    description='Tasks',
    lastBuildDate=datetime.datetime.now(),
    items=items)

  buffer = StringIO.StringIO()
  rss.write_xml(buffer)
  return buffer.getvalue()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=os.environ.get('PORT', None))
