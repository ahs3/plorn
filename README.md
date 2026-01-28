# Plorn
**Plorn**: build a catalog of photo albums and the photos they contain

## What's a Plorn?
A long time ago, I read a biography of Charles Dickens and was introduced
to his youngest son, Edward Bullwer Lytton Dickens, named after one of 
Charles' best friends.  For some reason, Edward was given the nickname
"Plorn" by his father.  For further unknown reasons, the word "plorn"
stuck in my wee brain; over time, I've ended up using it for things that
needed a name but I didn't know what they really were.  Surprisingly,
this happens a lot with software projects.  And that's what happened here.

In my office is a stack of boxes collected from relatives that contain
an astonishing number of photographs, some in albums, some loose, but
most of them just tossed into the box.  What I needed was some way
to organize them all.  I also needed some way to find them again whilst
doing genealogical research into my family history.  So, I started
working on a tool to do what I wanted; since I didn't know what it
was going to turn out to be or how it was going to work I ended up
calling it "plorn" as I often do with such things.  This time, the
name stuck.

Being of a somewhat lazy nature, I tried a bunch of existing open
source tools before starting on `plorn`.  All of them had one or more
of these "features" that I did ***not*** want:

* Limited, constrained or non-existent mechanisms for searching through
the cataloged items.
* Limited, constrained or non-existent mechanisms to attach notes to
photos or albums without modifying the photo file.
* Limited, constrained or non-existent mechanisms to assign tags to
photos or albums without modifying the photo file.
* When adding photos to an album, they had to be moved to a specific
location or got duplicated to some other location.

`Plorn` tries to avoid all these by allowing free-form text and user-defined
tags to be attached to photo files that can be anywhere on the system you
would like -- and then allowing you to search through all of those things.
Is it perfect?  Of course not.  Does it do what I wanted?  Mostly; there's
always room for improvement.

## How Does It Work?
`Plorn` knows how to deal with three sorts of things:

1.  Albums: these are data base objects that represent a collection of
    photos, and can be described with some text and/or attributes.  There
    are logical constructs, so no *physical* photo album is required.
2.  Photos: these are also data base objects that point to an image file
    somewhere on your system, and can also be described with some text and/or
    attributes.  They are not copies of the original files, merely pointers
    to them.
3.  Attributes: these are just strings that a user defines to help when
    trying to find albums and photos. There are three types that you can
    define:
    1. Names: since the original intent was for maintaining genealogical
       resources, you can create any number of names to identify photos
       or albums.
    2. Places: similar to Names, these are meant for genealogical data
       to indicate where an album or photo was created.  These are also
       defined by the user.
    3. Tags: these are just labels that can be used however you wish.
       A hierarchical structure can be defined, if desired.

Everything one can do in `plorn` is geared around manipulating one
of these three things -- adding, deleting, or modifying them.

## The User Interface

> [!CAUTION]
> Whilst I designed the user interface, this is not my particular
idiom[^1]; most of my experience has been with Linux kernel C code.
My preference for a "graphical" user interface leans toward a VT100
terminal using `vi`.  You have been warned.

[^1]: Thank you, Monty Python.

The start screen contains a series of tabs, with and without buttons.
Menus aren't used.  Each tab deals with a particular type of object.
The buttons on tabs are operations that can be performed on those
objects.  Here's the defined tabs:

* Albums, with these buttons:
    * info: shows what we currently know about the album
    * add: create a new album object
    * remove: delete the album from the database, including the pointers
      to any photos contained in the album
    * edit: change what we know about the album
    * import: add a set of photos to the selected album
* Photos, with these buttons:
    * an album pull down list to select the album photos to show.
    * info: shows what we currently know about the photo
    * add: create a new photo object
    * remove: delete the photo from the database, and from the album
      that contains it
    * edit: change what we know about the photo
* Attribute tabs for Names, Places and Tags, each with these buttons:
    * expand: toggle expansion of the tree hierarchy (it is collapsed
      by default)
    * add: add an attribute of this type
    * remove: delete an attribute
    * edit: change the attribute
* Search, with these buttons:
    * Clear: reset the search fields to defaults
    * Search: execute the search specified and produce a Search Results screen.
    * Advanced Search: similar to this tab but allow for slightly more
      complicated searches.  This is one of the areas that needs
      improvement over time.
* Settings, with no buttons, just displays the current values of various
  configuration items found in a `plorn.cfg` file; these are pretty
  minimal at this point.

The "clever" bits in the user interface are pretty minimal: if you click
on (i.e., select) an entry on the Album tab, and then select the Photos
tab, the photos shown will be the ones in the selected album.  Also, if
you double click on an entry when viewing Search Results, an info screen
for the item selected will be opened.  That's about it.  The whole point
is to be as simple as possible.

## Initial Use
There is a configuration file.  For now, this file must be
`~/.config/plorn/plorn.cfg`.  You can see the contents of this `.ini`
style file in the Settings tab mentioned above.  There is no need to
create this file; it will be created on first execution of `plorn` if
it does not already exist.

Similarly, an SQLite data base is created on initial startup.  Its
location is given in the configuration file, but defaults to
`~/.local/share/plorn/plorn.db`.  Note that `~/.local/share/plorn`
is also used by default to store thumbnail images of the photos

## Changing File System Locations
If you want to have the data base to be somewhere else, start up `plorn`
once then exit it.  Next, move the directory `~/.local/share/plorn` to
wherever you would like it to be; again, note that image thumbnails
will also be stored in this directory.  Finally, edit the configuration
file to show the new path in `data_dir` and optionally change the
`dbname` value to change the name of the data base itself.

For now, the configuration file needs to stay in the same location.
If there is a `plorn.cfg` file in the current working directory, it
will be used instead.

If you open an editor and create the file `~/.config/plorn/plorn.cfg`
(or `./plorn.cfg`) you can acheive the same goal, as long as it looks
something like this:

    [plorn]
    user = myusername
    full_name = My Full Name
    config_dir = /my_configuration_file_directory
    data_dir = /my_plorn_data_directory
    dbname = my_db_name.db

## Licensing Information
All Python code for the Plorn project is:

    Copyright (c) 2026, Albert H. Stone, III <ahs3@ahs3.net>

and is licensed under the terms of the GNU General Public License
Version 3 or later[^2].

[^2]: See the file `COPYING`.

The file `plorn_app.png` is a copy of a photograph from the Charles
Dickens Museum, 48-49 Doughty Street, London WC1N 2LX, England.  It
was originally found on
[Victorian Web](https://victorianweb.org/victorian/authors/dickens/family/child10.html).
The image was also used in the book **Charles Dickens: Dickens' Bicentenary
1812-2012**[^3].  The photograph in the book was taken circa 1868 and
is of Charles Dickens' son, Edward "Plorn" Dickens when he was about
sixteen years old.  Ownership is unclear; the Charles Dickens Museum,
who is credited with providing the picture used in the book, does not
know where this picture is currently and says they may or may not
have it.  Ms. Hawksley, who is also a member of the Museum, said I
should ask the museum about re-use of the photograph -- who in turn
pointed me to Ms. Hawksley.  Given the age of the original, it is most
likely in the public domain, but I cannot prove or disprove that.  The
photo is only used in one place and may easily be replaced (see
`PLORN_PHOTO_PATH` in the file `plorn_config.py`) if this becomes an issue.

[^3]: **Charles Dickens: Dickens' Bicentenary 1812-2012**,
 Lucinda Dickens Hawksley, copyright 2011 Lucinda Hawksley,
 Insight Editions, San Rafael, California, ISBN 978-1-60887-052-3.  See
 page 35.

The red X icon used in the search results (checkbox.png) is from:
	
	https://www.flaticon.com/free-icons/incorrect
	Incorrect icons created by heisenberg_jr - Flaticon

The green check mark (tick mark) in the search results (`red-x.png`) is
borrowed from the Linux Mint desktop icons and is distributed under
the terms of GPL-3.0-or later, as is this project.

The plus and minus icons used when adding or removing attributes (files
`list-add.png` and `list-remove.png`) are borrowed from the GNOME project,
and are re-used under the terms of GPL-3.0-or-later, as is this project.

