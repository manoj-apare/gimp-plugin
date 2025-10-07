#!/usr/bin/env python3
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
import sys

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

'''
A Python plugin.
My Frame.
'''

def add_frame(procedure, run_mode, image, drawables, config, data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init('python-fu-my-frame')
        Gegl.init(None)
        dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
        dialog.fill(None)
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
        else:
            dialog.destroy()

    image.undo_group_start()

    # Calculate border thickness as 0.0125 of image size
    imageWidth = image.get_width()
    imageHeight = image.get_height()
    border_thickness = int(max(imageWidth, imageHeight) * 0.0125)
    
    # Resize image to accommodate border
    newWidth = imageWidth + (2 * border_thickness)
    newHeight = imageHeight + (2 * border_thickness)
    image.resize(newWidth, newHeight, border_thickness, border_thickness)
    
    # Add white border layer
    border_layer = Gimp.Layer.new(image, "White Border",
                                 newWidth, newHeight,
                                 Gimp.ImageType.RGB_IMAGE,
                                 100, Gimp.LayerMode.NORMAL)

    total_layers = len(image.get_layers())
    image.insert_layer(border_layer, None, total_layers)
    border_layer.fill(Gimp.FillType.WHITE)

    image.undo_group_end()
    Gimp.displays_flush()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class MyFramePlugin (Gimp.PlugIn):
    # FUTURE all other Gimp classes that have GimpParamSpecs

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return False

    def do_query_procedures(self):
        return [ 'python-fu-my-frame' ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, add_frame, None)
        procedure.set_image_types("*")
        procedure.set_documentation ("My Frame ", "My Frame ", name)
        procedure.set_menu_label("My Frame")
        procedure.set_attribution("Manoj Kumar", "Manoj Kumar", "2025")
        # Top level menu "Frames"
        procedure.add_menu_path ("<Image>/Filters/Frames/")

        return procedure

Gimp.main(MyFramePlugin.__gtype__, sys.argv)
