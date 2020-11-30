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
    spec = {}
    s = {}
    with open(fname, 'r') as file:
        data = file.read()

    # we are intentionally ignoring multiple yaml docs in one file
    s = yaml.load_all(data, Loader=yaml.SafeLoader)
    spec = list(s)[0]
    return spec['specification']

def write_header(f, fname, sname):
    print("//////////////////////////////////////////////////////////", file=f)
    print("//", file=f)
    print("// SPDX-License-Identifier: CC-BY-4.0", file=f)
    print("//", file=f)
    print("// File automatically generated by %s" %
          lib.env.full_program(), file=f)
    print("// Original YAML: %s" % fname, file=f)
    print("// This file: %s" % sname, file=f)
    print("//", file=f)
    print("", file=f)

    return

def write_para_text(f, reqt):
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

def write_para_title(f, section_level, reqt):
    stype = reqt['type']
    print("> type of spec: %s" % stype )
    title = "#" * section_level
    title += " %s Specification: %s, v%s (%s)" % \
             (stype.capitalize(), reqt['name'].title(), reqt['version'],
              reqt['status'].capitalize())
    print(title, file=f)
    return

def write_reqt(f, level, reqt):
    title = "#" * level
    title += " %s [%s.%s]" % \
             (reqt['description'].title(), reqt['name'], reqt['revision'])
    print(title, file=f)
    
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

def write_dependencies(f, level, root):
    count = 0

    reqt_id = '.'.join([root['name'], str(root['revision'])])
    startlist = lib.db.get_dependencies(reqt_id)
    if len(startlist) < 1:
        return 0

    print("> %s reqts: %s" % ('dependent', startlist))
    title = "\n"
    title += "#" * level
    title += " Dependencies"
    print(title, file=f)

    print("The following requirements also need to be satisfied in", file=f)
    print("order to satisfy the parent requirement for this section.", file=f)

    for ii in startlist:
        rinfo = ii.split('.')
        r = lib.db.find_reqt(rinfo[0], rinfo[1])
        if not r:
            print("? unknown %s requirement: %s, revision %s" % 
                  ('dependent', rinfo[0], rinfo[1]))
        else:
            write_reqt(f, level+1, r)
            count += 1

    return count

def write_implications(f, level, root):
    count = 0

    reqt_id = '.'.join([root['name'], str(root['revision'])])
    startlist = lib.db.get_implications(reqt_id)
    if len(startlist) < 1:
        return 0

    print("> %s reqts: %s" % ('implications', startlist))
    title = "\n"
    title += "#" * level
    title += " Implications"
    print(title, file=f)

    print("The following requirements are implied by the need to", file=f)
    print("satisfy the parent requirement for this section.", file=f)

    for ii in startlist:
        rinfo = ii.split('.')
        r = lib.db.find_reqt(rinfo[0], rinfo[1])
        if not r:
            print("? unknown %s requirement: %s, revision %s" % 
                  ('implication', rinfo[0], rinfo[1]))
        else:
            write_reqt(f, level+1, r)
            count += 1

    return count

def write_all_reqts(key, f, level, root):
    count = 0

    title = "\n"
    title += "#" * level
    title += " %s Requirements" % key.capitalize()
    print(title, file=f)

    startlist = root[key]
    print("> %s reqts: %s" % (key, startlist))
    for ii in startlist:
        rinfo = ii.split('.')
        r = lib.db.find_reqt(rinfo[0], rinfo[1])
        if not r:
            print("? unknown %s requirement: %s, revision %s" % 
                  (key, rinfo[0], rinfo[1]))
        else:
            write_reqt(f, level+1, r)
            ndeps = write_dependencies(f, level+2, r)
            nimpls = write_implications(f, level+2, r)
            count += 1 + ndeps + nimpls

    return count

def generate(fname):
    if not os.path.exists(fname):
        print("? no such spec file: %s" % fname)
        return

    s = lib.asciidoc.get_yaml(fname)
    if not s:
        print("? no spec YAML found in %s" % fname)
        return

    sname = os.path.basename(fname.replace('.yml', '.adoc'))
    f = open(sname, 'w')

    print("> spec file: %s" % fname)
    print("> asciidoc file: %s" % sname)

    section_level = lib.env.config.get_start_section_level()
    write_header(f, fname, sname)
    write_para_title(f, section_level, s)
    write_para_text(f, s)

    count = 0
    total = 0
    for ii in ['mandatory', 'recommended', 'optional']:
        count = write_all_reqts(ii, f, section_level+1, s)
        print('> wrote %d %s reqts' % (count, ii))
        total += count

    print("> %d spec reqts processed" % total)
    f.close()
    return
