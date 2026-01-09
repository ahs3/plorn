import copy
import filetype
import logging
import os
from PIL import Image as pilImage
from PIL import ImageTk
from PIL.ExifTags import TAGS as pilTAGS
from PIL.ExifTags import GPSTAGS as pilGPSTAGS

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
                 default_state='normal', edit_path=False):
        self.db = db
        self.parent = parent
        self.album = album
        self.photo = photo
        self.default_state = default_state
        self.tfont=font.nametofont('TkDefaultFont')
        self.lframe = ttk.Frame(self.parent, padding='10 10 10 10')
        self.lframe.columnconfigure(0, weight=1)
        self.lframe.columnconfigure(1, weight=2)
        if edit_path:
            self.lframe.columnconfigure(2, weight=1)
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
        if edit_path:
            edit_state = 'normal'
        else:
            edit_state = 'readonly'
        self.path_entry = ttk.Entry(self.lframe, width=40,
                                    textvariable=self.photo_path,
                                    font=self.tfont,
                                    state=edit_state)
        self.path_entry.grid(column=1, row=2, sticky=(W))

        if edit_path:
            self.bdir = ttk.Button(self.lframe, text='Browse',
                                   command=self.get_image_name)
            self.bdir.grid(column=2, row=2)

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

    def get_album(self):
        return self.album

    def get_album_name(self):
        return self.album_name.get()

    def get_photo_name(self):
        return self.photo_name.get()

    def set_photo_name(self, name):
        self.photo_name.set(name)

    def get_photo_path(self):
        return self.photo_path.get()

    def set_photo_path(self, path):
        self.photo_path.set(path)

    def get_dated(self):
        return self.dated.get()

    def set_dated(self, dated):
        self.dated.set(dated)

    def get_notes(self):
        return self.notes.get('1.0', END)

    def set_notes(self, notes):
        self.notes.delete('1.0', END)

    def get_metadata(self, path):
        '''
        Get EXIF metadata from the image if we can
        '''

        def format_dms(degrees, minutes, seconds, direction):
            degree_symbol = u'\N{DEGREE SIGN}'
            value  = float(degrees)
            value += float(float(minutes) / 60.0)
            value += float(float(seconds) / 3600.0)
            return f'{value:.6}{degree_symbol} {direction}'

        exif_data = {}
        try:
            with pilImage.open(path) as img:
                info = img._getexif()
                for tag, value in info.items():
                    decoded_tag = pilTAGS.get(tag, tag)
                    if decoded_tag == 'DateTime':
                        exif_data[decoded_tag] = value
                    elif decoded_tag == 'OffsetTime':
                        exif_data[decoded_tag] = value
                    elif decoded_tag == 'GPSInfo':
                        gps_data = {}
                        for gps_tag in value:
                            sub_decoded_tag = pilGPSTAGS.get(gps_tag, gps_tag)
                            gps_data[sub_decoded_tag] = value[gps_tag]
                        exif_data[decoded_tag] = gps_data
                    else:
                        continue
            img.close()
        except (IOError, AttributeError, KeyError, IndexError):
            pass

        result = ''
        dated = ''
        if 'DateTime' in exif_data:
            dt = exif_data['DateTime'].split()
            date = dt[0].replace(':', '-')
            tm = dt[1]
            dated = f'{date}  {tm}'
            msg = f'Date and Time: {date}  {tm}'
            if 'OffsetTime' in exif_data:
                msg += f'{exif_data["OffsetTime"]}'
            result += msg

        if 'GPSInfo' in exif_data:
            loc = exif_data['GPSInfo']
            if len(loc) > 0:
                lat_deg = None
                lat_min = None
                lat_sec = None
                long_deg = None
                long_min = None
                long_sec = None
                if 'GPSLatitude' in loc:
                    lat_deg, lat_min, lat_sec = loc['GPSLatitude']
                    lat_dir = loc['GPSLatitudeRef']
                if 'GPSLongitude' in loc:
                    long_deg, long_min, long_sec = loc['GPSLongitude']
                    long_dir = loc['GPSLongitudeRef']
                if (lat_deg and lat_min and lat_sec) and \
                   (long_deg and long_min and long_sec):
                    lat = format_dms(lat_deg, lat_min, lat_sec, lat_dir)
                    long = format_dms(long_deg, long_min, long_sec, long_dir)
                    result += f'\nLatitude, Longitude: {lat}, {long}'

        return dated, result

    def get_image_name(self):
        photo_path = filedialog.askopenfilename(parent=self.lframe,
                                       title='Select an Image',
                                       initialdir=os.environ['HOME'],
                                      )
        if photo_path:
            self.set_photo_name(os.path.basename(photo_path))
            self.set_photo_path(photo_path)
            dated, notes = self.get_metadata(photo_path)
            self.set_dated(dated)
            self.set_notes(notes)
            self.path_entry.insert(0, photo_path)


class PhotoCanvas:
    def __init__(self, parent, path, width=600, height=500):
        self.canvas = Canvas(parent, width=width, height=height)
        self.parent = parent
        self.width = width
        self.height = height
        self.update_canvas(path)

    def get_canvas(self):
        return self.canvas

    def update_canvas(self, path):
        fullpath = os.path.expandvars(os.path.expanduser(path))

        if os.path.isfile(fullpath):
            if filetype.is_image(fullpath):
                with pilImage.open(fullpath) as img:
                    #-- i prefer scaling the image down vertically a bit,
                    # and centering it a little further down in the canvas
                    # to look better on the screen, so guess-timate where
                    # the center is best (this is a obviously subjective ... )
                    w, h = img.size         # from the image being shown
                    mid_height = (self.height/2) * 1.1
                    center = (self.width/2, mid_height)
                    img.thumbnail((self.width, self.height * 0.8),
                                  pilImage.Resampling.LANCZOS)
                    self.canvas_img = ImageTk.PhotoImage(image=img)
                    self.photo = self.canvas.create_image(center,
                                            anchor=CENTER,
                                            image=self.canvas_img)


class PlornShowPhoto(Toplevel):
    def __init__(self, parent, photo_id):
        super().__init__(parent)
        module_logger.debug('started PlornShowPhoto')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.photo = self.db.get_photo(photo_id)
        self.album = self.db.get_album(self.photo.get_album_id())

        self.geometry('1600x650')
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

        self.canvas = PhotoCanvas(self, self.photo.get_path())
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE,
                                      padx=20, pady=20)

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

        self.geometry('1600x650')
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

        self.canvas = PhotoCanvas(self, self.photo.get_path())
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE,
                                      padx=20, pady=20)

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

        self.geometry('1600x650')
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
                                          default_state='normal',
                                          edit_path=False)
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

        self.canvas = PhotoCanvas(self, self.photo.get_path())
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE,
                                      padx=20, pady=20)

        self.bupdate = ttk.Button(self, text='Update',
                                  command=self.update_photo)
        self.bupdate.grid(column=0, row=4)
        self.bcancel = ttk.Button(self, text='Cancel', command=self.destroy)
        self.bcancel.grid(column=1, row=4)

    def update_photo(self):
        fullpath = os.path.expandvars(os.path.expanduser(self.lframe.get_photo_path()))
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
                photo_copy.set_path(self.lframe.get_photo_path())
                photo_copy.set_dated(self.lframe.get_dated())
                photo_copy.set_notes(self.lframe.get_notes())
                photo_copy.set_name_list(self.rframe.get_listbox_names())
                photo_copy.set_place_list(self.rframe.get_listbox_places())
                photo_copy.set_tag_list(self.rframe.get_listbox_tags())

                self.photo = self.db.update_photo(self.photo, photo_copy)

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

        self.destroy()

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

    def get_updated_photo(self):
        return self.photo


class PlornAddPhoto(Toplevel):
    def __init__(self, parent, album_id):
        super().__init__(parent)
        module_logger.debug('started PlornAddPhoto')
        tfont = font.nametofont('TkDefaultFont')
        self.db = plorn_db.open()
        self.photo = PlornPhoto('')         # create place holder
        self.photo_written = False
        self.album = self.db.get_album(album_id)

        self.geometry('1600x650')
        self.title('Add a Photo')
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=5)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        self.lframe = PlornPhotoLeftFrame(self.db, self, album=self.album,
                                          photo=self.photo,
                                          edit_path=True)
        self.lframe.get_frame().grid(column=0, row=0, sticky=(N,W,E,S))

        self.rframe = plorn_common.PlornAttrFrame(self.db, self,
                base_obj=None,
                get_name_list=self.db.get_names_for_photo,
                get_place_list=self.db.get_places_for_photo,
                get_tag_list=self.db.get_tags_for_photo,
                edit_lists=True,
        )
        self.rframe.get_frame().grid(column=1, row=0, sticky=(N,W,E,S))
        self.rframe.set_name_commands(self.add_name, self.remove_name)
        self.rframe.set_place_commands(self.add_place, self.remove_place)
        self.rframe.set_tag_commands(self.add_tag, self.remove_tag)

        self.canvas = PhotoCanvas(self, plorn_config.plorn_photo_path())
        self.canvas.get_canvas().grid(column=2, row=0, sticky=NE,
                                      padx=20, pady=20)

        sep1 = ttk.Separator(self, orient=HORIZONTAL)
        sep1.grid(column=0, row=1, columnspan=3, sticky=(W+E))
        sep2 = ttk.Separator(self, orient=HORIZONTAL)
        sep2.grid(column=0, row=2, columnspan=3, sticky=(W+E))

        self.bframe = ttk.Frame(self, padding='10 10 10 10')
        self.bframe.columnconfigure(0, weight=1)
        self.bframe.columnconfigure(1, weight=1)
        self.bframe.columnconfigure(2, weight=1)
        self.bframe.columnconfigure(3, weight=1)
        self.bframe.rowconfigure(0, weight=1)
        self.bframe.grid(column=0, row=3, columnspan=3)
        self.bupdate = ttk.Button(self.bframe,
                                  text='Add', command=self.add_photo)
        self.bupdate.grid(column=0, row=0, padx=40, pady=0)
        self.bcancel = ttk.Button(self.bframe,
                                  text='Clear', command=self.clear_info)
        self.bcancel.grid(column=1, row=0, padx=40, pady=0)
        self.bcancel = ttk.Button(self.bframe,
                                  text='Cancel', command=self.destroy)
        self.bcancel.grid(column=2, row=0, padx=40, pady=0)
        self.bdone = ttk.Button(self.bframe, text='Done', command=self.destroy)
        self.bdone.grid(column=3, row=0, padx=40, pady=0)

    def get_new_photo(self):
        return self.photo

    def add_photo(self):
        global module_logger

        path = self.lframe.get_photo_path()
        module_logger.debug(f'PATH == {path}, or {self.lframe.get_photo_path()}')
        fullpath = os.path.expandvars(os.path.expanduser(path))
        if os.path.isfile(fullpath):
            if filetype.is_image(fullpath):
                self.canvas.update_canvas(path)
                if self.photo_written:
                    self._update_photo()
                else:
                    self._add_photo()
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

    def _add_photo(self):
        new_photo = PlornPhoto(self.lframe.get_photo_name(),
                               id=None,
                               album_id=self.lframe.get_album().get_id(),
                               path=self.lframe.get_photo_path(),
                               dated=self.lframe.get_dated(),
                               notes=self.lframe.get_notes(),
                               names=self.rframe.get_listbox_names(),
                               places=self.rframe.get_listbox_places(),
                               tags=self.rframe.get_listbox_tags())
        self.photo = self.db.add_photo(new_photo)
        self.photo_written = True
        self.bupdate.configure(text='Update')
        msg = f'Added Photo \'{self.lframe.get_photo_name()}\''
        messagebox.showinfo(parent=self, message=msg)

    def _update_photo(self):
        photo_copy = copy.deepcopy(self.photo)
        photo_copy.set_name(self.lframe.get_photo_name())
        photo_copy.set_path(self.lframe.get_photo_path())
        photo_copy.set_dated(self.lframe.get_dated())
        photo_copy.set_notes(self.lframe.get_notes())
        photo_copy.set_name_list(self.rframe.get_listbox_names())
        photo_copy.set_place_list(self.rframe.get_listbox_places())
        photo_copy.set_tag_list(self.rframe.get_listbox_tags())

        self.photo = self.db.update_photo(self.photo, photo_copy)

    def clear_info(self):
        self.lframe.set_photo_name('')
        self.lframe.set_photo_path('')
        self.lframe.set_dated('')
        self.lframe.set_notes('')
        self.rframe.set_name_listbox_values([])
        self.rframe.set_place_listbox_values([])
        self.rframe.set_tag_listbox_values([])
        del self.photo
        self.photo = PlornPhoto('')
        self.photo_written = False
        self.canvas.update_canvas(plorn_config.plorn_photo_path())
        self.bupdate.configure(text='Add')

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


