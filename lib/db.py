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

level_map = { 'mandatory': 'mandatory',
              'must': 'mandatory',
              'recommended': 'recommended',
              'should': 'recommended',
              'optional': 'optional',
              'may': 'optional',
            }

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
             WHERE reqt_id = '%s' and dep_id = '%s'""" \
             % (reqt_id.lower(), dep_id.lower())
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()

    return result

def find_implication(reqt_id, impl_id):
    global dbcon

    sql = """SELECT reqt_id, impl_id FROM implications
             WHERE reqt_id = '%s' and impl_id = '%s'""" \
             % (reqt_id.lower(), impl_id.lower())
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
             WHERE name = '%s' and revision = '%s'""" \
             % (name.lower(), str(revision).lower())
    dbcon.row_factory = sqlite3.Row
    cur = dbcon.cursor()
    cur.execute(sql)
    result = cur.fetchone()

    return result

def find_reqt_id(reqt_id):
    rid = reqt_id.split('.')
    result = find_reqt(rid[0].lower(), int(rid[1]))
    return result

def add_dependency(reqt_id, dep_id):
    global dbcon

    sql = """
    INSERT INTO dependencies
        (reqt_id, dep_id)
    VALUES (?, ?)"""

    cur = dbcon.cursor()
    cur.execute(sql, (reqt_id.lower(), dep_id.lower()))
    cur.close()
    dbcon.commit()

    return cur.lastrowid

def add_implication(reqt_id, impl_id):
    global dbcon

    sql = """
    INSERT INTO implications
        (reqt_id, impl_id)
    VALUES (?, ?)"""

    cur = dbcon.cursor()
    cur.execute(sql, (reqt_id.lower(), impl_id.lower()))
    cur.close()
    dbcon.commit()

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
             print('%s depends on %s' % (reqt_id.lower(), ii.lower()))
             if find_reqt_id(ii.lower()):
                 if not find_dependency(reqt_id.lower(), ii.lower()):
                     add_dependency(reqt_id.lower(), ii.lower())
                 else:
                     print('? duplicate: %s already depends on %s' %
                           (reqt_id.lower(), ii.lower()))
             else:
                     print('? cannot depend on non-existent reqt %s' %
                           (ii.lower()))
    if 'implies' in reqt.keys():
         for ii in reqt['implies']:
             print('%s implies %s' % (reqt_id.lower(), ii.lower()))
             if find_reqt_id(ii.lower()):
                 if not find_implication(reqt_id.lower(), ii.lower()):
                     add_implication(reqt_id.lower(), ii.lower())
                 else:
                     print('? duplicate: %s already implies %s' %
                           (reqt_id.lower(), ii.lower()))
             else:
                     print('? cannot imply a non-existent reqt %s' %
                           (ii.lower()))
    refs = ''
    if 'reference' in reqt.keys():
         refs = reqt['reference']

    cur.execute(sql, (reqt['name'].lower(), str(reqt['revision']).lower(),
                      reqt['type'].lower(), reqt['class'].lower(),
                      level_map[reqt['level'].lower()],
                      reqt['description'], reqt['test'], reqt['details'],
                      dep_id.lower(), impl_id.lower(), refs))
    result = cur.lastrowid
    cur.close()
    dbcon.commit()

    return result

def get_dependencies(reqt_id):
    global dbcon

    rlist = []
    sql = """SELECT dep_id reference FROM dependencies
             WHERE reqt_id = \"%s\" """ % reqt_id.lower()
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
             WHERE reqt_id = \"%s\" """ % reqt_id.lower()
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
             WHERE reqt_id = \"%s\" """ % reqt_id.lower()
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
             WHERE reqt_id = \"%s\" """ % reqt_id.lower()
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

def write_yaml_text(f, text):
    if reqt['details']:
        para = reqt['details'].split('\n')
        for ii in para:
            if ii == '.':
                print('', file=f)
            else:
                print(ii, file=f)
    else:
        print('This section temporarily left blank.', file=f)
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
    write_yaml_text(f, reqt['details'])
    if 'reference' in reqt.keys():
        print('    reference: >', file=f)
        write_yaml_text(f, reqt['reference'])
    if 'depends' in reqt.keys():
        write_yaml_dependencies(f, reqt['depends'])
    if 'implies' in reqt.keys():
        write_yaml_implications(f, reqt['implies'])
    print('...', file=f)
    
    return

def find_highest_revision(reqt):
    global dbcon

    sql = """SELECT revision FROM reqts WHERE name = '%s'""" % reqt.lower()
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

