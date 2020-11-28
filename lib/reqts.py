#!/usr/bin/env python3
#=============================================================================
# 
# SPDX-License-Identifier: MIT
# 
# Copyright (c) 2020 Al Stone <ahs3@redhat.com>
# 
#=============================================================================
#

import os
import lib.env
import numbers
import yaml

known_classes = [ 'hardware', 'software', 'firmware', 'hw', 'sw', 'fw' ]
known_levels = [ 'mandatory', 'recommended', 'optional', 'must', 'should',
                 'may' ]

def get_yaml(fname):
	reqt = {}
	r = {}
	with open(fname, 'r') as file:
		data = file.read()

	# print ("> read from %s" % fname)
	r = yaml.load_all(data, Loader=yaml.SafeLoader)
	for ii in list(r):
		for jj in list(ii):
			if jj in reqt:
				reqt[jj].append(ii)
			else:
				reqt[jj] = [ii]

	return reqt

def check_class(value):
    global known_classes

    if not value or len(value) < 1:
        return False

    v = value.lower()
    if v not in known_classes:
        return False

    return True

def check_description(value):
    if not value or len(value) < 1:
        return False

    if len(value.split('\n')) > 1:
        return False

    return True

def check_level(value):
    global known_levels

    if not value or len(value) < 1:
        return False

    v = value.lower()
    if v not in known_levels:
        return False

    return True

def check_name(name, rev):
    if not name or len(name) < 1:
        return False

    if not check_revision(rev):
        return False

    result = lib.db.find_reqt(name, rev)
    if result:
        return False

    return True

def check_revision(value):
    return isinstance(value, numbers.Number)

def check_test(value):
    if not value or len(value) < 1:
        return False

    if value == 'tbd' or value == 'TBD':
        return True

    return True

def check_text(value):
    if not value or len(value) < 1:
        return False

    return True

def check_type(value):
    if not value or len(value) < 1:
        return False

    v = value.lower()
    if v != 'platform' and v != 'profile':
        return False

    return True

def check(reqt):

    okay = True
    rdict = reqt
    name = rdict['name']
    print("--- checking %s" % name)
    # print(rdict)

    # mandatory stuff:
    # has the reqt id (name) already been used?
    if 'name' in rdict.keys():
        if not check_name(rdict['name'], rdict['revision']):
            print("? name already being used")
            okay = False
    else:
        print("? name field is required")
        okay = False

    # is there a non-empty description field?
    if 'description' in rdict.keys():
        if not check_description(rdict['description']):
            print("? description needs to be one line")
            okay = False
    else:
        print("? description field is required")
        okay = False

    # is there an integer revision field?
    if 'revision' in rdict.keys():
        if not check_revision(rdict['revision']):
            print("? revision field has invalid value")
            okay = False
    else:
        print("? revision field is required")
        okay = False

    # is there a type field, with platform | profile?
    if 'type' in rdict.keys():
        if not check_type(rdict['type']):
            print("? type field has invalid value")
            okay = False
    else:
        print("? type field is required")
        okay = False

    # is there a class field, with hardware | software | firmware?
    # or with hw | sw | fw?
    if 'class' in rdict.keys():
        if not check_class(rdict['class']):
            print("? class field has invalid value")
            okay = False
    else:
        print("? class field is required")
        okay = False

    # is there a level field, with mandatory | recommended |
    # optional?  or with must | should | may?
    if 'level' in rdict.keys():
        if not check_level(rdict['level']):
            print("? level field has invalid value")
            okay = False
    else:
        print("? level field is required")
        okay = False

    # is there a non-empty test field?
    if 'test' in rdict.keys():
        if not check_test(rdict['test']):
            print("? test field needs to be defined")
            okay = False
    else:
        print("? test field is required")
        okay = False

    # is there a non-empty details field?
    if 'details' in rdict.keys():
        if not check_text(rdict['details']):
            print("? details field needs to be defined")
            okay = False
    else:
        print("? details field is required")
        okay = False

    # optional stuff:
    # NB: these relationships are checked when the fields are added
    # if depends is used, are all reqts known?
    # if implies is used, are all reqts known?

    # if reference is used, is it a non-empty string?
    if 'reference' in rdict.keys():
        if not rdict['reference']:
            print("? reference field needs a value if used")
            okay = False

    return okay

def check_all(fname):
    reqt = lib.reqts.get_yaml(fname)
    
    for ii in reqt['reqt']:
        check(ii['reqt'])

    return

def add(fname):
    rowid = -1
    reqt = lib.reqts.get_yaml(fname)
    
    for ii in reqt['reqt']:
        if check(ii['reqt']):
            rowid = lib.db.add_reqt(ii['reqt'])
            print("--- added %s, row %s" % (ii['reqt']['name'], rowid))

    return rowid

def dump(dname):
    lib.db.dump_reqts_yaml(dname)
    return
