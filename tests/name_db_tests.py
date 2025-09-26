import copy
import os
import unittest

import plorn_album
import plorn_attr
import plorn_config
import plorn_db
import plorn_name
import plorn_photo
import plorn_place


class TestDbNameMethods(unittest.TestCase):

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
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())
        plorn_db.close()

    def tearDown(self):
        plorn_db.close()
        plorn_config.close()
        dbname = self.get_test_dbname()
        cfg = self.get_test_cfgname()
        if os.path.exists(dbname):
            os.remove(dbname)
        if os.path.exists(cfg):
            os.remove(cfg)

    def make_name(self, name, parent_id=None):
        return plorn_name.PlornName(name, parent_id=parent_id)

    def test_add_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('fred')
        name = db.add_name(tmp)
        self.assertTrue(db.name_exists(name))

        plorn_db.close()
        plorn_config.close()

    def test_add_subname(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('Flintstone')
        parent = db.add_name(tmp)
        self.assertTrue(db.name_exists(parent))

        p = db.get_name(parent.get_id())
        tmp = self.make_name('Fred', parent_id=p.get_id())
        child = db.add_name(tmp)
        self.assertTrue(db.name_exists(child))

        c = db.get_name(child.get_id())
        self.assertTrue(c.get_parent_id(), p.get_id())

        plorn_db.close()
        plorn_config.close()

    def test_get_name_children(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('Flintstone')
        parent = db.add_name(tmp)
        self.assertTrue(db.name_exists(parent))

        p = db.get_name(parent.get_id())
        tmp = self.make_name('Fred', parent_id=p.get_id())
        child = db.add_name(tmp)
        self.assertTrue(db.name_exists(child))

        c = db.get_name(child.get_id())
        self.assertTrue(c.get_parent_id(), p.get_id())

        kids = db.get_name_children(p)
        found = False
        for ii in kids:
            if ii.get_value() == c.get_value():
                found = True
                break
        self.assertTrue(found)

        plorn_db.close()
        plorn_config.close()

    def test_get_full_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('Flintstone')
        parent = db.add_name(tmp)
        self.assertTrue(db.name_exists(parent))

        p = db.get_name(parent.get_id())
        tmp = self.make_name('Fred', parent_id=p.get_id())
        child = db.add_name(tmp)
        self.assertTrue(db.name_exists(child))

        c = db.get_name(child.get_id())
        self.assertEqual(c.get_parent_id(), p.get_id())
        fullname = db.get_full_name(c)
        self.assertTrue(fullname == ['Flintstone', 'Fred'])
        self.assertTrue(', '.join(fullname) == 'Flintstone, Fred')

        plorn_db.close()
        plorn_config.close()

    def test_get_all_names(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('Flintstone')
        parent = db.add_name(tmp)
        self.assertTrue(db.name_exists(parent))

        p = db.get_name(parent.get_id())
        tmp = self.make_name('Fred', parent_id=p.get_id())
        child = db.add_name(tmp)
        self.assertTrue(db.name_exists(child))

        c = db.get_name(child.get_id())
        self.assertEqual(c.get_parent_id(), p.get_id())
        fullname = db.get_full_name(c)
        self.assertTrue(fullname == ['Flintstone', 'Fred'])
        self.assertTrue(', '.join(fullname) == 'Flintstone, Fred')
        self.assertEqual(c.get_parent_id(), p.get_id())

        all_names = db.get_all_names()
        self.assertTrue(len(all_names) == 2)
        id_list = []
        for ii in all_names:
            id_list.append(ii.get_id())
        self.assertTrue(p.get_id() in id_list)
        self.assertTrue(c.get_id() in id_list)

        plorn_db.close()
        plorn_config.close()

    def test_remove_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('fred')
        name = db.add_name(tmp)
        self.assertTrue(db.name_exists(name))

        db.remove_name(name)
        self.assertFalse(db.name_exists(name))

        names = db.get_all_names()
        self.assertTrue(len(names) == 0)

        plorn_db.close()
        plorn_config.close()

    def test_update_name(self):
        db = plorn_db.open(self.get_test_dbname(),
                           self.get_test_cfgname())

        tmp = self.make_name('fred')
        name = db.add_name(tmp)
        self.assertTrue(db.name_exists(name))

        name_copy = copy.deepcopy(name)
        self.assertTrue(name.get_value() == name_copy.get_value())

        name_copy.set_value('barney')
        tid = db.update_name(name, name_copy)
        updated_name = db.get_name(tid)
        self.assertTrue(updated_name.get_value() == 'barney')
        self.assertTrue(updated_name.get_value() != 'fred')

        names = db.get_all_names()
        self.assertTrue(len(names) == 1)

        plorn_db.close()
        plorn_config.close()

