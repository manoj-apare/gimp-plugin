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
from gi.repository import Gio
import time
import sys
import math

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

'''
A Python plugin.
My Watermark.
'''

def add_watermark(procedure, run_mode, image, drawables, config, data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init('python-fu-my-watermark')
        Gegl.init(None)
        dialog = GimpUi.ProcedureDialog(procedure=procedure, config=config)
        dialog.fill(None)
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, GLib.Error())
        else:
            dialog.destroy()

    file = config.get_property('file')
    scale = config.get_property('scale')
    margin = config.get_property('margin')
    opacity = config.get_property('opacity')

    Gimp.context_push()

    if file is None:
        error = 'No watermark file given'
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))
    if scale is None:
        error = 'No scale factor given'
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))
    if margin is None:
        error = 'No offset margin given'
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))
    if opacity is None:
        error = 'No opacity given'
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR,
                                           GLib.Error(error))

    # Create new layer for watermark and place it above the image.
    watermarkLayer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image, file)
    image.insert_layer(watermarkLayer, None, -1)
    # Get image width & height.
    imageWidth = image.get_width()
    imageHeight = image.get_height()
    # Get layer width & height.
    watermarkWidth = watermarkLayer.get_width()
    watermarkHeight = watermarkLayer.get_height()
    # Calculate scaled layer width & height.
    scaledWidth = math.ceil(imageWidth / scale)
    scaledHeight = math.ceil(scaledWidth * watermarkHeight / watermarkWidth)
    # Scale watermark layer.
    watermarkLayer.scale(scaledWidth, scaledHeight, False)
    # Calculate watermark layer position.
    watermarkXOff = math.ceil((imageWidth - scaledWidth) - (margin * imageWidth))
    watermarkYOff = math.ceil((imageHeight - scaledHeight) - (margin * imageHeight))
    watermarkLayer.set_offsets(watermarkXOff, watermarkYOff)
    # Set watermark layer opacity.
    watermarkLayer.set_opacity(opacity)

    Gimp.displays_flush()

    Gimp.context_pop()

    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

class MyWatermarkPlugin (Gimp.PlugIn):
    # FUTURE all other Gimp classes that have GimpParamSpecs

    ## GimpPlugIn virtual methods ##
    def do_set_i18n(self, procname):
        return False

    def do_query_procedures(self):
        return [ 'python-fu-my-watermark' ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            add_watermark, None)
        procedure.set_image_types("*")
        procedure.set_documentation ("My Watermark ",
                                     "My Watermark ",
                                     name)
        procedure.set_menu_label("My Watermark")
        procedure.set_attribution("Manoj Kumar",
                                  "Manoj Kumar",
                                  "2025")
        # Top level menu "Test"
        procedure.add_menu_path ("<Image>/Filters/Watermarks/")

        procedure.add_file_argument ("file", "_File", "File",
                                         Gimp.FileChooserAction.SAVE,
                                         False, None, GObject.ParamFlags.READWRITE)
        procedure.add_int_argument ("scale", "_Scale", "Scale", 1, 100, 10,
                                         GObject.ParamFlags.READWRITE)
        procedure.add_double_argument ("margin", "_Margin", "Margin", 0.0, 1.0, 0.005,
                                         GObject.ParamFlags.READWRITE)
        procedure.add_int_argument ("opacity", "_Opacity", "Opacity", 1, 100, 30,
                                         GObject.ParamFlags.READWRITE)

        return procedure

Gimp.main(MyWatermarkPlugin.__gtype__, sys.argv)
