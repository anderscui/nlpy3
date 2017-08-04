#!/usr/bin/env python
# encoding: utf-8
# Copyright 2016 Information Retrieval and Data Science (IRDS) Group,
# University of Southern California (USC), Los Angeles
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
os.environ['NADILEAF_ENV'] = 'dev'

from etl.io import IOParams, DBNode, SQLFeed
from ndconfig import RDS_SETTING

from argparse import ArgumentParser
import os
import json
import sys
import sqlite3
import logging
from datetime import datetime
import urllib
import random

from flask import Flask, render_template, request, abort, send_file, redirect, Response

app = Flask(__name__)

# Constants
DB_FILE = "db.sqlite"
SETTINGS_FILE = "settings.json"
LOGS_FILE = "logs.log"
CREATE_TABLE_STMT = "CREATE TABLE IF NOT EXISTS data (" \
                    "text text PRIMARY KEY, " \
                    "label text, " \
                    "last_modified datetime DEFAULT current_timestamp, " \
                    "before text, " \
                    "after text, " \
                    " UNIQUE (text) ON CONFLICT IGNORE )"  # Ignore it to preserve previous labels
INSERT_STMT = "INSERT INTO data VALUES (?, ?, ?, ?, ?)"
UPDATE_STMT = "UPDATE data SET label=?, last_modified=datetime() WHERE text=?"
SELECT_UNLABELLED = "SELECT * FROM data WHERE label IS NULL"
SELECT_LABELLED = "SELECT * FROM data WHERE label IS NOT NULL"
GET_STMT = "SELECT * FROM data WHERE text = ?"
LOG_LEVEL = logging.DEBUG

service = None  # will be initialized from CLI args


@app.route("/")
def webpage():
    text = request.args.get('text')
    if not text:
        # redirect with text query param so that user can navigate back later
        next_rec = service.get_next_unlabelled()
        if next_rec:
            return redirect("/?text=%s" % (urllib.parse.quote(next_rec['text'])))
        else:
            featured_content = "No Unlabelled Record Found."
    else:
        featured_content = get_next(text)
    data = {
        'featured_content': featured_content,
        'status': service.overall_status()
    }
    return render_template('index.html', **data)


@app.route("/proxy")
def document():
    url = request.args.get('url')
    if not url or not os.path.exists(url):
        return abort(400, "File %s not found " % url)
    return send_file(url)


@app.route("/update", methods=['POST'])
def update():
    data = request.form
    text = data['text']
    labels = data.getlist('label')
    assert labels
    assert text
    count = service.update_record(text, labels)
    if count > 0:
        next_rec = service.get_next_unlabelled()
        target = "/"
        if next_rec:
            target += "?text=%s" % (urllib.parse.quote(next_rec['text']))
        return redirect(location=target)
    else:
        return abort(400, "Failed... No records updated")


@app.route("/settings")
def get_settings():
    return json.dumps(service.settings)


@app.route("/download.csv")
def download():
    recs = service.query_recs(SELECT_LABELLED + " ORDER BY last_modified DESC", first_only=False)
    recs = map(lambda r: ":::".join([r['last_modified'], r['text'], r['label']])
                         + "\n", recs)
    return Response(recs, mimetype='text/csv')


def get_next(text=None):
    next_rec = service.get_record(text)
    text = next_rec['text']
    before = next_rec['before']
    after = next_rec['after']
    template_name = '%s.html' % service.settings['type']
    data_url = text if text.startswith('http') else "/proxy?url=%s" % urllib.parse.quote(next_rec['text'])
    data = {
        'data_url': data_url,
        'text': text,
        'before_cxt': before.splitlines() if before else [],
        'after_cxt': after.splitlines() if after else [],
        'task': service.settings['task']
    }
    return render_template(template_name, **data)


class DbService(object):
    def __init__(self, workdir, input_file):
        self.workdir = workdir
        print("Work Dir : %s" % workdir)
        logs_fn = os.path.join(workdir, LOGS_FILE)
        settings_fn = os.path.join(workdir, SETTINGS_FILE)
        if not os.path.exists(settings_fn):
            print("Error: Settings file not found, looked at: %s" % settings_fn)
            sys.exit(2)

        print("Logs are being stored at %s ." % logs_fn)
        self.log = logging
        self.log.basicConfig(filename=logs_fn, level=LOG_LEVEL)
        with open(settings_fn) as f:
            self.settings = json.load(f)
            self.log.debug("Loaded the settings : %s" % (self.settings))
        self.db = self.connect_db()
        self.log.info("Work Dir %s" % workdir)
        if input_file:
            if not os.path.exists(input_file):
                self.log.info('Loading data from database...')
                self.load_texts_from_db_source()

            elif input_file.endswith('.txt'):
                self.log.info('Loading data from text file...')
                with open(input_file, 'r') as input:
                    samples = filter(lambda y: y, map(lambda x: x.strip(), input))
                    count = self.insert_if_not_exists(samples)
                    self.log.info("Inserted %d new records from %s file." % (count, input_file))
            else:
                self.log.info('Loading data from json file...')
                secs = json.load(open(input_file, 'r'))
                samples = []
                for sec in secs[:100]:
                    nonempty = [line.strip() for line in sec if line.strip()]
                    if nonempty:
                        n = len(nonempty)
                        lino = random.choice(range(n))
                        before = nonempty[lino - 1] if lino > 0 else None
                        after = nonempty[lino + 1] if lino < (n - 1) else None
                        samples.append((nonempty[lino], before, after))

                count = self.insert_if_not_exists(samples)
                self.log.info("Inserted %d new records from %s file." % (count, input_file))

        else:
            self.log.info("No new inputs are supplied")

    def load_texts_from_db_source(self):
        ioparams = IOParams(
            chunksize=1280,
            flag='deterministic',
            train_ratio=100)
        dbnode = DBNode(
            database=RDS_SETTING.job_crawl,
            table_name='lagou_stage')

        samples = []
        for dfno, df in SQLFeed(dbnode,
                                 origin_columns=['job_responsibility'],
                                 params=ioparams):
            if dfno > 0:
                break
            for i, row in df.iterrows():
                job_desc = row['job_responsibility']
                nonempty = [line.strip() for line in job_desc.splitlines() if line.strip()]
                if nonempty:
                    n = len(nonempty)
                    lino = random.choice(range(n))

                    before_lines = []
                    if lino > 0:
                        before_lines = nonempty[max(0, lino-2): lino]
                    before = '\n'.join(before_lines) if before_lines else None

                    after_lines = []
                    if lino < (n - 1):
                        after_lines = nonempty[lino+1: min(n-1, lino+2)+1]
                    after = '\n'.join(after_lines) if after_lines else None

                    samples.append((nonempty[lino], before, after))

        count = self.insert_if_not_exists(samples)
        self.log.info("Inserted %d new records from database." % count)

    def connect_db(self):
        db_file = os.path.join(self.workdir, DB_FILE)
        self.log.info("Connecting to database file at %s" % db_file)
        db = sqlite3.connect(db_file, check_same_thread=False)

        def dict_factory(cursor, row):  # map tuples to dictionary with column names
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        db.row_factory = dict_factory
        cursor = db.cursor()
        cursor.execute(CREATE_TABLE_STMT)
        db.commit()
        cursor.close()
        return db

    def insert_if_not_exists(self, urls):
        count = 0
        cursor = self.db.cursor()
        for text, before, after in urls:
            values = (text, None, datetime.now(), before, after)
            # assumption: if rec exists, DB will IGNORE IT
            res = cursor.execute(INSERT_STMT, values)
            count += 1
        self.db.commit()
        cursor.close()
        return count

    def update_record(self, text, labels):
        self.log.info("Updating %s with %s" % (text, labels))
        cur = self.db.execute(UPDATE_STMT, (",".join(labels), text))
        count = cur.rowcount
        self.log.info("Rows Updated = %d" % count)
        cur.close()
        self.db.commit()
        return count

    def get_next_unlabelled(self):
        return self.query_recs(SELECT_UNLABELLED + " ORDER BY RANDOM() LIMIT 1",
                               first_only=True)

    def get_record(self, text):
        return self.db.execute(GET_STMT, (text,)).fetchone()

    def query_recs(self, query, first_only=True):
        cur = self.db.execute(query)
        return cur.fetchone() if first_only else cur

    def get_count(self, query):
        assert " * " in query
        query = query.replace(" * ", " COUNT(*) as COUNT ")
        return self.db.execute(query).fetchone()['COUNT']

    def overall_status(self):
        pending = self.get_count("SELECT * FROM data WHERE label IS NULL")
        total = self.get_count("SELECT * FROM data")
        return {'total': total, 'pending': pending, 'done': total - pending}

    def __del__(self):
        if hasattr(self, 'db') and self.db:
            self.log.info("Committing before exit.")
            self.db.commit()
            self.db = None


if __name__ == "__main__":
    parser = ArgumentParser(description="Web UI for Labeling images")
    parser.add_argument("-i", "--input", help="Path to to input file which has list of paths, one per line. (Optional)")
    parser.add_argument("-w", "--work-dir", help="Work Directory. (Required)", required=True)
    parser.add_argument("-p", "--port", type=int, help="Bind port. (Optional)", default=8080)
    parser.add_argument("-c", "--context", type=int, help="Context window size. (Optional)", default=1)
    args = vars(parser.parse_args())
    host = '0.0.0.0'
    service = DbService(args['work_dir'], args['input'])
    print("Starting on  %s %s/" % (host, args['port']))
    app.run(host=host, port=args['port'])