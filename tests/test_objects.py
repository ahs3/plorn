
#######################################################################
# Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################

import pytest

from plorn import (
    PlornBaseObj, PlornAttr,
    PlornName, PlornPlace, PlornTag,
    PlornAlbum, PlornPhoto,
)

#-- test base objects 
def test_base_init():
    '''
    Assume defaults for most things
    '''
    obj = PlornBaseObj('testing')
    assert obj.get_name() == 'testing'
    assert obj.get_id() == None
    assert obj.get_dated() == ''
    assert obj.get_notes() == ''
    assert obj.get_name_list() == []
    assert obj.get_place_list() == []
    assert obj.get_tag_list() == []

def test_base_using_id():
    '''
    Make sure set/get of id works
    '''
    obj = PlornBaseObj('testing')
    assert obj.get_id() == None
    obj.set_id(12)
    assert obj.get_id() == 12

def test_base_using_name():
    '''
    Make sure set/get of name works
    '''
    obj = PlornBaseObj('testing')
    assert obj.get_name() == 'testing'
    obj.set_name('bizmumble')
    assert obj.get_name() == 'bizmumble'

def test_base_using_dated():
    '''
    Make sure set/get of dated works
    '''
    obj = PlornBaseObj('testing')
    assert obj.get_dated() == ''
    obj.set_dated('bizmumble')
    assert obj.get_dated() == 'bizmumble'

def test_base_using_notes():
    '''
    Make sure set/get of notes works
    '''
    obj = PlornBaseObj('testing')
    assert obj.get_notes() == ''
    obj.set_notes('bizmumble')
    assert obj.get_notes() == 'bizmumble'

def test_base_name_list():
    '''
    Make sure set/get of name_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'

def test_base_add_to_name_list():
    '''
    Make sure adding to name_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    obj3 = PlornBaseObj('foobar', id=3)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'
    obj.add_name_to_list(obj3)
    assert obj.get_name_list()[1].get_id() == 3
    assert obj.get_name_list()[1].get_name() == 'foobar'

def test_base_remove_from_name_list():
    '''
    Make sure removing from name_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    obj3 = PlornBaseObj('foobar', id=3)
    obj4 = PlornBaseObj('blah blah', id=4)
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

def test_base_place_list():
    '''
    Make sure set/get of place_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'

def test_base_add_to_place_list():
    '''
    Make sure adding to place_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    obj3 = PlornBaseObj('foobar', id=3)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'
    obj.add_place_to_list(obj3)
    assert obj.get_place_list()[1].get_id() == 3
    assert obj.get_place_list()[1].get_name() == 'foobar'

def test_base_remove_from_place_list():
    '''
    Make sure removing from place_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    obj3 = PlornBaseObj('foobar', id=3)
    obj4 = PlornBaseObj('blah blah', id=4)
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

def test_base_tag_list():
    '''
    Make sure set/get of tag_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'

def test_base_add_to_tag_list():
    '''
    Make sure adding to tag_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    obj3 = PlornBaseObj('foobar', id=3)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'
    obj.add_tag_to_list(obj3)
    assert obj.get_tag_list()[1].get_id() == 3
    assert obj.get_tag_list()[1].get_name() == 'foobar'

def test_base_remove_from_tag_list():
    '''
    Make sure removing from tag_list works
    '''
    obj = PlornBaseObj('testing', id=1)
    obj2 = PlornBaseObj('bizmumble', id=2)
    obj3 = PlornBaseObj('foobar', id=3)
    obj4 = PlornBaseObj('blah blah', id=4)
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

#-- test PlornAlbum objects 
def test_album_init():
    '''
    Assume defaults for most things
    '''
    obj = PlornAlbum('testing')
    assert obj.get_name() == 'testing'
    assert obj.get_id() == None
    assert obj.get_dated() == ''
    assert obj.get_notes() == ''
    assert obj.get_name_list() == []
    assert obj.get_place_list() == []
    assert obj.get_tag_list() == []

def test_album_using_id():
    '''
    Make sure set/get of id works
    '''
    obj = PlornAlbum('testing')
    assert obj.get_id() == None
    obj.set_id(12)
    assert obj.get_id() == 12

def test_album_using_name():
    '''
    Make sure set/get of name works
    '''
    obj = PlornAlbum('testing')
    assert obj.get_name() == 'testing'
    obj.set_name('bizmumble')
    assert obj.get_name() == 'bizmumble'

def test_album_using_dated():
    '''
    Make sure set/get of dated works
    '''
    obj = PlornAlbum('testing')
    assert obj.get_dated() == ''
    obj.set_dated('bizmumble')
    assert obj.get_dated() == 'bizmumble'

def test_album_using_notes():
    '''
    Make sure set/get of notes works
    '''
    obj = PlornAlbum('testing')
    assert obj.get_notes() == ''
    obj.set_notes('bizmumble')
    assert obj.get_notes() == 'bizmumble'

def test_album_name_list():
    '''
    Make sure set/get of name_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'

def test_album_add_to_name_list():
    '''
    Make sure adding to name_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    obj3 = PlornAlbum('foobar', id=3)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'
    obj.add_name_to_list(obj3)
    assert obj.get_name_list()[1].get_id() == 3
    assert obj.get_name_list()[1].get_name() == 'foobar'

def test_album_remove_from_name_list():
    '''
    Make sure removing from name_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    obj3 = PlornAlbum('foobar', id=3)
    obj4 = PlornAlbum('blah blah', id=4)
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

def test_album_place_list():
    '''
    Make sure set/get of place_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'

def test_album_add_to_place_list():
    '''
    Make sure adding to place_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    obj3 = PlornAlbum('foobar', id=3)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'
    obj.add_place_to_list(obj3)
    assert obj.get_place_list()[1].get_id() == 3
    assert obj.get_place_list()[1].get_name() == 'foobar'

def test_album_remove_from_place_list():
    '''
    Make sure removing from place_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    obj3 = PlornAlbum('foobar', id=3)
    obj4 = PlornAlbum('blah blah', id=4)
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

def test_album_tag_list():
    '''
    Make sure set/get of tag_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'

def test_album_add_to_tag_list():
    '''
    Make sure adding to tag_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    obj3 = PlornAlbum('foobar', id=3)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'
    obj.add_tag_to_list(obj3)
    assert obj.get_tag_list()[1].get_id() == 3
    assert obj.get_tag_list()[1].get_name() == 'foobar'

def test_album_remove_from_tag_list():
    '''
    Make sure removing from tag_list works
    '''
    obj = PlornAlbum('testing', id=1)
    obj2 = PlornAlbum('bizmumble', id=2)
    obj3 = PlornAlbum('foobar', id=3)
    obj4 = PlornAlbum('blah blah', id=4)
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

#-- test PlornPhoto objects 
def test_photo_init():
    '''
    Assume defaults for most things
    '''
    obj = PlornPhoto('testing')
    assert obj.get_name() == 'testing'
    assert obj.get_id() == None
    assert obj.get_dated() == ''
    assert obj.get_notes() == ''
    assert obj.get_name_list() == []
    assert obj.get_place_list() == []
    assert obj.get_tag_list() == []

def test_photo_using_id():
    '''
    Make sure set/get of id works
    '''
    obj = PlornPhoto('testing')
    assert obj.get_id() == None
    obj.set_id(12)
    assert obj.get_id() == 12

def test_photo_using_name():
    '''
    Make sure set/get of name works
    '''
    obj = PlornPhoto('testing')
    assert obj.get_name() == 'testing'
    obj.set_name('bizmumble')
    assert obj.get_name() == 'bizmumble'

def test_photo_using_dated():
    '''
    Make sure set/get of dated works
    '''
    obj = PlornPhoto('testing')
    assert obj.get_dated() == ''
    obj.set_dated('bizmumble')
    assert obj.get_dated() == 'bizmumble'

def test_photo_using_notes():
    '''
    Make sure set/get of notes works
    '''
    obj = PlornPhoto('testing')
    assert obj.get_notes() == ''
    obj.set_notes('bizmumble')
    assert obj.get_notes() == 'bizmumble'

def test_photo_name_list():
    '''
    Make sure set/get of name_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'

def test_photo_add_to_name_list():
    '''
    Make sure adding to name_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    obj3 = PlornPhoto('foobar', id=3)
    assert obj.get_name_list() == []
    obj.set_name_list([obj2])
    assert obj.get_name_list()[0].get_id() == 2
    assert obj.get_name_list()[0].get_name() == 'bizmumble'
    obj.add_name_to_list(obj3)
    assert obj.get_name_list()[1].get_id() == 3
    assert obj.get_name_list()[1].get_name() == 'foobar'

def test_photo_remove_from_name_list():
    '''
    Make sure removing from name_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    obj3 = PlornPhoto('foobar', id=3)
    obj4 = PlornPhoto('blah blah', id=4)
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

def test_photo_place_list():
    '''
    Make sure set/get of place_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'

def test_photo_add_to_place_list():
    '''
    Make sure adding to place_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    obj3 = PlornPhoto('foobar', id=3)
    assert obj.get_place_list() == []
    obj.set_place_list([obj2])
    assert obj.get_place_list()[0].get_id() == 2
    assert obj.get_place_list()[0].get_name() == 'bizmumble'
    obj.add_place_to_list(obj3)
    assert obj.get_place_list()[1].get_id() == 3
    assert obj.get_place_list()[1].get_name() == 'foobar'

def test_photo_remove_from_place_list():
    '''
    Make sure removing from place_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    obj3 = PlornPhoto('foobar', id=3)
    obj4 = PlornPhoto('blah blah', id=4)
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

def test_photo_tag_list():
    '''
    Make sure set/get of tag_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'

def test_photo_add_to_tag_list():
    '''
    Make sure adding to tag_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    obj3 = PlornPhoto('foobar', id=3)
    assert obj.get_tag_list() == []
    obj.set_tag_list([obj2])
    assert obj.get_tag_list()[0].get_id() == 2
    assert obj.get_tag_list()[0].get_name() == 'bizmumble'
    obj.add_tag_to_list(obj3)
    assert obj.get_tag_list()[1].get_id() == 3
    assert obj.get_tag_list()[1].get_name() == 'foobar'

def test_photo_remove_from_tag_list():
    '''
    Make sure removing from tag_list works
    '''
    obj = PlornPhoto('testing', id=1)
    obj2 = PlornPhoto('bizmumble', id=2)
    obj3 = PlornPhoto('foobar', id=3)
    obj4 = PlornPhoto('blah blah', id=4)
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

#-- test PlornAttr base object
def test_attr_init():
    '''
    Assume defaults for everything
    '''
    obj = PlornAttr('fred')
    assert obj.get_id() == None
    assert obj.get_value() == 'fred'
    assert obj.get_parent_id() == None
    assert obj.get_db_table_name() == ''

def test_attr_set():
    '''
    Assume defaults for everything
    '''
    obj = PlornAttr('fred')
    assert obj.get_value() == 'fred'

    obj.set_value('barney')
    assert obj.get_value() == 'barney'
    obj.set_id(112)
    assert obj.get_id() == 112
    obj.set_parent_id(93)
    assert obj.get_parent_id() == 93
    obj.set_db_table_name('eleanor')
    assert obj.get_db_table_name() == 'eleanor'

#-- test PlornName object
def test_name_init():
    '''
    Assume defaults for everything
    '''
    obj = PlornName('fred')
    assert obj.get_id() == None
    assert obj.get_value() == 'fred'
    assert obj.get_parent_id() == 0
    assert obj.get_db_table_name() == 'names'

def test_name_set():
    '''
    Assume defaults for everything
    '''
    obj = PlornName('fred')
    assert obj.get_value() == 'fred'

    obj.set_value('barney')
    assert obj.get_value() == 'barney'
    obj.set_id(112)
    assert obj.get_id() == 112
    obj.set_parent_id(93)
    assert obj.get_parent_id() == 93
    obj.set_db_table_name('eleanor')
    assert obj.get_db_table_name() == 'names'

#-- test PlornPlace object
def test_place_init():
    '''
    Assume defaults for everything
    '''
    obj = PlornPlace('fred')
    assert obj.get_id() == None
    assert obj.get_value() == 'fred'
    assert obj.get_parent_id() == 0
    assert obj.get_db_table_name() == 'places'

def test_place_set():
    '''
    Assume defaults for everything
    '''
    obj = PlornPlace('fred')
    assert obj.get_value() == 'fred'

    obj.set_value('barney')
    assert obj.get_value() == 'barney'
    obj.set_id(112)
    assert obj.get_id() == 112
    obj.set_parent_id(93)
    assert obj.get_parent_id() == 93
    obj.set_db_table_name('eleanor')
    assert obj.get_db_table_name() == 'places'

#-- test PlornTag object
def test_tag_init():
    '''
    Assume defaults for everything
    '''
    obj = PlornTag('fred')
    assert obj.get_id() == None
    assert obj.get_value() == 'fred'
    assert obj.get_parent_id() == 0
    assert obj.get_db_table_name() == 'tags'

def test_tag_set():
    '''
    Assume defaults for everything
    '''
    obj = PlornTag('fred')
    assert obj.get_value() == 'fred'

    obj.set_value('barney')
    assert obj.get_value() == 'barney'
    obj.set_id(112)
    assert obj.get_id() == 112
    obj.set_parent_id(93)
    assert obj.get_parent_id() == 93
    obj.set_db_table_name('eleanor')
    assert obj.get_db_table_name() == 'tags'

