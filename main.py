#!/usr/bin/env python2

import asana
import PyRSS2Gen
from flask import Flask, jsonify, request
from werkzeug.exceptions import Forbidden


import StringIO
import datetime
import os

app = Flask(__name__)

def validate_token():
  if request.args.get('token') != os.environ['SECRET']:
    raise Forbidden()


def fetch_tasks():
  client = asana.Client.access_token(os.environ['ASANA_TOKEN'])
  client.headers={'asana-enable': 'string_ids'}
  project_gid = os.environ['ASANA_PROJECT_GID']

  limit = request.args.get('limit', 5)

  tasks = []
  for task in client.tasks.find_all({'project': project_gid, 'completed_since': 'now'}):
    tasks.append({
      'name': task['name'],
      'id': task['gid'],
    })
    if len(tasks) >= limit:
      break
  return tasks


@app.route('/asana/tasks.json')
def get_json():
  validate_token()
  return jsonify(tasks=fetch_tasks())


@app.route('/asana/rss.xml')
def rss():
  validate_token()

  client = asana.Client.access_token(os.environ['ASANA_TOKEN'])
  client.headers={'asana-enable': 'string_ids'}

  project_gid = os.environ['ASANA_PROJECT_GID']
  items = []
  for task in fetch_tasks():
    items.append(PyRSS2Gen.RSSItem(
      title=task['name'],
      link = "http://www.dalkescientific.com/news/030906-PyRSS2Gen.html",
      guid=task['id'],
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
