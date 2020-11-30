#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=================================m
#

import os
import sqlite3
import sys

dbcon = ''

def add_dependencies_table(cur):
    table_sql = """
    CREATE TABLE dependencies (
       id integer PRIMARY KEY,
       reqt_id text NOT NULL,
       dep_id text NOT NULL
    )"""
    cur.execute(table_sql)
    return

def add_implications_table(cur):
    table_sql = """
    CREATE TABLE implications (
       id integer PRIMARY KEY,
       reqt_id text NOT NULL,
       impl_id text NOT NULL
    )"""
    cur.execute(table_sql)
    return

def add_reqts_table(cur):
    reqts_table_sql = """
    CREATE TABLE reqts (
	name text NOT NULL,
	revision integer NOT NULL,
	type text NOT NULL,
	class text NOT NULL,
	level text NOT NULL,
	description text NOT NULL,
	test text NOT NULL,
	details text NOT NULL,
	depends text,
	implies text,
	reference text,
	PRIMARY KEY (name, revision),
        FOREIGN KEY (depends) REFERENCES dependencies (id),
        FOREIGN KEY (implies) REFERENCES implications (id))"""
    cur.execute(reqts_table_sql)
    return

def init(dbname):
    if os.path.exists(dbname):
        print("? data base \"%s\" already exists, exiting" % dbname)
        sys.exit(1)

    con = sqlite3.connect(dbname)
    cur = con.cursor()
    add_dependencies_table(cur)
    add_implications_table(cur)
    add_reqts_table(cur)
    con.close()

    return

def opendb(dbname):
    global dbcon

    if not os.path.exists(dbname):
        print("? data base \"%s\" does not exist, run init" % dbname)
        sys.exit(1)

    dbcon = sqlite3.connect(dbname)

    return

def closedb():
    global dbcon

    dbcon.close()

    return

def find_dependency(reqt_id, dep_id):
    global dbcon

    sql = """SELECT reqt_id, dep_id FROM dependencies
             WHERE reqt_id = '%s' and dep_id = '%s'""" % (reqt_id, dep_id)
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()

    return result

def find_implication(reqt_id, impl_id):
    global dbcon

    sql = """SELECT reqt_id, impl_id FROM implications
             WHERE reqt_id = '%s' and impl_id = '%s'""" % (reqt_id, impl_id)
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()

    return result

def find_reqt(name, revision):
    global dbcon

    key = str(name) + '-' + str(revision)
    sql = """SELECT name, revision, type, class, level, description,
             test, details, depends, implies, reference FROM reqts
             WHERE name = '%s' and revision = '%s'""" % (name, revision)
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()

    return result

def add_dependency(reqt_id, dep_id):
    global dbcon

    sql = """
    INSERT INTO dependencies
        (reqt_id, dep_id)
    VALUES (?, ?)"""

    cur = dbcon.cursor()
    cur.execute(sql, (reqt_id, dep_id))

    return cur.lastrowid

def add_implication(reqt_id, impl_id):
    global dbcon

    sql = """
    INSERT INTO implications
        (reqt_id, impl_id)
    VALUES (?, ?)"""

    cur = dbcon.cursor()
    cur.execute(sql, (reqt_id, impl_id))

    return cur.lastrowid

def add_reqt(reqt):
    global dbcon

    sql = """
    INSERT INTO reqts
        (name, revision, type, class, level, description,
	 test, details, depends, implies, reference)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    cur = dbcon.cursor()

    reqt_id = reqt['name'] + '.' + str(reqt['revision'])
    dep_id = reqt['name'] + '.' + str(reqt['revision'])
    impl_id = reqt['name'] + '.' + str(reqt['revision'])
    if 'depends' in reqt.keys():
         for ii in reqt['depends']:
             print('%s depends on %s' % (reqt_id, ii))
             if not find_dependency(reqt_id, ii):
                 add_dependency(reqt_id, ii)
    if 'implies' in reqt.keys():
         for ii in reqt['implies']:
             print('%s implies %s' % (reqt_id, ii))
             if not find_implication(reqt_id, ii):
                 add_implication(reqt_id, ii)
    refs = ''
    if 'reference' in reqt.keys():
         refs = reqt['reference']

    cur.execute(sql, (reqt['name'], reqt['revision'],
                      reqt['type'], reqt['class'], reqt['level'],
                      reqt['description'], reqt['test'], reqt['details'],
		      dep_id, impl_id, refs))
    dbcon.commit()
    result = cur.lastrowid

    return result

def get_dependencies(reqt_id):
    global dbcon

    rlist = []
    sql = """SELECT dep_id reference FROM dependencies
             WHERE reqt_id = \"%s\" """ % reqt_id
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    while result:
        rlist.append[list(result)[0]]
        result = cur.fetchone()
    return rlist

def get_implications(reqt_id):
    global dbcon

    rlist = []
    sql = """SELECT impl_id reference FROM implications
             WHERE reqt_id = \"%s\" """ % reqt_id
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    while result:
        rlist.append[list(result)[0]]
        result = cur.fetchone()
    return rlist

def write_yaml_dependencies(f, reqt_id):
    global dbcon

    sql = """SELECT dep_id reference FROM dependencies
             WHERE reqt_id = \"%s\" """ % reqt_id
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    if result:
        print('    depends:', file=f)
        while result:
            print('        - %s' % list(result)[0], file=f)
            result = cur.fetchone()

    return

def write_yaml_implications(f, reqt_id):
    global dbcon

    sql = """SELECT impl_id reference FROM implications
             WHERE reqt_id = \"%s\" """ % reqt_id
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    if result:
        print('    implies:', file=f)
        while result:
            print('        - %s' % list(result)[0], file=f)
            result = cur.fetchone()

    return

def write_yaml_list(f, info):
    for ii in info:
        print('    - %s' % ii)
    return

def write_yaml_string(f, info):
    last = 0
    raw = info.strip().split()
    ln = ''
    for ii in raw:
        if last + len(ii) > 60:
            print('        %s' % ln.strip(), file=f)
            ln = ii + ' '
            last = 0
        else:
            ln += ii + ' '
        last += len(ii)
    if len(ln) > 0:
        print('        %s' % ln.strip(), file=f)
    return

def write_yaml(f, reqt):
    
    # print(reqt, file=f)
    print('%YAML 1.2', file=f)
    print('---', file=f)
    print('reqt:', file=f)
    print('    name: %s' % reqt['name'], file=f)
    print('    description: %s' % reqt['description'], file=f)
    print('    revision: %s' % reqt['revision'], file=f)
    print('    type: %s' % reqt['type'], file=f)
    print('    class: %s' % reqt['class'], file=f)
    print('    level: %s' % reqt['level'], file=f)
    print('    details: >', file=f)
    write_yaml_string(f, reqt['details'])
    if 'reference' in reqt.keys():
        print('    reference: >', file=f)
        write_yaml_string(f, reqt['reference'])
    if 'depends' in reqt.keys():
        write_yaml_dependencies(f, reqt['depends'])
    if 'implies' in reqt.keys():
        write_yaml_implications(f, reqt['implies'])
    print('...', file=f)
    
    return

def find_highest_revision(reqt):
    global dbcon

    sql = """SELECT revision FROM reqts WHERE name = '%s'""" % reqt
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    rev = -1
    result = cur.fetchone()
    while result:
        if list(result)[0] > rev:
            rev = list(result)[0]
        result = cur.fetchone()
    return rev

def list_reqt(reqt):
    revision = find_highest_revision(reqt)
    if revision >= 0:
        result = find_reqt(reqt, revision)
        if result:
            write_yaml(sys.stdout, (dict(result)))
        else:
            print("? reqt '%s.%d' not found" % (reqt, revision))
    else:
        print("? reqt '%s.%d' not found" % (reqt, revision))

    return

def dump_reqts_yaml(dname):
    global dbcon

    sql = """SELECT name, revision, type, class, level,
                    description, test, details, depends, implies,
		    reference FROM reqts"""
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    while result:
        fname = os.path.join(dname, dict(result)['name'])
        fname += '.yml'

        with open(fname, 'w') as f:
            write_yaml(f, (dict(result)))

        result = cur.fetchone()

    return

