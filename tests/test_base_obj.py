
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import os
import sys
import pytest

if os.path.join(',', 'src', 'plorn') not in sys.path:
    current_path = os.path.dirname(os.path.dirname(__file__))
    package_source_path = os.path.join(current_path, 'src')
    sys.path.insert(0, package_source_path)

import plorn.base_obj

def test_init():
    '''
    Assume defaults for most things
    '''
    obj = plorn.base_obj.PlornBaseObj('testing')
    assert obj.get_name() == 'testing'
    assert obj.get_id() == None
    assert obj.get_dated() == ''
    assert obj.get_notes() == ''
    assert obj.get_name_list() == []
    assert obj.get_place_list() == []
    assert obj.get_tag_list() == []

def test_using_id():
    '''
    Make sure set/get of id works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing')
    assert obj.get_id() == None
    obj.set_id(12)
    assert obj.get_id() == 12

def test_using_name():
    '''
    Make sure set/get of name works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing')
    assert obj.get_name() == 'testing'
    obj.set_name('bizmumble')
    assert obj.get_name() == 'bizmumble'

def test_using_dated():
    '''
    Make sure set/get of dated works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing')
    assert obj.get_dated() == ''
    obj.set_dated('bizmumble')
    assert obj.get_dated() == 'bizmumble'

def test_using_notes():
    '''
    Make sure set/get of notes works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing')
    assert obj.get_notes() == ''
    obj.set_notes('bizmumble')
    assert obj.get_notes() == 'bizmumble'

def test_basic_name_list():
    '''
    Make sure set/get of name_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'

def test_add_to_name_list():
    '''
    Make sure adding to name_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    obj3 = plorn.base_obj.PlornBaseObj('foobar', id=3)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'
    obj.add_name_to_list(obj3)
    assert obj.get_name_list()[1].get_id() == 3
    assert obj.get_name_list()[1].get_name() == 'foobar'

def test_remove_from_name_list():
    '''
    Make sure removing from name_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    obj3 = plorn.base_obj.PlornBaseObj('foobar', id=3)
    obj4 = plorn.base_obj.PlornBaseObj('blah blah', id=4)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'
    obj.add_name_to_list(obj3)
    assert obj.get_name_list()[1].get_id() == 3
    assert obj.get_name_list()[1].get_name() == 'foobar'
    obj.add_name_to_list(obj4)
    assert obj.get_name_list()[2].get_id() == 4
    assert obj.get_name_list()[2].get_name() == 'blah blah'
    obj.remove_name_from_list(obj3)
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'
    assert obj.get_name_list()[1].get_id() == 4
    assert obj.get_name_list()[1].get_name() == 'blah blah'

def test_basic_place_list():
    '''
    Make sure set/get of place_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'

def test_add_to_place_list():
    '''
    Make sure adding to place_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    obj3 = plorn.base_obj.PlornBaseObj('foobar', id=3)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'
    obj.add_place_to_list(obj3)
    assert obj.get_place_list()[1].get_id() == 3
    assert obj.get_place_list()[1].get_name() == 'foobar'

def test_remove_from_place_list():
    '''
    Make sure removing from place_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    obj3 = plorn.base_obj.PlornBaseObj('foobar', id=3)
    obj4 = plorn.base_obj.PlornBaseObj('blah blah', id=4)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'
    obj.add_place_to_list(obj3)
    assert obj.get_place_list()[1].get_id() == 3
    assert obj.get_place_list()[1].get_name() == 'foobar'
    obj.add_place_to_list(obj4)
    assert obj.get_place_list()[2].get_id() == 4
    assert obj.get_place_list()[2].get_name() == 'blah blah'
    obj.remove_place_from_list(obj3)
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'
    assert obj.get_place_list()[1].get_id() == 4
    assert obj.get_place_list()[1].get_name() == 'blah blah'

def test_basic_tag_list():
    '''
    Make sure set/get of tag_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'

def test_add_to_tag_list():
    '''
    Make sure adding to tag_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    obj3 = plorn.base_obj.PlornBaseObj('foobar', id=3)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'
    obj.add_tag_to_list(obj3)
    assert obj.get_tag_list()[1].get_id() == 3
    assert obj.get_tag_list()[1].get_name() == 'foobar'

def test_remove_from_tag_list():
    '''
    Make sure removing from tag_list works
    '''
    obj = plorn.base_obj.PlornBaseObj('testing', id=1)
    obj2 = plorn.base_obj.PlornBaseObj('bizmumble', id=2)
    obj3 = plorn.base_obj.PlornBaseObj('foobar', id=3)
    obj4 = plorn.base_obj.PlornBaseObj('blah blah', id=4)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'
    obj.add_tag_to_list(obj3)
    assert obj.get_tag_list()[1].get_id() == 3
    assert obj.get_tag_list()[1].get_name() == 'foobar'
    obj.add_tag_to_list(obj4)
    assert obj.get_tag_list()[2].get_id() == 4
    assert obj.get_tag_list()[2].get_name() == 'blah blah'
    obj.remove_tag_from_list(obj3)
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'
    assert obj.get_tag_list()[1].get_id() == 4
    assert obj.get_tag_list()[1].get_name() == 'blah blah'

