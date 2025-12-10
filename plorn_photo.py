import copy
import filetype
import logging
import os
from PIL import Image as pilImage
from PIL import ImageTk

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox

import plorn_attr
import plorn_base_obj
import plorn_common
import plorn_config
from plorn_config import FONTSIZE
import plorn_db

module_logger = logging.getLogger('plorn.photo')
module_logger.setLevel(logging.DEBUG)

class PlornPhoto(plorn_base_obj.PlornBaseObj):
    def __init__(self, name, id=None, album_id=None,
                 path='', dated='', notes='', thumbnail='',
                 names=[], places=[], tags=[]):
        self.album_id = album_id
        self.path = path
        self.thumbnail = thumbnail
        super().__init__(name, id, dated, notes, names, places, tags)
        module_logger.debug('initializing photo object: ' + str(self))

    def set_path(self, path):
        self.path = path

    def get_path(self):
        return self.path

    def set_album_id(self, album_id):
        self.album_id = album_id

    def get_album_id(self):
        return self.album_id

    def set_thumbnail(self, thumbnail):
        self.thumbnail = thumbnail

    def get_thumbnail(self):
        return self.thumbnail

    def __str__(self):
        val  = f'id: \'{self.id}\''
        val += f', name: \'{self.name}\''
        val += f', path: \'{self.path}\''
        val += f', dated: \'{self.dated}\''
        val += f', notes: \'{self.notes}\''
        val += f', thumbnail: \'{self.thumbnail}\''
        return val

class PlornPhotoLeftFrame:
    '''
    Factor out common code for building the left frame for building
    responses to commands on the photo notebook tab
    '''
    def __init__(self, db, parent, album=None, photo=None,
                 default_state='normal'):
        self.db = db
        self.parent = parent
        self.album = album
        self.photo = photo
        self.default_state = default_state
        self.tfont=font.nametofont('TkDefaultFont')
        self.lframe = ttk.Frame(self.parent, padding='10 10 10 10')
        self.lframe.columnconfigure(0, weight=1)
        self.lframe.columnconfigure(1, weight=2)
        for ii in range(0,7):
            self.lframe.rowconfigure(ii, weight=1)

        self.lab1 = ttk.Label(self.lframe, width=10, text='Album:')
        self.lab1.grid(column=0, row=0, sticky=(W))
        self.album_name = StringVar(self.lframe, value='')
        if self.album != None:
            self.album_name.set(self.album.get_name())
        self.album_entry = ttk.Entry(self.lframe, width=40,
                                     textvariable=self.album_name,
                                     font=self.tfont, state='readonly')
        self.album_entry.grid(column=1, row=0, sticky=(W))
        self.album_entry.focus_set()

        self.lab2 = ttk.Label(self.lframe, width=10, text='Name:')
        self.lab2.grid(column=0, row=1, sticky=(W))
        self.photo_name = StringVar(self.lframe, value='')
        if self.photo != None:
            self.photo_name.set(self.photo.get_name())
        self.name_entry = ttk.Entry(self.lframe, width=40,
                                    textvariable=self.photo_name,
                                    font=self.tfont, state=self.default_state)
        self.name_entry.grid(column=1, row=1, sticky=(W))

        self.lab3 = ttk.Label(self.lframe, width=10, text='Path:')
        self.lab3.grid(column=0, row=2, sticky=(W))
        self.photo_path = StringVar(self.lframe, value='')
        if self.photo != None:
            self.photo_path.set(self.photo.get_path())
        self.path_entry = ttk.Entry(self.lframe, width=40,
                                    textvariable=self.photo_path,
                                    font=self.tfont,
                                    state='readonly')
        self.path_entry.grid(column=1, row=2, sticky=(W))

        self.lab4 = ttk.Label(self.lframe, width=10, text='Dated:')
        self.lab4.grid(column=0, row=3, sticky=(W))
        self.dated = StringVar(self.lframe, value='')
        if self.photo != None:
            self.dated.set(self.photo.get_dated())
        self.date_entry = ttk.Entry(self.lframe, width=40,
                                    textvariable=self.dated,
                                    font=self.tfont, state=self.default_state)
        self.date_entry.grid(column=1, row=3, sticky=(W))

        self.lab5 = ttk.Label(self.lframe, width=10, text='Notes:')
        self.lab5.grid(column=0, row=4, sticky=(N, W))
        self.notes = Text(self.lframe, height=10, width=40, font=self.tfont)
        if self.photo != None:
            self.notes.insert('1.0', self.photo.get_notes())
        self.note_state = 'normal'
        if self.default_state == 'readonly':
            self.note_state = 'disabled'
        self.notes.configure(state=self.note_state)
        self.notes.grid(column=1, row=4, sticky=(N, W, E, S))

    def get_frame(self):
        return self.lframe

    def get_album_name(self):
        return self.album_name.get()

    def get_photo_name(self):
        return self.photo_name.get()

    def get_path(self):
        return self.photo_path.get()

    def get_dated(self):
        return self.dated.get()

    def get_notes(self):
        return self.notes.get('1.0', END)


class PhotoCanvas:
    def __init__(self, parent, path, width=600, height=450):
        self.canvas = Canvas(parent, width=width, height=height)
        self.img = pilImage.open(path)
        self.img.thumbnail((width,height), pilImage.Resampling.LANCZOS)
        self.canvas_img = ImageTk.PhotoImage(image=self.img)
        self.canvas.create_image(10, 10, anchor=NW, image=self.canvas_img)

    def get_canvas(self):
        return self.canvas


class PlornShowPhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug('started PlornShowPhoto')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.photo = self.db.get_photo(photo_id)
        self.album = self.db.get_album(self.photo.get_album_id())

        self.geometry('1600x600')
        self.title('Photo Info')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        self.lframe = PlornPhotoLeftFrame(self.db, self, album=self.album,
                                          photo=self.photo,
                                          default_state='readonly')
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn_common.PlornAttrFrame(self.db, self,
                base_obj=self.photo,
                get_name_list=self.db.get_names_for_photo,
                get_place_list=self.db.get_places_for_photo,
                get_tag_list=self.db.get_tags_for_photo,
                edit_lists=False,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))
        self.rframe.set_name_commands(self.add_name, self.remove_name)
        self.rframe.set_place_commands(self.add_place, self.remove_place)
        self.rframe.set_tag_commands(self.add_tag, self.remove_tag)

        self.canvas = PhotoCanvas(self, self.photo.get_path(),
                                  width=600, height=450)
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE, padx=(20,20))

        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))

        self.bdone = ttk.Button(self, text='Done', command=self.destroy)
        self.bdone.grid(column=2, row=3)

    def add_name(self):
        global module_logger

        name_list = self.db.get_all_names()
        selectone = plorn_attr.PlornSelectAttr('Name', table_name='names',
                                               attr_list=name_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        name = self.db.get_name(entry['id'])
        self.photo.add_name_to_list(name)
        self.rframe.set_name_listbox_values(self.photo.get_name_list())
        module_logger.debug('add name, selected: ' + str(name))

    def remove_name(self):
        global module_logger

        name = self.rframe.get_name_listbox_value()
        module_logger.debug(f'remove_name: {str(name)}')
        if name == None:
            messagebox.showinfo(parent=self,
                                title='Remove Name from Photo',
                                message='No name selected',
                                detail='Please select a name to remove',
                               )
        else:
            self.photo.remove_name_from_list(name)
            self.rframe.set_name_listbox_values(self.photo.get_name_list())

    def add_place(self):
        global module_logger

        place_list = self.db.get_all_places()
        selectone = plorn_attr.PlornSelectAttr('Place', table_name='places',
                                               attr_list=place_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        place = self.db.get_place(entry['id'])
        self.photo.add_place_to_list(place)
        self.rframe.set_place_listbox_values(self.photo.get_place_list())
        module_logger.debug('add place, selected: ' + str(place))

    def remove_place(self):
        global module_logger

        place = self.rframe.get_place_listbox_value()
        module_logger.debug(f'remove_place: {str(place)}')
        if place == None:
            messagebox.showinfo(parent=self,
                                title='Remove Place from Photo',
                                message='No place selected',
                                detail='Please select a place to remove',
                               )
        else:
            self.photo.remove_place_from_list(place)
            self.rframe.set_place_listbox_values(self.photo.get_place_list())

    def add_tag(self):
        global module_logger

        tag_list = self.db.get_all_tags()
        selectone = plorn_attr.PlornSelectAttr('Tag', table_name='tags',
                                               attr_list=tag_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        tag = self.db.get_tag(entry['id'])
        self.photo.add_tag_to_list(tag)
        self.rframe.set_tag_listbox_values(self.photo.get_tag_list())
        module_logger.debug('add tag, selected: ' + str(tag))

    def remove_tag(self):
        global module_logger

        tag = self.rframe.get_tag_listbox_value()
        module_logger.debug(f'remove_tag: {str(tag)}')
        if tag == None:
            messagebox.showinfo(parent=self,
                                title='Remove Tag from Photo',
                                message='No tag selected',
                                detail='Please select a tag to remove',
                               )
        else:
            self.photo.remove_tag_from_list(tag)
            self.rframe.set_tag_listbox_values(self.photo.get_tag_list())


class PlornRemovePhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug('started PlornRemovePhoto')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.photo = self.db.get_photo(photo_id)
        self.album = self.db.get_album(self.photo.get_album_id())

        self.geometry('1600x600')
        self.title('Photo Info')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        self.lframe = PlornPhotoLeftFrame(self.db, self, album=self.album,
                                          photo=self.photo,
                                          default_state='readonly')
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn_common.PlornAttrFrame(self.db, self,
                base_obj=self.photo,
                get_name_list=self.db.get_names_for_photo,
                get_place_list=self.db.get_places_for_photo,
                get_tag_list=self.db.get_tags_for_photo,
                edit_lists=False,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))

        self.canvas = PhotoCanvas(self, self.photo.get_path(),
                                  width=600, height=450)
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE, padx=(20,20))

        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))

        self.bcancel = ttk.Button(self, text='Cancel', command=self.destroy)
        self.bcancel.grid(column=0, row=3)
        self.bremove = ttk.Button(self, text='Remove',
                                  command=self.confirm_remove)
        self.bremove.grid(column=1, row=3)

    def confirm_remove(self):
        photo_name = self.photo.get_name()
        photo_path = self.photo.get_path()
        result = messagebox.askyesnocancel('Confirm Removal',
                    message=f'Remove photo {photo_name}?',
                    detail='Only removes the catalog entry, not the file.',
                    parent=self,
                 )
        if result is True:
            self.db.remove_photo_by_id(self.photo.get_id())
            self.destroy()

class PlornEditPhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug('started PlornEditPhoto')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.photo_id = photo_id
        self.photo = self.db.get_photo(photo_id)
        self.album = self.db.get_album(self.photo.get_album_id())

        self.geometry('1600x600')
        self.title('Edit Photo')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        self.lframe = PlornPhotoLeftFrame(self.db, self, album=self.album,
                                          photo=self.photo,
                                          default_state='normal')
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn_common.PlornAttrFrame(self.db, self,
                base_obj=self.photo,
                get_name_list=self.db.get_names_for_photo,
                get_place_list=self.db.get_places_for_photo,
                get_tag_list=self.db.get_tags_for_photo,
                edit_lists=True,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))
        self.rframe.set_name_commands(self.add_name, self.remove_name)
        self.rframe.set_place_commands(self.add_place, self.remove_place)
        self.rframe.set_tag_commands(self.add_tag, self.remove_tag)

        self.canvas = PhotoCanvas(self, self.photo.get_path(),
                                  width=600, height=450)
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE, padx=(20,20))

        self.bupdate = ttk.Button(self, text='Update',
                                  command=self.update_photo)
        self.bupdate.grid(column=0, row=4)
        self.bcancel = ttk.Button(self, text='Cancel', command=self.destroy)
        self.bcancel.grid(column=1, row=4)
        self.bdone = ttk.Button(self, text='Done', command=self.destroy)
        self.bdone.grid(column=2, row=4)

    def update_photo(self):
        fullpath = os.path.expandvars(os.path.expanduser(self.lframe.get_path()))
        if os.path.isfile(fullpath):
            if filetype.is_image(fullpath):
                if self.lframe.get_photo_name() != self.photo.get_name():
                        if self.db.album_exists(self.lframe.get_album_name()):
                            messagebox.showerror(parent=self,
                                              title='Updating an Album',
                                              message='Album already exists',
                                              detail='Please use another name',
                            )
                            return

                photo_copy = copy.deepcopy(self.photo)
                photo_copy.set_name(self.lframe.get_photo_name())
                photo_copy.set_path(self.lframe.get_path())
                photo_copy.set_dated(self.lframe.get_dated())
                photo_copy.set_notes(self.lframe.get_notes())
                photo_copy.set_name_list(self.rframe.get_listbox_names())
                photo_copy.set_place_list(self.rframe.get_listbox_places())
                photo_copy.set_tag_list(self.rframe.get_listbox_tags())

                self.photo = self.db.update_photo(self.photo, photo_copy)

                msg = f'Updated Photo \'{self.lframe.get_photo_name()}\''
                messagebox.showinfo(parent=self, message=msg)
            else:
                messagebox.showerror(parent=self,
                                    title='Update a Photo',
                                    message='File is not a known image type',
                                    detail='Please choose another path.')
        else:
            messagebox.showerror(parent=self,
                                 title='Update a Photo',
                                 message='Image is not a regular file',
                                 detail='Please choose another path.')

        return

    def add_name(self):
        global module_logger

        name_list = self.db.get_all_names()
        selectone = plorn_attr.PlornSelectAttr('Name', table_name='names',
                                               attr_list=name_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        name = self.db.get_name(entry['id'])
        self.photo.add_name_to_list(name)
        self.rframe.set_name_listbox_values(self.photo.get_name_list())
        module_logger.debug('add name, selected: ' + str(name))

    def remove_name(self):
        global module_logger

        name = self.rframe.get_name_listbox_value()
        module_logger.debug(f'remove_name: {str(name)}')
        if name == None:
            messagebox.showinfo(parent=self,
                                title='Remove Name from Photo',
                                message='No name selected',
                                detail='Please select a name to remove',
                               )
        else:
            self.photo.remove_name_from_list(name)
            self.rframe.set_name_listbox_values(self.photo.get_name_list())

    def add_place(self):
        global module_logger

        place_list = self.db.get_all_places()
        selectone = plorn_attr.PlornSelectAttr('Place', table_name='places',
                                               attr_list=place_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        place = self.db.get_place(entry['id'])
        self.photo.add_place_to_list(place)
        self.rframe.set_place_listbox_values(self.photo.get_place_list())
        module_logger.debug('add place, selected: ' + str(place))

    def remove_place(self):
        global module_logger

        place = self.rframe.get_place_listbox_value()
        module_logger.debug(f'remove_place: {str(place)}')
        if place == None:
            messagebox.showinfo(parent=self,
                                title='Remove Place from Photo',
                                message='No place selected',
                                detail='Please select a place to remove',
                               )
        else:
            self.photo.remove_place_from_list(place)
            self.rframe.set_place_listbox_values(self.photo.get_place_list())

    def add_tag(self):
        global module_logger

        tag_list = self.db.get_all_tags()
        selectone = plorn_attr.PlornSelectAttr('Tag', table_name='tags',
                                               attr_list=tag_list)
        selectone.grab_set()
        self.wait_window(selectone)
        entry = selectone.get_attr()
        tag = self.db.get_tag(entry['id'])
        self.photo.add_tag_to_list(tag)
        self.rframe.set_tag_listbox_values(self.photo.get_tag_list())
        module_logger.debug('add tag, selected: ' + str(tag))

    def remove_tag(self):
        global module_logger

        tag = self.rframe.get_tag_listbox_value()
        module_logger.debug(f'remove_tag: {str(tag)}')
        if tag == None:
            messagebox.showinfo(parent=self,
                                title='Remove Tag from Photo',
                                message='No tag selected',
                                detail='Please select a tag to remove',
                               )
        else:
            self.photo.remove_tag_from_list(tag)
            self.rframe.set_tag_listbox_values(self.photo.get_tag_list())


class PlornAddPhoto(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornAddPhoto')
        tfont = font.nametofont('TkDefaultFont')
        self.album_id = album_id
        self.db = plorn_db.open()
        self.album = self.db.get_album(album_id)
        self.path = None
        self.new_photo = None

        self.geometry('800x600')
        self.title('Add Photo')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=5)
        self.rowconfigure(0, weight=1)
        self.frame = ttk.Frame(self, padding='10 10 10 10')
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        for ii in range(0,8):
            self.frame.rowconfigure(ii, weight=1)

        lab1 = ttk.Label(self.frame, width=10, text='Name:')
        lab1.grid(column=0, row=0, sticky=(W))
        self.photo_name = StringVar(self.frame)
        self.photo_entry = ttk.Entry(self.frame, width=40,
                                     textvariable=self.photo_name,
                                     font=tfont)
        self.photo_entry.grid(column=1, row=0, sticky=(W))
        self.photo_entry.focus_set()

        lab2 = ttk.Label(self.frame, width=10, text='Path:')
        lab2.grid(column=0, row=1, sticky=(W))
        self.photo_path = StringVar(self.frame)
        self.path_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.photo_path,
                                    font=tfont)
        self.path_entry.grid(column=1, row=1, sticky=(W))
        self.bdir = ttk.Button(self.frame, text='Browse',
                               command=self.get_image_name)
        self.bdir.grid(column=2, row=1)

        lab3 = ttk.Label(self.frame, width=10, text='Dated:')
        lab3.grid(column=0, row=2, sticky=(W))
        self.dated = StringVar(self.frame)
        self.date_entry = ttk.Entry(self.frame, width=40,
                                    textvariable=self.dated,
                                    font=tfont)
        self.date_entry.grid(column=1, row=2, sticky=(W))

        lab4 = ttk.Label(self.frame, width=10, text='Notes:')
        lab4.grid(column=0, row=3, sticky=(N, W))
        self.notes = Text(self.frame, height=10, width=40, font=tfont)
        self.notes.grid(column=1, row=3, sticky=(N, W, E, S))

        sep1 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep1.grid(column=0, row=4, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self.frame, orient=HORIZONTAL)
        sep2.grid(column=0, row=5, columnspan=3, sticky=(W+E))

        self.bupdate = ttk.Button(self.frame, text='Add',
                                  command=self.add_photo)
        self.bupdate.grid(column=0, row=6)
        self.bcancel = ttk.Button(self.frame, text='Cancel',
                                  command=self.destroy)
        self.bcancel.grid(column=1, row=6)
        self.bdone = ttk.Button(self.frame, text='Done',
                                command=self.destroy)
        self.bdone.grid(column=2, row=6)

    def get_image_name(self):
        self.path = filedialog.askopenfilename(parent=self,
                                       title='Select an Image',
                                       initialdir=self.album.get_path(),
                                      )
        if self.path:
            self.path_entry.insert(0, self.path)

    def get_new_photo(self):
        return self.new_photo

    def add_photo(self):
        albumpath = os.path.expandvars(os.path.expanduser(self.album.get_path()))
        basename = os.path.basename(self.photo_path.get())
        if not os.path.exists(os.path.join(albumpath, basename)):
            messagebox.showerror(parent=self,
                                 title='Add a Photo',
                                 message=f'No path to image in {albumpath}',
                                 detail='Please choose another image.')
            return

        fullpath = os.path.expandvars(os.path.expanduser(self.photo_path.get()))
        if os.path.isfile(fullpath):
            if filetype.is_image(fullpath):
                photo = PlornPhoto(self.photo_name.get(),
                                   self.photo_path.get(),
                                   id=None,
                                   album_id=self.album_id,
                                   dated=self.dated.get(),
                                   notes=self.notes.get('1.0', END))
                self.new_photo = self.db.add_photo(photo)
                msg = f'Added Photo \'{self.photo_name.get()}\''
                messagebox.showinfo(parent=self, message=msg)
            else:
                messagebox.showerror(parent=self,
                                    title='Add a Photo',
                                    message='File is not a known image type',
                                    detail='Please choose another path.')
        else:
            messagebox.showerror(parent=self,
                                 title='Add a Photo',
                                 message='Image is not a regular file',
                                 detail='Please choose another path.')

