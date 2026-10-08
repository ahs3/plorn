
[^comment]: SPDX-License-Identifier: CC-BY-4.0

# Plorn
**plorn**: build catalogs of photo albums and the photos they contain

## Table of Contents

1. [What Is A Plorn?](#what-is-a-plorn)
2. [How Does It Work?](#how-does-it-work)
3. [Current State of Development](#current-state-of-development)
4. [The User Interface](#the-user-interface)
5. [Initial Use](#initial-use)
6. [The Configuration File](#the-configuration-file)
7. [Changing File System Locations](#changing-file-system-locations)
8. [Installation](#installation)
9. [Licenses](#licenses)

<a id="what-is-a-plorn"></a>
## What Is a Plorn?
<table border=0>
<tr>
<td width="55%">
<p>A long time ago, I read a biography of Charles Dickens and was introduced
to his youngest son, Edward Bullwer Lytton Dickens, named after one of 
Charles' best friends.  For some reason, Edward was given the nickname
"Plorn" by his father.  For further unknown reasons, the word "plorn"
stuck in my wee brain; over time, I've ended up using it for things that
needed a name but I didn't know what they really were.  Surprisingly,
this happens a lot with software projects.  And that's what happened here.
</p>

<p>In my office are stacks of boxes collected from relatives that contain
an astonishing number of photographs, some in albums, some loose, but
most of them just tossed into a box.  What I needed was some way
to organize them all.  I also needed some way to find them again whilst
doing genealogical research into my family history.  So, I started
working on a tool to do what I wanted; since I didn't know what it
was going to turn out to be or how it was going to work I ended up
calling it "plorn" as I often do with such things.  This time, the
name stuck.
</p>
</td>
<td>
<div style="float: right">
    <figure>
        <img 
        src="https://github.com/ahs3/plorn/blob/5d452416d7fd6072d04611f6fdbf3d66ee7a8783/src/plorn/plorn_app.png"
        alt="Photo of Plorn, courtesy of the Charles Dickens Museum, London"
        height=320 width=200>
        <figcaption>Photo of Plorn,<br>courtesy Charles Dickens Museum,<br>
                    London, England
        </figcaption>
    </figure>
</div>
</td>
</tr>
</table>

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

<a id="how-does-it-work"></a>
## How Does It Work?
`Plorn` knows how to deal with four sorts of things:

1.  Catalogs: these contain albums; underneath, they are simply a name,
    and locations for key files used by the application.
2.  Albums: these are data base objects that represent a collection of
    photos, and can be described with some text and/or attributes.  There
    are logical constructs, so no *physical* photo album is required.
3.  Photos: these are also data base objects that point to an image file
    somewhere on your system, and can also be described with some text and/or
    attributes.  They are not copies of the original files, merely pointers
    to them.
4.  Attributes: these are just strings that a user defines to help when
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
of these four things -- adding, deleting, or modifying them.

<a id="current-state-of-development"></a>
## Current State of Development
At this stage, there are a lot of functions that have not yet been
implemented.  Unfortunately, the one big thing is the search function.
However, managing catalogs, albums and photos work reasonably well; I'm
sure there are still lots of bugs given my inexperience with user
interfaces, but I'm getting better [^1]

[^1]: Thank you, Monty Python.

<a id="the-user-interface"></a>
## The User Interface

> [!CAUTION]
> Whilst I designed the user interface, this is not my particular
idiom[^2]; most of my experience has been with Linux kernel C code.
My preference for a "graphical" user interface leans toward a VT100
terminal using `vi`.  You have been warned.

[^2]: Um, Ibid.

The start screen contains a list of all the albums and photos in the
*current catalog*.  You can have as many catalogs as you wish, but 'plorn'
only handles working with one catalog at a time.

This is where menus come in: the first drop-down menu is "Catalogs".
That drop-down lets you mess with catalogs:

* New: creates a new catalog (which is actually just an entry in the
  configuration file).  Optionally, you can set the new catalog to be
  the default, or to be the current catalog, or both.
* Open: select a previously defined catalog and make that the currently
  open catalog.
* Delete: select a previously defined catalog and remove it.  Note that
  ***no*** files actually get removed -- neither the database with
  all the album and photo information, nor the photos themselves; the
  only thing removed is the entry for the catalog in the configuration
  file.

The start screen contains additional menus for "Albums", "Photos",
"Attributes", "Tools", and "Help":

* Albums, with these choices:
    * View: shows what we currently know about the album
    * Add: create a new album in the current catalog
    * Edit: change what we know about the album
    * Manage Photos: add or remove photos from an album
    * Remove: delete the album from the database, including the pointers
      to any photos contained in the album
    * Slide Show: this has not been implemented yet, but the idea would be
      to present the photos in an album in a preferred order using the photo
      notes as descriptive text.
* Photos, with these choices; you will have to select a photo first for
  each of these:
    * View: shows what we currently know about the photo
    * Add: create a new photo in one of the albums in the catalog
    * Edit: change what we know about the photo
    * Remove: delete the pointer to the photo from the database, and from
      the album that contains it; this does not affect the original photo
      in any way.
* Attributes: choose among the types of attributes -- Names, Places, or Tags.
  Each of these choices will take you to a dialog allowing you to see the
  currently defined values, but also add, edit, or remove them.  If an
  attribute is renamed, it is renamed for all uses of it; if an attribute
  is removed, it is removed from wherever it has been used.  On the other
  hand, you have to specifically add an attribute to any photo or album.
* Tools, with these choices:
    * Search: unfortunately, not implemented yet, but the idea would be to
      allow for the searching of all text fields in the current catalog.
    * Raw Database Tables: show the content of any of the internal database
      tables; this is really only useful as a debugging feature and is does
      not allow you to change any of the content.
    * Check Catalog Structues: not implemented yet, but the intent is to
      perform some basic sanity checks on the content of the catalog -- are
      photos listed actually readable, for example.
    * Preferences: also to be implmented, and for displaying the current
      values of various configuration items found in a `plorn.cfg` file;
      these are pretty minimal at this point.
* Help, with these choices:
    * Help, which displays this manual, such as it is.
    * About, providing basic info about the `plorn` itself.

There are only a couple of "clever" bits in the user interface.  If you
double click on an album or photo, you will be taken to the current view
of that object -- the same as if you had used one of the drop-down menu
View choices.  If you right click the mouse, you will get most of the same
options as the drop-menus, but tailored to the nearest photo or album.
Finally, the keyboard combination of `cntrl-q` will exit the application.

<a id="initial-use"></a>
## Initial Use
There is a configuration file called `~/.config/plorn/plorn.cfg`.  You
can see the contents of this `.ini` style file via the Preference 
menu choice mentioned above.  There is no need to create this file; it
will be created on first execution of `plorn` if it does not already exist.

Similarly, a default catalog named "Plorn" is created, with an SQLite
database to go along with it, on initial startup.  Its location is given
in the configuration file, but defaults to
`~/.local/share/plorn/plorn.db`.  This catalog is also set as the current
and default catalogs.

<a id="the-configuration-file"></a>
## The Configuration File
The content of the configuration file is very simple `.ini` file format.
In general, it will look something like this:

```
    [DEFAULT]
    user = my_username
    full_name = My Full Name
    config_dir = /my_home_dir/.config/plorn
    data_dir = /my_home_dir/.local/share/plorn
    default_catalog = Plorn
    current_catalog = Plorn

    [gui]
    default_photo = plorn_app.png
    last_directory_selected = /my_home_dir/Pictures/last-week

    [Plorn]
    name = Plorn
    dbname = plorn.db

    [wilma]
    name = wilma
    dbname = wilma.catalog
```
The `DEFAULT` section is precisely that -- default values for the entire
application.  Note that only the `data_dir` option can be overriden, and
only in a catalog section.  These are pretty self-explanatory.

The `gui` section affects the behavior of the user interface.  The
`default_photo` is used as the application icon, and a place holder when
a photo is needed but none is supplied.  The `last_directory_selected`
keeps track of where the user has been when adding photos so they don't
have to keep retracing their path.
    
The `Plorn` and `wilma` sections are catalogs.  Yup, that's all a catalog
is: a name and a database name.  If a catalog section contains a `data_dir`
value, that will override the default and the database will be stored in
that directory.

If you would rather use a different configuration, you can always edit
an existing file, or create one from scratch -- as long as it ends up in
`~/.config/plorn/plorn.cfg`.

<a id="changing-file-system-locations"></a>
## Changing File System Locations
There are two mechanisms for changing where `plorn` data is stored: (1)
edit the configuration file directly, or (2) the preferred mechanism of
creating a new catalog.  Either way works; you just need to be more careful
when editing the configuration file.

When creating a catalog, you define the name of the catalog, the name
of the database, and optionally the path to the directory to contain the
database.  If you do not specify a path, the default data_dir value is
used -- usually, `~/.local/share/plorn`.

If you want to move the database somewhere else for an existing catalog,
you can edit the configuration file directly.  Find the catalog section
in the configuration file (see the `[wilma]` example above) and add
a `data_dir` value for the location you want to use -- or change an
existing value, if there is one.  Save your changes.  Then, move the
database from wherever it was before to the newly specified location.
The database name can also be changed, if desired, when editing the
configuration file.  When restarted, `plorn` will use the new entries.

This can also be done in the application itself by first removing the
catalog with the database to be moved, and then creating a new catalog
with the new location, or any other changes.  When removing a catalog,
the only actual change is that the entry in the configuration file is
removed; databases, directories, albums, and photos, remain untouched.
Hence, you will have to move the old database to the new location by hand,
if this method is used.

<a id="installation"></a>
## Installation
Until someone makes a distribution ready package for `plorn`, the
easiest way to install it is this:

```
    $ pip install plorn
```
All my development -- and testing -- has occurred on a Linux laptop
running fairly recent Fedora releases.  I do not know yet if things
work the same on other distributions and I have not tried other operating
systems.  At least not yet; the plan is to port to MacOS someday.

In theory, the Python code used in `plorn` is reasonably OS agnostic.
In reality, theory is never quite right.

Source is always available via:

```
    $ git clone https://codeberg.org/ahs3/plorn.git
```
Improvements and suggestions are always welcome; if I knew how to do
everything exactly right, I probably wouldn't have to work for a living.

<a id="licenses"></a>
## Licenses
See the licensing information in the source file `LICENSES`.

