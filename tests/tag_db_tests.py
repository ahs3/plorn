
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import copy
import os
import sys
import unittest

import plorn.album
import plorn.attr
import plorn.config
import plorn.db
import plorn.photo

import tests.reporting

sys.stderr = open(os.devnull, 'w')


class TestDbTagMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tests.reporting.start(cls)

    @classmethod
    def tearDownClass(cls):
        tests.reporting.stop(cls)

    def write_test_config(self, name):
        data = [
            '[plorn]',
            'user = fred',
            'full_name = Fred Flintstone',
            'config_dir = /tmp/barney',
            f'data_dir = {os.path.expanduser('~/.local/share/plorn')}',
            'dbname = completely_bogus.db',
        ]
        with open(name, 'w') as cfg:
            for ii in data:
                cfg.write(ii + '\n')
        cfg.close()

    def get_test_dbname(self):
        dbpath = os.path.expanduser('~/.local/share/plorn')
        return os.path.join(dbpath, 'completely_bogus.db')

    def get_test_cfgname(self):
        path = os.path.expanduser('~/.config/plorn')
        return os.path.join(path, 'completely_bogus.cfg')

    def setUp(self):
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)
        self.write_test_config(self.get_test_cfgname())
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        plorn.db.close()

    def tearDown(self):
        tests.reporting.echo_result(self)
        plorn.db.close()
        plorn.config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def make_tag(self, tag, parent_id=None):
        return plorn.attr.PlornTag(tag, parent_id=parent_id)

    def test_add_tag(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('fred')
        tag = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(tag))

        plorn.db.close()
        plorn.config.close()

    def test_add_subtag(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('Flintstone')
        parent = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(parent))

        p = db.get_tag(parent.get_id())
        tmp = self.make_tag('Fred', parent_id=p.get_id())
        child = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(child))

        c = db.get_tag(child.get_id())
        self.assertTrue(c.get_parent_id(), p.get_id())

        plorn.db.close()
        plorn.config.close()

    def test_get_tag_children(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('Flintstone')
        parent = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(parent))

        p = db.get_tag(parent.get_id())
        tmp = self.make_tag('Fred', parent_id=p.get_id())
        child = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(child))

        c = db.get_tag(child.get_id())
        self.assertTrue(c.get_parent_id(), p.get_id())

        kids = db.get_tag_children(p)
        found = False
        for ii in kids:
            if ii.get_value() == c.get_value():
                found = True
                break
        self.assertTrue(found)

        plorn.db.close()
        plorn.config.close()

    def test_get_full_tag(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('Flintstone')
        parent = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(parent))

        p = db.get_tag(parent.get_id())
        tmp = self.make_tag('Fred', parent_id=p.get_id())
        child = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(child))

        c = db.get_tag(child.get_id())
        self.assertEqual(c.get_parent_id(), p.get_id())
        fulltag = db.get_full_tag(c)
        self.assertTrue(fulltag == ['Flintstone', 'Fred'])
        self.assertTrue(', '.join(fulltag) == 'Flintstone, Fred')

        plorn.db.close()
        plorn.config.close()

    def test_get_all_tags(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('Flintstone')
        parent = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(parent))

        p = db.get_tag(parent.get_id())
        tmp = self.make_tag('Fred', parent_id=p.get_id())
        child = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(child))

        c = db.get_tag(child.get_id())
        self.assertEqual(c.get_parent_id(), p.get_id())
        fulltag = db.get_full_tag(c)
        self.assertTrue(fulltag == ['Flintstone', 'Fred'])
        self.assertTrue(', '.join(fulltag) == 'Flintstone, Fred')
        self.assertEqual(c.get_parent_id(), p.get_id())

        all_tags = db.get_all_tags()
        self.assertTrue(len(all_tags) == 2)
        id_list = []
        for ii in all_tags:
            id_list.append(ii.get_id())
        self.assertTrue(p.get_id() in id_list)
        self.assertTrue(c.get_id() in id_list)

        plorn.db.close()
        plorn.config.close()

    def test_remove_tag(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('fred')
        tag = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(tag))

        db.remove_tag(tag)
        self.assertFalse(db.tag_exists(tag))

        tags = db.get_all_tags()
        self.assertTrue(len(tags) == 0)

        plorn.db.close()
        plorn.config.close()

    def test_update_tag(self):
        db = plorn.db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_tag('fred')
        tag = db.add_tag(tmp)
        self.assertTrue(db.tag_exists(tag))

        tag_copy = copy.deepcopy(tag)
        self.assertTrue(tag.get_value() == tag_copy.get_value())

        tag_copy.set_value('barney')
        tid = db.update_tag(tag, tag_copy)
        updated_tag = db.get_tag(tid)
        self.assertTrue(updated_tag.get_value() == 'barney')
        self.assertTrue(updated_tag.get_value() != 'fred')

        tags = db.get_all_tags()
        self.assertTrue(len(tags) == 1)

        plorn.db.close()
        plorn.config.close()

