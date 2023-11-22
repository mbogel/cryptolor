#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
#from gi.repository import GLib
#from gi.repository import GObject
#from gi.repository import Gdk
#from gi.repository import GdkPixbuf
from io import BytesIO
from PIL import Image
import os
import json
import math
#import random
#import shutil

from crypto import Crypto
from cryptolor import *
try:
    from .gtk_builder import *
except:
    from gtk_builder import *
    
class DecodeDialog(Gtk.Dialog):
    def __init__(self, parent, file_name=None, data=None, options={}, title="Decode"):
        super().__init__(title=title, transient_for=parent, flags=0)
        self.options = options
        cancel_button = self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        self.ok_button = self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.set_default_size(960, 600)
        self.input_image_filename = file_name
        self.output_filename = None
        self.crypto = Crypto()
        self.widgets = {}
        self.widgets["widgets"] = []
        if data != None:
            if data["vol"] == -1:
                data["vol"] = ""
            if data["num"] == -1:
                data["num"] = ""
            self.widgets["options"] = data
        else:
            self.widgets["options"] = {}
        
        paned = create_widget("paned", "paned", self.widgets, default=480)
        create_widget("Input Image", "image", self.widgets, add_scrolled=True, parent=paned, position=1)
        options_vbox = create_widget("options_vbox", "vbox", self.widgets, parent=paned, position=2)
        options_scrollpane = create_widget("options_scrollpane", "vbox", self.widgets, add_scrolled=True, parent=options_vbox)
        input_file_hbox = create_widget("input_file_hbox", "hbox", self.widgets, parent=options_scrollpane)
        create_widget("Input Image Filename", "entry", self.widgets, default=self.input_image_filename, parent=input_file_hbox, onchanged=self.on_option_changed)
        create_widget("Choose Input Image", "button", self.widgets, id="img_button", parent=input_file_hbox, onclick=self.on_file_clicked, icon=parent.folder_button_file)
        create_widget("Type", "combo", self.widgets, with_frame=True, options=["Seed", "Checkered", "Box"], default="Seed", parent=options_scrollpane)
        create_widget("Seed", "entry", self.widgets, editable=True, parent=options_scrollpane)
        nums_vbox = create_widget("nums_vbox", "vbox", self.widgets, parent=options_scrollpane)
        create_widget("Encoding Factor", "entry", self.widgets, editable=True, parent=nums_vbox)
        create_widget("Box Size", "entry", self.widgets, editable=True, parent=nums_vbox)
        create_widget("Gzip", "combo", self.widgets, with_frame=True, options=["No", "Yes"], default="No", parent=options_scrollpane)
        create_widget("Encryption", "combo", self.widgets, with_frame=True, options=["No", "Yes"], default="No", parent=options_scrollpane)
        create_widget("Salt", "entry", self.widgets, editable=True, default="", parent=options_scrollpane)
        create_widget("Password", "entry", self.widgets, editable=True, default="", parent=options_scrollpane)
        create_widget("buttons", "button_group", self.widgets, onclick=self.on_button_clicked, buttons=["Decode File", "Decode String"], parent=options_vbox)
        create_widget("", "label", self.widgets, id="Output Message", justify=Gtk.Justification.LEFT, parent=options_scrollpane)

        box = self.get_content_area()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        pack_widgets(box, self.widgets)
        set_margins(box,10)

        self.show_all()
        self.update_image()

    def get_data(self):
        return parse_widget_values(self.widgets)
    
    def decode(self):
        if self.input_image_filename != None:
            try:
                seed = get_widget_by_id(self.widgets, "Seed").get_text()
                encode_factor = int(get_widget_by_id(self.widgets, "Encoding Factor").get_text())
                values = parse_widget_values(self.widgets)
                _type = values["Type"]
                checkered = False
                box = None
                if _type == "Checkered":
                    checkered = True
                if _type == "Box":
                    box = int(get_widget_by_id(self.widgets, "Box Size").get_text())
                use_gzip = False
                _gzip = values["Gzip"]
                if _gzip == "Yes":
                    use_gzip = True
                cryptolor = Cryptolor(self.input_image_filename, seed=seed, encode_factor=encode_factor, checkered=checkered, box=box, gzip=use_gzip)
                test = cryptolor.decode()
                if test != None:
                    get_widget_by_id(self.widgets, "Output Message").set_text(test)
                else:
                    if values["Encryption"] == "Yes":
                        password = values["Password"].encode("utf-8")
                        salt = values["Salt"]
                        key = self.crypto.gen_key(password, salt)
                        try:
                            get_widget_by_id(self.widgets, "Output Message").set_text(self.crypto.decrypt(key.decode("utf-8"),cryptolor.get_decoded_bytes()).decode("utf-8"))
                        except:
                            get_widget_by_id(self.widgets, "Output Message").set_text("BAD DECRYPTION!")
                    else:
                        get_widget_by_id(self.widgets, "Output Message").set_text(cryptolor.get_decoded_string())
            except Exception as e:
                print(e)
                get_widget_by_id(self.widgets, "Output Message").set_text("Missing settings!")
                
    
    def decode_file(self):
        if self.input_image_filename != None:
            try:
                seed = get_widget_by_id(self.widgets, "Seed").get_text()
                encode_factor = int(get_widget_by_id(self.widgets, "Encoding Factor").get_text())
                values = parse_widget_values(self.widgets)
                _type = values["Type"]
                checkered = False
                box = None
                if _type == "Checkered":
                    checkered = True
                if _type == "Box":
                    box = int(get_widget_by_id(self.widgets, "Box Size").get_text())
                use_gzip = False
                _gzip = values["Gzip"]
                if _gzip == "Yes":
                    use_gzip = True
                cryptolor = Cryptolor(self.input_image_filename, seed=seed, encode_factor=encode_factor, checkered=checkered, box=box, gzip=use_gzip)
                test = cryptolor.decode()
                if test != None:
                    get_widget_by_id(self.widgets, "Output Message").set_text(test)
                else:
                    dialog = Gtk.FileChooserDialog(
                    title="Save File", parent=self, action=Gtk.FileChooserAction.SAVE
                    )
                    dialog.add_buttons(
                        Gtk.STOCK_CANCEL,
                        Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_OPEN,
                        Gtk.ResponseType.OK,
                    )
                    if self.output_filename != None:
                        dialog.set_current_name(self.output_filename)
                    else:
                        dialog.set_current_name("cryptolor.out")
                    dialog.set_do_overwrite_confirmation(True)
                    #self.add_filters(dialog)

                    response = dialog.run()
                    if response == Gtk.ResponseType.OK:
                        print("Open clicked")
                        print("File selected: " + dialog.get_filename())
                        get_widget_by_id(self.widgets, "Output Message").set_text("File Written: " + dialog.get_filename())
                        if values["Encryption"] == "Yes":
                            password = values["Password"].encode("utf-8")
                            salt = values["Salt"]
                            key = self.crypto.gen_key(password, salt)
                            try:
                                decoded_bytes = self.crypto.decrypt(key.decode("utf-8"),cryptolor.get_decoded_bytes())                    
                                o = open(dialog.get_filename(),'wb')
                                o.write(decoded_bytes)
                                o.close()
                            except:
                                get_widget_by_id(self.widgets, "Output Message").set_text("BAD DECRYPTION!")
                        else:
                            cryptolor.write_file(dialog.get_filename())
                    elif response == Gtk.ResponseType.CANCEL:
                        print("Cancel clicked")

                    dialog.destroy()
            except:
                get_widget_by_id(self.widgets, "Output Message").set_text("Missing settings!")
                
                
    
    def update_image(self):
        if self.input_image_filename != None:
            try:
                im = Image.open(self.input_image_filename)
                im.load()
                m = im.info["metadata"]
                metadata = json.loads(m)
                print(metadata)
                get_widget_by_id(self.widgets, "Box Size").set_text(metadata["b"])
                get_widget_by_id(self.widgets, "Seed").set_text(metadata["s"])
                get_widget_by_id(self.widgets, "Encoding Factor").set_text(metadata["e"])
                if metadata["c"] == "2":
                    get_widget_by_id(self.widgets, "Type").set_active(2)
                elif metadata["c"] == "1":
                    get_widget_by_id(self.widgets, "Type").set_active(1)
                else:
                    get_widget_by_id(self.widgets, "Type").set_active(0)
                if metadata["z"] == "1":
                    get_widget_by_id(self.widgets, "Gzip").set_active(1)
                else:
                    get_widget_by_id(self.widgets, "Gzip").set_active(0)
                if metadata["i"] == "File":
                    self.output_filename = metadata["f"]
                if "t" in metadata:
                    get_widget_by_id(self.widgets, "Salt").set_text(metadata["t"])
                    get_widget_by_id(self.widgets, "Encryption").set_active(1)
            except:
                pass
            image = get_widget_by_id(self.widgets, "Input Image", return_dict=True)["container"]
            width = image.get_allocation().width
            height = image.get_allocation().height
            pixbuf = get_img_pixbuf_scale(self.input_image_filename, width, height)
            get_widget_by_id(self.widgets, "Input Image").set_from_pixbuf(pixbuf)

    def on_option_changed(self, widget):
        self.update_image()
        
    def on_button_clicked(self, widget):
        if widget == get_widget_by_id(self.widgets, "buttons", member_id="Decode String"):
            self.decode()

        if widget == get_widget_by_id(self.widgets, "buttons", member_id="Decode File"):
            self.decode_file()

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        #self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            get_widget_by_id(self.widgets, "Input Image Filename").set_text(dialog.get_filename())
            self.input_image_filename = dialog.get_filename()
            self.update_image()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

class CryptolorGTK(Gtk.Window):
    def __init__(self):
        super().__init__(title="Cryptolor")

        self.icon_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cryptolor.png")
        self.set_icon_from_file(self.icon_filename)
        
        self.config_filename = ".config.json"
        self.options_filename = ".options.json"

        self.widgets = {}
        self.widgets["widgets"] = []
        try:
            self.widgets["options"] = read_json(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.options_filename))
        except:
            self.widgets["options"] = {}
        print(self.widgets["options"])
        try:
            self.config = read_json(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.config_filename))
        except:
            self.config = {}
            self.config["position"] = (0,25)
            self.config["size"] = (640, 480)
            self.config["paned_position"] = 300
            self.config["paned2_position"] = 300
            self.config["paned3_position"] = 300
            self.config["img_width"] = 512
            self.config["img_height"] = 600
        
        self.current_file = None
        self.current_file_name = None
        self.last_saved_file = None
        self.default_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default.png")
        self.refresh_button_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "refresh.png")
        self.folder_button_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "folder.png")
        self.pixbuf = None
        self.bytes = None
        self.cryptolor = None
        self.crypto = Crypto()
        self.salt = self.crypto.gen_salt()
        self.operations = ["","Points", "Generate"]
        d = read_json(os.path.join(os.path.dirname(os.path.realpath(__file__)), "dict.json"))
        self.dictionary = []
        for item in d:
            self.dictionary.append(item)
        self.dictionary.reverse()
        #self.dictionary = self.dictionary[0:100]
        self.input_file_bytes = b'testing'


        paned = create_widget("paned", "paned", self.widgets, default=self.config["paned_position"])
        input_vbox = create_widget("input_vbox", "vbox", self.widgets, parent=paned, position=1)
        create_widget("Search", "search", self.widgets, onchanged=self.on_search_changed, parent=input_vbox, box=False)
        input_img_hbox = create_widget("input_file_hbox", "hbox", self.widgets, parent=input_vbox)
        create_widget("Input Image Folder", "entry", self.widgets, parent=input_img_hbox)
        create_widget("Choose Input Image Folder", "button", self.widgets, id="img_button", parent=input_img_hbox, onclick=self.on_imginput_clicked, icon=self.folder_button_file)
        
        create_widget("Input", "treeview", self.widgets, search_filter=self.search_visibility_filter, selectchanged=self.on_tree_selection_changed, parent=input_vbox)
        paned2 = create_widget("paned2", "paned", self.widgets, default=self.config["paned2_position"], parent=paned, position=2, move_handle=self.paned_moved)
        create_widget("Input Image", "image", self.widgets, add_scrolled=True, parent=paned2, position=1)
        paned3 = create_widget("paned3", "paned", self.widgets, default=self.config["paned3_position"], parent=paned2, position=2, move_handle=self.paned_moved)
        create_widget("Output Image", "image", self.widgets, add_scrolled=True, parent=paned3, position=1)
        options_vbox = create_widget("options_vbox", "vbox", self.widgets, parent=paned3, position=2)
        options_scrollpane = create_widget("options_scrollpane", "vbox", self.widgets, add_scrolled=True, parent=options_vbox)
        create_widget("Operation", "combo", self.widgets, with_frame=True, options=self.operations, default="Points", parent=options_scrollpane, onchanged=self.on_option_changed)
        create_widget("Type", "combo", self.widgets, with_frame=True, options=["Seed", "Checkered", "Box"], default="Seed", parent=options_scrollpane, onchanged=self.on_option_changed)
        seed_hbox = create_widget("seed_hbox", "hbox", self.widgets, parent=options_scrollpane)
        create_widget("Seed", "entry", self.widgets, editable=True, default="testing", parent=seed_hbox, onchanged=self.on_option_changed)
        create_widget("Dict Seed", "treeview", self.widgets, options=self.dictionary, parent=options_scrollpane, selectchanged=self.on_dict_tree_select_changed)
        create_widget("Random", "button", self.widgets, onclick=self.on_button_clicked, parent=seed_hbox, icon=self.refresh_button_file)
        create_widget("Box Size", "entry", self.widgets, editable=True, default="9", parent=seed_hbox, onchanged=self.on_option_changed, max_chars=4)
        auto_hbox = create_widget("auto_hbox", "hbox", self.widgets, parent=options_scrollpane)
        create_widget("Auto Seed", "button", self.widgets, onclick=self.on_button_clicked, parent=auto_hbox, wrap=True)
        create_widget("Bytes", "entry", self.widgets, editable=True, default="10000", parent=auto_hbox, max_chars=6)
        create_widget("Tries", "entry", self.widgets, editable=True, default="100", parent=auto_hbox, max_chars=6)
        dim_hbox = create_widget("dim_hbox", "hbox", self.widgets, parent=options_scrollpane)
        create_widget("Encoding Factor", "entry", self.widgets, editable=True, default="4", parent=dim_hbox, onchanged=self.on_option_changed, max_chars=4)
        create_widget("Auto Encode", "button", self.widgets, onclick=self.on_button_clicked, parent=dim_hbox, icon=self.refresh_button_file)
        create_widget("Width", "entry", self.widgets, editable=True, default="256", parent=dim_hbox, onchanged=self.on_option_changed, max_chars=4)
        create_widget("Height", "entry", self.widgets, editable=True, default="512", parent=dim_hbox, onchanged=self.on_option_changed, max_chars=4)
        create_widget("Auto Scale", "button", self.widgets, onclick=self.on_button_clicked, parent=dim_hbox, icon=self.refresh_button_file)
        create_widget("Perfect Fit", "button", self.widgets, onclick=self.on_button_clicked, parent=options_scrollpane)
        create_widget("Input Source", "combo", self.widgets, with_frame=True, options=["Message", "File"], default="Message", parent=options_scrollpane, onchanged=self.on_source_changed)
        create_widget("Message", "entry", self.widgets, editable=True, default="testing", parent=options_scrollpane, onchanged=self.on_option_changed)
        input_file_hbox = create_widget("input_file_hbox", "hbox", self.widgets, parent=options_scrollpane)
        create_widget("Input Filename", "entry", self.widgets, parent=input_file_hbox)
        create_widget("Choose File", "button", self.widgets, id="img_button", parent=input_file_hbox, onclick=self.on_file_clicked, icon=self.folder_button_file)
        create_widget("Save PNG Tags", "combo", self.widgets, with_frame=True, options=["No", "Yes"], default="Yes", parent=options_scrollpane)
        create_widget("Gzip", "combo", self.widgets, with_frame=True, options=["No", "Yes"], default="Yes", parent=options_scrollpane, onchanged=self.on_option_changed)
        create_widget("Encryption", "combo", self.widgets, with_frame=True, options=["No", "Yes"], default="No", parent=options_scrollpane, onchanged=self.on_option_changed)
        create_widget("Salt", "entry", self.widgets, editable=False, default=self.salt.decode("utf-8"), parent=options_scrollpane, onchanged=self.on_option_changed)
        create_widget("Password", "entry", self.widgets, editable=True, default="testing", parent=options_scrollpane, onchanged=self.on_option_changed)
        create_widget("", "label", self.widgets, id="Output Message", justify=Gtk.Justification.LEFT, parent=options_scrollpane, add_scrolled=True)
        create_widget("buttons", "button_group", self.widgets, onclick=self.on_button_clicked, buttons=["Decode", "Save"], parent=options_vbox)
        create_widget("Idle", "label", self.widgets, id="Status", justify=Gtk.Justification.LEFT)

        self.update_input_image_treeview()

        liststore = get_widget_by_id(self.widgets, "Dict Seed", return_dict=True)["liststore"]
        for d in self.dictionary:
            liststore.append((d,))

        get_widget_by_id(self.widgets, "Salt").set_text(self.salt.decode("utf-8"))

        self.update_current_file(self.default_file)
        self.update_input_file_bytes()

        box = Gtk.Box(spacing=6)
        box.set_orientation(Gtk.Orientation.VERTICAL)
        pack_widgets(box, self.widgets)
        set_margins(box,10)

        self.add(box)

        self.set_default_size(self.config["size"][0], self.config["size"][1])
        self.move(self.config["position"][0],self.config["position"][1])

    def update_input_image_treeview(self):
        
        get_widget_by_id(self.widgets, "Operation").set_active(0)
        liststore = get_widget_by_id(self.widgets, "Input", return_dict=True)["liststore"]
        liststore.clear()
        values = parse_widget_values(self.widgets, skip_tree=True)
        files = parse_files(values["Input Image Folder"])
        files.sort()
        accepted_files = ["png", "jpg", "jpeg", "bmp"]
        for fname in files:
            suffix = fname.rpartition(".")[2]
            if suffix.lower() in accepted_files:
                liststore.append((os.path.basename(fname),))
        #get_widget_by_id(self.widgets, "Operation").set_active(1)

    def on_imginput_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a directory", parent=self, action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        #self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            get_widget_by_id(self.widgets, "Input Image Folder").set_text(dialog.get_filename())
            self.update_input_image_treeview()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        #self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            get_widget_by_id(self.widgets, "Input Filename").set_text(dialog.get_filename())
            self.update_input_file_bytes()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def on_destroy(self, widget=None, *data):
        write_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.config_filename), self.config)
        values = parse_widget_values(self.widgets, skip_tree=True)
        write_file(os.path.join(os.path.dirname(os.path.realpath(__file__)), self.options_filename), values)

    def on_resize(self, window):
        current_size = (window.get_size()[0], window.get_size()[1])
        current_position = (window.get_position()[0], window.get_position()[1])
        if self.config["size"] != current_size:
            self.config["size"] = current_size
        if self.config["position"] != current_position:
            self.config["position"] = current_position

    def on_show(self, *args):
        pass

    def update_input_file_bytes(self):
        values = parse_widget_values(self.widgets, skip_tree=True)
        if "Input Filename" in values and values["Input Filename"] != "":
            try:
                f = open(values["Input Filename"], 'rb')
                self.input_file_bytes = f.read()
                f.close()
                if self.cryptolor != None:
                    self.update_cryptolor()
                self.update_image()
            except:
                pass

    def on_source_changed(self, widget):
        self.update_input_file_bytes()
        if self.cryptolor != None:
            self.update_cryptolor()
        self.update_image()

    def on_option_changed(self, widget):
        if self.cryptolor != None:
            self.update_cryptolor()
        self.update_image()

    def on_search_changed(self, widget):
        filter = get_widget_by_id(self.widgets, "Input", return_dict=True)["search_filter"]
        filter.refilter()
        self.update_count()

    def search_visibility_filter(self, model, iter, data):
        search_string = get_widget_by_id(self.widgets, "Search").get_text()
        if search_string == "":
            return True
        elif all(s in model[iter][0].lower() for s in search_string.lower().split(" ")):
            return True
        else:
            return False
        
    def on_dict_tree_select_changed(self, selection):
        model, treeiter = selection.get_selected()
        try:
            if treeiter is not None:
                key = model[treeiter][0]
                get_widget_by_id(self.widgets, "Seed").set_text(key)
                self.update()
        except:
            pass

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        try:
            if treeiter is not None:
                key = model[treeiter][0]
                self.current_file_name = key
                dir = get_widget_by_id(self.widgets, "Input Image Folder").get_text()
                path = os.path.join(dir, key)
                self.update_current_file(path)
                self.update()
                self.update_message()
        except:
            pass

    def paned_moved(self, scrolltype, data):
        image = get_widget_by_id(self.widgets, "Input Image", return_dict=True)["container"]
        self.config["img_width"] = image.get_allocation().width
        self.config["img_height"] = image.get_allocation().height
        paned = get_widget_by_id(self.widgets, "paned")
        self.config["paned_position"] = paned.get_position()
        paned2 = get_widget_by_id(self.widgets, "paned2")
        self.config["paned2_position"] = paned2.get_position()
        paned3 = get_widget_by_id(self.widgets, "paned3")
        self.config["paned3_position"] = paned3.get_position()
        self.update()

    def parse_message(self):
        message = self.cryptolor.get_message()
        out = {}
        parts = message.split("\n")
        for part in parts:
            key = part.rpartition(":")[0].strip()
            
            try:
                value = int(part.rpartition(":")[2].strip())
            except:
                value = part.rpartition(":")[2].strip()
            out[key] = value
        return out

    def perfect_fit(self):
        e_factor = 1
        tries = 20
        try:
            tries = int(get_widget_by_id(self.widgets, "Tries").get_text())
        except:
            pass
        get_widget_by_id(self.widgets, "Operation").set_active(0)
        get_widget_by_id(self.widgets, "Encoding Factor").set_text(str(e_factor))
        get_widget_by_id(self.widgets, "Width").set_text("128")
        get_widget_by_id(self.widgets, "Height").set_text("128")
        get_widget_by_id(self.widgets, "Operation").set_active(2)
        self.auto_scale()
        done = False
        i = 0
        while not done and i < tries:
            message = self.parse_message()
            print(message)
            print("e_factor", e_factor)
            if "" in message:
                error = message[""]
                print(error)
                if "NOT ENOUGH SPACE" in error:
                    print("auto scaling")
                    self.auto_scale()
                    self.auto_scale()
                elif "PIXEL" in error:
                    e_factor = e_factor + 1
                    print("increasing encoding factor")
                    get_widget_by_id(self.widgets, "Encoding Factor").set_text(str(e_factor))
                    self.auto_scale()
                else:
                    done = True
            else:
                done = True
            
            i = i + 1
            print("tries", i)

    def auto_encode(self):
        total_bytes = None
        message_bytes = None
        try:
            message = self.parse_message()
            total_bytes = message["Total Bytes"]
            message_bytes = message["Message Bytes"]
        except:
            pass
        if total_bytes != None and message_bytes != None:
            efactor = int(float(total_bytes) / float(message_bytes))
            if efactor != 0:
                get_widget_by_id(self.widgets, "Encoding Factor").set_text(str(efactor))
            else:
                get_widget_by_id(self.widgets, "Encoding Factor").set_text("1")
        else:
            get_widget_by_id(self.widgets, "Encoding Factor").set_text("1")
        self.update_cryptolor()

    def auto_scale(self):
        message = self.parse_message()
        total_bytes = message["Available Bytes"]
        message_bytes = message["Message Bytes"]
        width, height = self.cryptolor.get_size()
        factor = message_bytes / total_bytes
        new_amount = width * height * factor
        #w_ratio = (float(width) / float(height))
        h_ratio = (float(height) / float(width))
        new_width = math.ceil(math.sqrt(new_amount / h_ratio))
        if new_width % 2 != 0:
            new_width = new_width + 1
        new_height = new_width * h_ratio
        
        print("factor", factor)
        #print("w_ratio", w_ratio)
        print("h_ratio", h_ratio)
        print("new_amount", new_amount)
        print("old_amount", width * height)
        print("new_width", new_width)
        print("new_height", new_height)
        
        get_widget_by_id(self.widgets, "Width").set_text(str(math.ceil(new_width)))
        get_widget_by_id(self.widgets, "Height").set_text(str(math.ceil(new_height)))
        self.update_cryptolor()
        
    def auto_seed(self):
        tries = 100
        target_bytes = 1000
        try:
            tries = int(get_widget_by_id(self.widgets, "Tries").get_text())
            target_bytes = int(get_widget_by_id(self.widgets, "Bytes").get_text())
        except:
            pass
        i = 0
        done = False
        while i < tries and not done:
            self.set_random_seed()
            self.update_cryptolor()
            message = self.cryptolor.get_message()
            parts = message.split("\n")
            for part in parts:
                if "Total Bytes" in part:
                    if int(part.rpartition(":")[2].strip()) >= target_bytes:
                        done = True
            i = i + 1
            self.update_status("Tries: " + str(i))

    def set_random_seed(self):
        get_widget_by_id(self.widgets, "Seed").set_text(random_string(random_length=True, min_length=8, length=32))

    def on_button_clicked(self, widget):
        
        if widget == get_widget_by_id(self.widgets, "Perfect Fit"):
            self.perfect_fit()
        if widget == get_widget_by_id(self.widgets, "Random"):
            self.set_random_seed()
        if widget == get_widget_by_id(self.widgets, "Auto Seed"):
            self.auto_seed()
        if widget == get_widget_by_id(self.widgets, "Auto Encode"):
            self.auto_encode()
        if widget == get_widget_by_id(self.widgets, "Auto Scale"):
            self.auto_scale()
        if widget == get_widget_by_id(self.widgets, "buttons", member_id="Decode"):
            dialog = DecodeDialog(self, file_name=self.last_saved_file)
            response = dialog.run()
            dialog.destroy()
        if widget == get_widget_by_id(self.widgets, "buttons", member_id="Save"):
            dialog = Gtk.FileChooserDialog(
            title="Save File", parent=self, action=Gtk.FileChooserAction.SAVE
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN,
                Gtk.ResponseType.OK,
            )
            if self.current_file_name != None:
                dialog.set_current_name(self.current_file_name.rpartition(".")[0] + ".output.png")
            else:
                dialog.set_current_name("output.png")
            dialog.set_do_overwrite_confirmation(True)
            #self.add_filters(dialog)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                print("Open clicked")
                print("File selected: " + dialog.get_filename())
                self.save_file(dialog.get_filename())
                self.last_saved_file = dialog.get_filename()
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")

            dialog.destroy()
    
    def save_file(self, fname):
        values = parse_widget_values(self.widgets)
        tags = values["Save PNG Tags"]
        encryption = values["Encryption"]
        if tags == "Yes" or encryption == "Yes":
            """
            options = []
            
            options.append(values["Seed"])
            options.append(values["Encoding Factor"])
            options.append(values["Input Source"])
            options.append(os.path.basename(values["Input Filename"]))
            data = ":".join(options)
            data = base64.b64encode(data.encode("utf-8"))
            tags= {"metadata" : data}
            """
            tags = {}
            _type = values["Type"]
            if _type == "Box":
                tags["c"] = "2"
            elif _type == "Checkered":
                tags["c"] = "1"
            else:
                tags["c"] = "0"
            gzip = values["Gzip"]
            if gzip == "Yes":
                tags["z"] = "1"
            else:
                tags["z"] = "0"
            tags["b"] = values["Box Size"]
            tags["s"] = values["Seed"]
            tags["e"] = values["Encoding Factor"]
            tags["i"] = values["Input Source"]
            tags["f"] = os.path.basename(values["Input Filename"])
            if encryption == "Yes":
                tags["t"] = self.salt.decode("utf-8")
            t = {}
            t["metadata"] = json.dumps(tags, indent=2)
            self.cryptolor.write_image(fname, tags=t)
        else:
            self.cryptolor.write_image(fname)

    def update_message(self, message):
        widget = get_widget_by_id(self.widgets, "Output Message")
        widget.set_text(message)

    def update_status(self, text):
        widget = get_widget_by_id(self.widgets, "Status")
        widget.set_text(text)

    def update_count(self):
        treeview = get_widget_by_id(self.widgets, "Input")
        model = treeview.get_model()
        self.update_status("Images: " + str(len(model)))

    def update_current_file(self, fname):
        if self.current_file != fname:
            self.current_file = fname
            f = open(self.current_file, 'rb')
            self.bytes = f.read()
            f.close()
            mime = self.current_file.rpartition(".")[2].lower()
            if mime == "jpg":
                mime = "jpeg"
            self.pixbuf = get_img_pixbuf_from_bytes(self.bytes, mime)
            self.update_cryptolor()

    def update_cryptolor(self):
        seed_entry = get_widget_by_id(self.widgets, "Seed")
        values = parse_widget_values(self.widgets)
        _type = values["Type"]
        checkered = False
        box = None
        if _type == "Checkered":
            checkered = True
        if _type == "Box":
            box = int(values["Box Size"])
        use_gzip = False
        _gzip = values["Gzip"]
        if _gzip == "Yes":
            use_gzip = True
        if seed_entry != None:
            seed = seed_entry.get_text()
            if seed == "":
                seed = "a"
            encoding_factor = 4
            try:
                encoding_factor = int(get_widget_by_id(self.widgets, "Encoding Factor").get_text())
            except:
                pass
            width_string = get_widget_by_id(self.widgets, "Width").get_text()
            height_string = get_widget_by_id(self.widgets, "Height").get_text()
            if width_string != "" and height_string != "":
                try:
                    width = int(width_string)
                    height = int(height_string)
                    self.cryptolor = Cryptolor(BytesIO(self.bytes), seed=seed, scale=True, width=width, height=height, encode_factor=encoding_factor, checkered=checkered, box=box, gzip=use_gzip)
                    
                    
                except:
                    print("Error Generating")
            else:
                self.cryptolor = Cryptolor(BytesIO(self.bytes), seed=seed, encode_factor=encoding_factor, checkered=checkered, gzip=use_gzip)
                
            operation = self.operations[get_widget_by_id(self.widgets, "Operation").get_active()]
            if operation == "Points":
                self.cryptolor.points()
                self.update_message(self.cryptolor.get_message())
                bytes_io_file = self.cryptolor.get_buffer()
                self.pixbuf2 = get_img_pixbuf_from_bytes(bytes_io_file.read(), "png")
            elif operation == "Generate":
                values = parse_widget_values(self.widgets, skip_tree=True)
                encryption = values["Encryption"]
                if encryption == "Yes":
                    key = self.crypto.gen_key(values["Password"].encode("utf-8"), self.salt)
                    if values["Input Source"] == "Message":
                        message = get_widget_by_id(self.widgets, "Message").get_text()
                        self.cryptolor.encode_bytes(self.crypto.encrypt(key,message.encode("utf-8")))
                    if values["Input Source"] == "File":
                        self.cryptolor.encode_bytes(self.crypto.encrypt(key,self.input_file_bytes))
                else:
                    if values["Input Source"] == "Message":
                        message = get_widget_by_id(self.widgets, "Message").get_text()
                        self.cryptolor.encode_string(message)
                    if values["Input Source"] == "File":
                        self.cryptolor.encode_bytes(self.input_file_bytes)
                error = self.cryptolor.process()
                if error == None:
                    self.update_message(self.cryptolor.get_message())
                    bytes_io_file = self.cryptolor.get_buffer()
                    self.pixbuf2 = get_img_pixbuf_from_bytes(bytes_io_file.read(), "png")
                else:
                    self.update_message(error)
            else:
                self.pixbuf2 = self.pixbuf

    def update_image(self):
        if self.pixbuf != None:
            pixbuf = scale_img_pixbuf(self.pixbuf, self.config["img_width"], self.config["img_height"])
            get_widget_by_id(self.widgets, "Input Image").set_from_pixbuf(pixbuf)
            pixbuf2 = scale_img_pixbuf(self.pixbuf2, self.config["img_width"], self.config["img_height"], nearest=True)
            get_widget_by_id(self.widgets, "Output Image").set_from_pixbuf(pixbuf2)

    def update(self):
        self.update_image()

win = CryptolorGTK()
win.connect("destroy", Gtk.main_quit)
win.connect('delete-event', win.on_destroy)
win.connect('check-resize', win.on_resize)
win.show_all()
win.on_show()
Gtk.main()