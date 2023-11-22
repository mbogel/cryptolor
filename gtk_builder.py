#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#reference https://lazka.github.io/pgi-docs/
import json
import zlib
import gi
import random
import string

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
#from gi.repository import GLib
#from gi.repository import GObject
#from gi.repository import Gdk
from gi.repository import GdkPixbuf

def random_string(length=16, min_length=8, random_length=False):
    if random_length:
        length = random.randint(min_length,length)
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation, k=length))

def pretty_print(object):
    print(json.dumps(object, indent=2))

def parse_files(directory):
    import os
    ffiles = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            path = os.path.join(root, name)
            ffiles.append(path)
    return ffiles

def get_current_timestamp(filename=True):
    from datetime import datetime
    d = datetime.now()
    if filename:
        return d.strftime('%Y-%m-%d_%H_%M_%S')
    else:
        return d.strftime('%Y-%m-%d %H:%M:%S')

def write_file(filename, data, json_object=True, gzip=False, level=9):
    if json_object:
        data = json.dumps(data, sort_keys=False, indent=4, default=str)
    if gzip:
        if type(data) == str:
            data = data.encode("utf-8")
        data = zlib.compress(data, level=level)
    if type(data) == str:
        f = open(filename, "w")
        f.write(data)
    else:
        f = open(filename, "wb")
        f.write(data)
    f.close()

def read_json(filename, gzip=False):
    json_obj = None
    if gzip:
        f = open(filename, 'rb')
        data = f.read()
        data = zlib.decompress(data)
        json_obj = json.loads(data.decode("utf-8"))
        f.close()
    else:
        f = open(filename, 'r')
        json_obj = json.load(f)
        f.close()
    return json_obj

def get_img_pixbuf_scale(img_path, img_width, img_height):
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=img_path, 
                width=img_width, 
                height=img_height, 
                preserve_aspect_ratio=True)
        return pixbuf
    except Exception as e:
        print(e)
        print("Error Loading Image")
        return None
    
###########FIX THIS FROM SCALE AND FROM FILE FULL PIX
def get_img_pixbuf(img_file):
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(img_file)
        return pixbuf
    except Exception as e:
        print(e)
        print("Error Loading Image")
        return None
    
def get_img_pixbuf_from_bytes(input_bytes, file_type):
    loader = GdkPixbuf.PixbufLoader.new_with_type(file_type)
    loader.write(input_bytes)
    loader.close()
    return loader.get_pixbuf()

def scale_img_pixbuf(src_image_pixbuf, width, height, nearest=False):
    k_pixbuf = float(src_image_pixbuf.props.height) / src_image_pixbuf.props.width
    k_rect = float(height) / width
    if k_pixbuf < k_rect:
        newWidth = width
        newHeight = int(newWidth * k_pixbuf)
    else:
        newHeight = height
        newWidth = int(newHeight / k_pixbuf)
    if nearest:
        return src_image_pixbuf.scale_simple(newWidth, newHeight, GdkPixbuf.InterpType(0))
    else:
        return src_image_pixbuf.scale_simple(newWidth, newHeight, GdkPixbuf.InterpType(2)) 
    
def create_widget(label, type, widgets, id=None, default=None, onclick=None, onchanged=None, selectchanged=None, onactivated=None, options=None, search_filter=None, buttons=None, justify=None, parent=None, shown=True, position=None, editable=True, add_scrolled=False, move_handle=None, with_entry=False, with_frame=False, icon=None, icon_size=16, max_chars=None, wrap=False, box=False):
    container = None
    widget = None
    child = None
    item = {}
    if id == None:
        id = label
    if type == "image":
        widget = Gtk.Image()
        if default != None:
            widget.set_from_file(default)
        widget.xalign = 0.5
        widget.yalign = 0.5
    if type == "paned":
        widget = Gtk.Paned()
        widget.set_wide_handle(True)
        if default != None:
            widget.set_position(default)
        else:
            widget.set_position(200)
        if move_handle != None:
            widget.connect("size-allocate", move_handle)

    if type == "hbox":
        widget = Gtk.Box(spacing=6)
        widget.set_orientation(Gtk.Orientation.HORIZONTAL)
        widget.set_hexpand(True)
    if type == "vbox":
        widget = Gtk.Box(spacing=6)
        widget.set_orientation(Gtk.Orientation.VERTICAL)
        widget.set_hexpand(True)
    if type == "expander":
        widget = Gtk.Expander(label=label)
        widget.set_expanded(shown)
        child = Gtk.Box(spacing=6)
        child.set_orientation(Gtk.Orientation.VERTICAL)
        widget.add(child)
    if type == "entry":
        container = Gtk.Frame(label=label)
        widget = Gtk.Entry()
        widget.set_hexpand(True)
        widget.set_editable(editable)
        container.set_shadow_type(Gtk.ShadowType.NONE)
        container.add(widget)
        if id in widgets["options"]:
            widget.set_text(str(widgets["options"][id]))
        elif default != None:
            widget.set_text(default)
        if max_chars != None:
            widget.set_max_width_chars(max_chars)
            widget.set_width_chars(max_chars)
    elif type == "label":
        widget = Gtk.Label(label=label)
        container = Gtk.Box(spacing=6)
        container.set_orientation(Gtk.Orientation.HORIZONTAL)
        if justify != None:
            widget.set_justify(justify)
            if justify == Gtk.Justification.RIGHT:
                container.set_halign(Gtk.Align.END)
            else:
                container.set_halign(Gtk.Align.START)
        
        widget.set_hexpand(True)
        container.set_hexpand(True)
        container.add(widget)
    elif type == "combo" or type == "combo_entry":
        widget = None
        if with_entry:
            widget = Gtk.ComboBoxText.new_with_entry()
        else:
            widget = Gtk.ComboBoxText()
        for option in options:
            widget.append_text(option)
        #widget.set_entry_text_column(0)
        widget.set_hexpand(True)        
        if onchanged != None:
            widget.connect("changed", onchanged)
        if id in widgets["options"]:
            widget.set_active(options.index(widgets["options"][id]))
        elif default != None:
            widget.set_active(options.index(default))
        widget.set_hexpand(True)
        container = None
        if with_frame:
            container = Gtk.Frame(label=label)
            container.set_shadow_type(Gtk.ShadowType.NONE)
        else:
            lbl = Gtk.Label(label=label)
            container = Gtk.Box(spacing=6)
            container.set_orientation(Gtk.Orientation.HORIZONTAL)
            container.add(lbl)
        container.add(widget)
        
    elif type == "button":
        if icon != None:
            widget = Gtk.Button()
            img = Gtk.Image()
            i = GdkPixbuf.Pixbuf.new_from_file_at_size(icon, icon_size, icon_size) 
            img.set_from_pixbuf(i) 
            widget.set_image(img)
            set_margins(widget, 0)
            widget.set_hexpand(False)
            widget.set_halign(Gtk.Align.CENTER)
            widget.set_vexpand(False)
            widget.set_valign(Gtk.Align.END)
        else:
            widget = Gtk.Button(label=label)
            widget.set_halign(Gtk.Align.CENTER)
            widget.set_hexpand(True)
        widget.connect("clicked", onclick)

    elif type == "button_group":
        container = Gtk.Box(spacing=6)
        container.set_orientation(Gtk.Orientation.HORIZONTAL)

        members = []
        for button in buttons:
            b = Gtk.Button(label=button)
            b.connect("clicked", onclick)
            b.set_halign(Gtk.Align.CENTER)
            b.set_hexpand(True)
            b.set_margin_top(10)
            container.add(b)
            members.append({"id": button, "widget":b})
            
        item["members"] = members

    elif type == "treeview":
        liststore = Gtk.ListStore(str)
        if id in widgets["options"]:
            for previous in widgets["options"][id]["items"]:
                liststore.append([previous])

        if search_filter != None:
            filter = liststore.filter_new()
            filter.set_visible_func(search_filter, data=None)
            item["search_filter"] = filter
            widget = Gtk.TreeView(model=filter)
        else:
            widget = Gtk.TreeView(model=liststore)
        item["liststore"] = liststore
        
        widget.props.headers_visible = False
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Name", renderer_text, text=0)
        widget.append_column(column_text)

        select = widget.get_selection()
        if selectchanged != None:
            select.connect("changed", selectchanged)
        treeviewscrolledwindow = Gtk.ScrolledWindow()
        treeviewscrolledwindow.set_hexpand(True)
        treeviewscrolledwindow.set_vexpand(True)
        treeviewscrolledwindow.add(widget)

        container = Gtk.Frame(label=label)
        container.set_shadow_type(Gtk.ShadowType.NONE)
        container.add(treeviewscrolledwindow)
        
    elif type == "search":
        widget = Gtk.Entry()
        if id in widgets["options"]:
            widget.set_text(widgets["options"][id])
        searchframe = Gtk.Frame(label=label)
        searchframe.set_shadow_type(Gtk.ShadowType.NONE)
        searchframe.add(widget)
        if box == False:
            container = searchframe
        else:
            container = Gtk.Box(spacing=6)
            container.set_orientation(Gtk.Orientation.HORIZONTAL)
            container.set_halign(Gtk.Align.END)
            container.set_hexpand(True)
            container.set_margin_top(10)
            container.add(searchframe)
    
    if wrap:
        widget.set_hexpand(False)
        widget.set_halign(Gtk.Align.CENTER)
        widget.set_vexpand(False)
        widget.set_valign(Gtk.Align.END)

    if onchanged != None:
        widget.connect("changed", onchanged)

    if onactivated != None:
        widget.connect("activate", onactivated)

    if add_scrolled:
        container = Gtk.ScrolledWindow()
        container.set_hexpand(True)
        container.set_vexpand(True)
        container.add(widget)

    item["id"] = id
    item["type"] = type
    item["widget"] = widget
    item["container"] = container
    item["options"] = options
    item["parent"] = parent
    item["child"] = child
    if position != None:
        item["position"] = position
    widgets["widgets"].append(item)
    if child != None:
        return child
    elif container != None and not add_scrolled:
        return container
    else:
        return widget

def pack_widgets(container, widgets):
    for widget in widgets["widgets"]:
        if widget["parent"] != None:
            parent = widget["parent"]
            if widget["container"] != None:
                if type(parent) is Gtk.Paned:
                    if widget["position"] == 1:
                        parent.add1(widget["container"])
                    if widget["position"] == 2:
                        parent.add2(widget["container"])
                else:
                    parent.add(widget["container"])
            else:
                if type(parent) is Gtk.Paned:
                    if widget["position"] == 1:
                        parent.add1(widget["widget"])
                    if widget["position"] == 2:
                        parent.add2(widget["widget"])
                else:        
                    parent.add(widget["widget"])
        elif widget["container"] != None:
            container.add(widget["container"])
        else:
            container.add(widget["widget"])

def set_margins(widget, amount):
    widget.set_margin_top(amount)
    widget.set_margin_bottom(amount)
    widget.set_margin_start(amount)
    widget.set_margin_end(amount)
    
def get_widget_by_id(widgets, id, member_id=None, return_dict=False):
    for widget in widgets["widgets"]:
        if widget["id"] == id:
            if member_id != None:
                members = widget["members"]
                for member in members:
                    if member["id"] == member_id:
                        return member["widget"]
            else:        
                if return_dict:
                    return widget
                else:
                    return widget["widget"]
    return None

def parse_widget_values(widgets, skip_tree=False):
    values = {}
    for widget in widgets["widgets"]:
        if widget["type"] == "entry" or widget["type"] == "search":
            values[widget["id"]] = widget["widget"].get_text()
        elif widget["type"] == "combo":
            values[widget["id"]] = widget["options"][widget["widget"].get_active()]
        elif widget["type"] == "combo_entry":
            values[widget["id"]] = widget["widget"].get_active_text()
        elif widget["type"] == "treeview" and not skip_tree:
            treeview_item = {}
            selected = None
            model, treeiter = widget["widget"].get_selection().get_selected()
            if treeiter is not None:
                selected = model[treeiter][0]
            treeview_item["selected"] = selected
            items = []
            treeview = widget["widget"]
            model = treeview.get_model()
            for item in model:
                items.append(item[0])
            treeview_item["items"] = items
            values[widget["id"]] = treeview_item
    return values

def set_treeview_selection(treeview, item):
    model = treeview.get_model()
    items = []
    for i in model:
        items.append(i[0])
    try:
        model = treeview.get_model()
        index = items.index(item)
        treeview.set_cursor(index)
    except Exception as e:
        print(e)