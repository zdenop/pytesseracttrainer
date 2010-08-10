#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SVN revision "$WCREV$"
# Date: "$WCDATE$"

# pyTesseractTrainer is editor for tesseract-ocr box files.
# pyTesseractTrainer is successor of tesseractTrainer.py 
#
# More information about project can be found on project page:
# http://pytesseracttrainer.googlecode.com
#
# pyTesseractTrainer.py
# Copyright 2010 Zdenko Podobný <zdenop at gmail.com>
# http://pytesseracttrainer.googlecode.com
# http://sk-spell.sk.cx
#
# tesseractTrainer.py
# Copyright 2007 Catalin Francu <cata at francu.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.#}}}

import pygtk
pygtk.require('2.0')
import gtk
import os
import pango
import sys
import codecs
from time import clock
from datetime import datetime, date

VERSION = '1.01'
REVISION = '23'
VERBOSE = 1  # if 1, than print additional information to standrard output
DEBUG_SPEED = 0
BASE_FONT = 'monospace'

MENU = '''<ui>
  <menubar name="MenuBar">
    <menu action="File">
      <menuitem action="Open"/>
      <menuitem action="MergeText"/>
      <menuitem action="Save"/>
      <menuitem action="Quit"/>
    </menu>
    <menu action="Commands">
      <menuitem action="Split"/>
      <menuitem action="JoinWithNext"/>
      <menuitem action="Delete"/>
    </menu>
    <menu action="Help">
      <menuitem action="About"/>
      <menuitem action="Shortcuts"/>
    </menu>
  </menubar>
</ui>'''

ATTR_BOLD = 0
ATTR_ITALIC = 1
ATTR_UNDERLINE = 2

DIR_LEFT = 0
DIR_RIGHT = 1
DIR_TOP = 2
DIR_BOTTOM = 3

def print_timing(func):
    '''http://www.daniweb.com/code/snippet216610.html'''
    def wrapper(*arg):
        t1 = clock()
        res = func(*arg)
        t2 = clock()
        if DEBUG_SPEED == 1:
            print '%s took %0.3f ms' % (func.func_name, (t2-t1)*1000.0)
        return res
    return wrapper

class Symbol:
    text = ''
    left = 0
    right = 0
    top = 0
    bottom = 0
    bold = False
    italic = False
    underline = False
    spaceBefore = False
    entry = None
    handlers = []

    @print_timing
    def setEntryFont(self):
        font = BASE_FONT
        if self.bold:
            font += ' bold'
        #endif
        if self.italic:
            font += ' italic'
        #endif
        self.entry.modify_font(pango.FontDescription(font))

        if self.underline:
            self.entry.set_width_chars(len(unicode(self.text)) + 1)
            self.entry.set_text("'" + self.text)
        else:
            self.entry.set_width_chars(len(unicode(self.text)))
            self.entry.set_text(self.text)
        #endif
    #enddef

    @print_timing
    def clone(self):
        s = Symbol()
        s.text = self.text
        s.left = self.left
        s.right = self.right
        s.top = self.top
        s.bottom = self.bottom
        s.bold = self.bold
        s.italic = self.italic
        s.underline = self.underline
        s.spaceBefore = self.spaceBefore
        s.entry = self.entry
        s.handlers = self.handlers
        return s
    #enddef

    @print_timing
    def deleteLabelBefore(self):
        e = self.entry
        box = e.get_parent()
        pos = box.child_get_property(e, "position")
        label = box.get_children()[pos - 1]
        label.destroy()
    #enddef

    @print_timing
    def __str__(self):
        return 'Text [%s] L%d R%d T%d B%d' % (
            self.text, self.left, self.right,
            self.top, self.bottom)
    #enddef
#endclass

# Returns a list of lines. Each line contains a list of symbols
# FIELD_* constants.
@print_timing
def loadBoxData(boxName, height):
    f = codecs.open(boxName, 'r', 'utf-8')
    if VERBOSE == 1:
        print datetime.now(), "File %s is opened." % boxName
    result = []
    symbolLine = []
    prevRight = -1
    line_nmbr = 1

    for line in f:
        if len(line.split()) == 6:
            (text, left, bottom, right, top, page) = line.split() # tesseract 3.00
            #print "tess 3.00"
        elif len(line.split()) == 5:
            (text, left, bottom, right, top) = line.split() # tesseract < 2.0x
            #print "tess 2.0x"
        else:
            message = "Unknown format of line %s:\n'%s'\nin box file '%s'!" \
                % (str(line_nmbr), line.strip(), boxName)
            dialog = gtk.MessageDialog(parent = None, 
                buttons = gtk.BUTTONS_CLOSE, 
                flags = gtk.DIALOG_DESTROY_WITH_PARENT,
                type = gtk.MESSAGE_WARNING, message_format = message)
            dialog.set_title("Error in box file!")
            dialog.run()
            dialog.destroy()
            sys.exit() # TODO: do not kill application  please ;-)
        line_nmbr += 1
        s = Symbol()

        # if there is more than 1 symbols in text, check for:
        # bold, italic, underline
        if len(text) > 1:
            if '@' in text[:1]:
                s.bold = True
                text = text.replace('@', '', 1)
            #endif
            if '$' in text[:1]:
                s.italic = True
                text = text.replace('$', '', 1)
            #endif
            if "'" in text[:1]:
                s.underline = True
                text = text.replace("'", "", 1)
            #endif
        #endif

        s.text = text
        s.left = int(left)
        s.right = int(right)
        s.top = height - int(top)
        s.bottom = height - int(bottom)
        s.spaceBefore = s.left >= prevRight + 6 and prevRight != -1

        if s.left < prevRight - 10:
            result.append(symbolLine)
            symbolLine = []
        #endif
        symbolLine.append(s)
        prevRight = s.right
    #endfor

    result.append(symbolLine)
    f.close()
    return result
#enddef

# Ensures that the adjustment is set to include the range of size "size"
# starting at "start"
@print_timing
def ensureVisible(adjustment, start, size):
    # Compute the visible range
    visLo = adjustment.value
    visHi = adjustment.value + adjustment.page_size
    if start <= visLo or start + size >= visHi:
        desired = start - (adjustment.page_size - size) / 2
        if desired < 0:
            desired = 0
        elif desired + adjustment.page_size >= adjustment.upper:
            desired = adjustment.upper - adjustment.page_size
        #endif
        adjustment.set_value(desired)
    #endif
#enddef

# Counts all the black pixels in column x
@print_timing
def countBlackPixels(pixels, x):
    numPixels = 0;
    for row in pixels:
        if isBlack(row[x]):
            numPixels += 1
      #endif
    #endfor
    return numPixels
#enddef

@print_timing
def isBlack(pixel):
    return pixel[0][0] + pixel[1][0] + pixel[2][0] < 128 * 3
#enddef

class MainWindow:
    pixbuf = None
    selectedRow = None
    selectedColumn = None
    buttonUpdateInProgress = None
    boxes = None

    @print_timing
    def reconnectEntries(self, rowIndex):
        row = self.boxes[rowIndex]
        for col in range(0, len(row)):
            e = row[col].entry
            for handler in row[col].handlers:
                e.disconnect(handler)
            #endfor
            row[col].handlers = [
                e.connect('focus-in-event', self.onEntryFocus,
                          rowIndex, col),
                e.connect('changed', self.onEntryChanged, rowIndex, col),
                e.connect("key-press-event", self.onEntryKeyPress, rowIndex,
                          col)]

        #endfor
    #enddef

    @print_timing
    def errorDialog(self, labelText, parent):
        dialog = gtk.Dialog("Error", parent,
                            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK))
        label = gtk.Label(labelText)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.run()
        dialog.destroy()
    #enddef

    @print_timing
    def makeGtkEntry(self, symbol, row, col):
        symbol.entry = gtk.Entry(10)
        symbol.entry.set_text(symbol.text)
        symbol.entry.set_width_chars(len(unicode(symbol.text)))
        symbol.setEntryFont()
        symbol.handlers = [
            symbol.entry.connect('focus-in-event', self.onEntryFocus, row, col),
            symbol.entry.connect('changed', self.onEntryChanged, row, col),
            symbol.entry.connect("key-press-event", self.onEntryKeyPress,
                                 row, col)]
    #enddef

    @print_timing
    def invalidateImage(self):
        width, height = self.drawingArea.window.get_size()
        self.drawingArea.window.invalidate_rect((0, 0, width, height), False)
    #enddef

    @print_timing
    def onCheckButtonToggled(self, widget, attr):
        if self.buttonUpdateInProgress or self.selectedRow == None:
            return
        #endif

        value = widget.get_active()
        symbol = self.boxes[self.selectedRow][self.selectedColumn]
        if attr == ATTR_BOLD:
            symbol.bold = value
        elif attr == ATTR_ITALIC:
            symbol.italic = value
        elif attr == ATTR_UNDERLINE:
            symbol.underline = value
        #endif

        symbol.setEntryFont()

        # The underline attribute does not apply to the entire word
        if attr == ATTR_UNDERLINE:
            return
        #endif

        row = self.boxes[self.selectedRow]
        i = self.selectedColumn - 1
        while i >= 0 and not row[i + 1].spaceBefore:
            if attr == ATTR_BOLD:
                row[i].bold = value
            elif attr == ATTR_ITALIC:
                row[i].italic = value
            #endif
            row[i].setEntryFont()
            i -= 1
        #endwhile

        i = self.selectedColumn + 1
        while i < len(row) and not row[i].spaceBefore:
            if attr == ATTR_BOLD:
                row[i].bold = value
            elif attr == ATTR_ITALIC:
                row[i].italic = value
            #endif
            row[i].setEntryFont()
            i += 1
        #endwhile
    #enddef

    @print_timing
    def onEntryFocus(self, entry, ignored, row, column):
        self.selectedRow = row
        self.selectedColumn = column

        # Force the image to refresh
        self.invalidateImage()

        # Bring the rectangle into view if necessary
        s = self.boxes[row][column]
        width = s.right - s.left
        height = s.bottom - s.top
        ensureVisible(self.scrolledWindow.get_hadjustment(), s.left, width)
        ensureVisible(self.scrolledWindow.get_vadjustment(), s.top, height)

        # Activate the formatting checkboxes and set their values
        self.setSymbolControlSensitivity(True)
        self.buttonUpdateInProgress = True
        self.boldButton.set_active(s.bold)
        self.italicButton.set_active(s.italic)
        self.underlineButton.set_active(s.underline)

        # Update the spin buttons
        self.spinLeft.set_value(s.left)
        self.spinRight.set_value(s.right)
        self.spinTop.set_value(s.top)
        self.spinBottom.set_value(s.bottom)
        self.buttonUpdateInProgress = None
    #enddef

    @print_timing
    def onEntryChanged(self, entry, row, col):
        symbol = self.boxes[row][col]
        symbol.text = entry.get_text()
        symbol.underline = symbol.text.startswith("'")
        entry.set_width_chars(len(unicode(symbol.text)))
        while symbol.text.startswith("'"):
            symbol.text = symbol.text[1:]
        #endwhile
        self.buttonUpdateInProgress = True
        self.underlineButton.set_active(symbol.underline)
        self.buttonUpdateInProgress = None
    #enddef

    # Intercept ctrl-arrow and ctrl-shift-arrow
    @print_timing
    def onEntryKeyPress(self, entry, event, row, col):
        if not event.state & gtk.gdk.CONTROL_MASK:
            return False
        #endif

        shift = event.state & gtk.gdk.SHIFT_MASK
        s = self.boxes[row][col]
        if event.keyval == 65361:          # Left arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.left += 1
            else:
                s.left -= 1
            self.spinLeft.set_value(s.left)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        elif event.keyval == 65362:          # Up arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.top += 1
            else:
                s.top -= 1
            self.spinTop.set_value(s.top)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        elif event.keyval == 65363:          # Right arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.right -= 1
            else:
                s.right += 1
            self.spinRight.set_value(s.right)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        elif event.keyval == 65364:          # Down arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.bottom -= 1
            else:
                s.bottom += 1
            self.spinBottom.set_value(s.bottom)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        #endif
        return False
    #enddef

    @print_timing
    def onSpinButtonChanged(self, button, dir):
        if self.buttonUpdateInProgress or self.selectedRow == None:
            return
        #endif

        value = int(button.get_value())
        s = self.boxes[self.selectedRow][self.selectedColumn]
        prevValue = (s.left, s.right, s.top, s.bottom)[dir]

        if dir == DIR_LEFT:
            s.left = value
        elif dir == DIR_RIGHT:
            s.right = value
        elif dir == DIR_TOP:
            s.top = value
        elif dir == DIR_BOTTOM:
            s.bottom = value
        #endif
        self.invalidateImage()
    #enddef

    @print_timing
    def populateTextVBox(self):
        ''' Creates text entries from the boxes'''
        # first we need to remove old symbols 
        # in case this is not first open file
        self.textVBox.foreach(lambda widget:self.textVBox.remove(widget))
        
        row = 0
        for line in self.boxes:
            col = 0
            hbox = gtk.HBox()
            self.textVBox.pack_start(hbox)
            hbox.show()
            for s in line:
                if s.spaceBefore:
                    label = gtk.Label('   ')
                    hbox.pack_start(label, False, False, 0)
                    label.show()
                #endif

                self.makeGtkEntry(s, row, col)
                hbox.pack_start(s.entry, False, False, 0)
                s.entry.show()
                col += 1
            #endfor
            row += 1
        #endfor
    #enddef

    @print_timing
    def redrawArea(self, drawingArea, event):
        '''reddraw area of selected symbol + add rectangle'''
        gc = drawingArea.get_style().fg_gc[gtk.STATE_NORMAL]
        color = gtk.gdk.color_parse("red")
        drawingArea.modify_fg(gtk.STATE_NORMAL, color)  # color of rectangle
        if self.pixbuf:
            drawingArea.window.draw_pixbuf(gc, self.pixbuf, 0, 0, 0, 0)
        #endif
        if self.selectedRow != None:
            s = self.boxes[self.selectedRow][self.selectedColumn]
            width = s.right - s.left
            height = s.bottom - s.top
            drawingArea.window.draw_rectangle(gc, False, s.left, s.top,
                                              width, height)
        #endif
    #enddef

    @print_timing
    def loadImageAndBoxes(self, imageName, fileChooser):
        (name, extension) = imageName.rsplit('.', 1)
        boxName = name + '.box'

        # Make sure that the image exists
        try:
            f = open(imageName, 'r')
            f.close()
        except IOError:
            self.errorDialog('Cannot find the specified file', fileChooser)
            return False
        #endtry

        if VERBOSE == 1:
            print datetime.now(), "File %s is opened." % imageName
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(imageName)
        height = self.pixbuf.get_height()

        try:
            self.boxes = loadBoxData(boxName, height)
            self.loadedBoxFile = boxName
            self.window.set_title("pyTesseractTrainer: %s" % boxName)
        except IOError:
            self.errorDialog('Cannot load image, because there is no '
                             'corresponding box file', fileChooser)
            return False
        #endtry

        if VERBOSE == 1:
            print datetime.now(), "Displaying image..."
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(imageName)
        self.drawingArea.set_size_request(self.pixbuf.get_width(), height)
        if VERBOSE == 1:
            print datetime.now(), "Displaying symbols..."
        self.populateTextVBox()

        # Set adjustments on all spin buttons
        if VERBOSE == 1:
            print datetime.now(), "Adjusting all spin buttons..."
        self.spinLeft.set_adjustment(
            gtk.Adjustment(0, 0, self.pixbuf.get_width(), 1, 1))
        self.spinRight.set_adjustment(
            gtk.Adjustment(0, 0, self.pixbuf.get_width(), 1, 1))
        self.spinTop.set_adjustment(gtk.Adjustment(0, 0, height, 1, 1))
        self.spinBottom.set_adjustment(gtk.Adjustment(0, 0, height, 1, 1))

        self.setImageControlSensitivity(True)
        self.selectedRow = 0
        self.selectedColumn = 0
        self.boxes[0][0].entry.grab_focus()
        if VERBOSE == 1:
            print datetime.now(), "Function loadImageAndBoxes is finished."
        return True
    #enddef

    @print_timing
    def mergeTextFile(self, fileName, fileChooser):
        row = 0
        col = 0
        try:
            f = open(fileName, 'r')
            for line in f:
                line = unicode(line)
                for char in line:
                    if not char.isspace():
                        if row < len(self.boxes):
                            self.boxes[row][col].text = char
                            self.boxes[row][col].setEntryFont()
                            col += 1
                            if col == len(self.boxes[row]):
                                col = 0
                                row += 1
                            #endif
                        #endif
                    #endif
                #endfor
            #endfor
            f.close()
        except IOError:
            self.errorDialog('File ' + fileName + ' does not exist',
                             fileChooser)
        #endtry
    #enddef

    @print_timing
    def doFileOpen(self, action):
        chooser = gtk.FileChooserDialog(
            "Open Image", self.window, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name("TIFF files")
        filter.add_pattern("*.tif")
        filter.add_pattern("*.tiff")
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("Image files")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.png")
        filter.add_pattern("*.bmp")
        filter.add_pattern("*.tif")
        filter.add_pattern("*.tiff")
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            fileName = chooser.get_filename()
            self.loadImageAndBoxes(fileName, chooser)
        #endif

        chooser.destroy()
    #enddef

    @print_timing
    def doFileMergeText(self, action):
        chooser = gtk.FileChooserDialog(
            "Merge Text File", self.window, gtk.FILE_CHOOSER_ACTION_OPEN,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
             gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            fileName = chooser.get_filename()
            self.mergeTextFile(fileName, chooser)
        #endif

        chooser.destroy()
    #enddef

    @print_timing
    def doFileSave(self, action):
        if self.boxes == None:
            self.errorDialog('Nothing to save', self.window)
            return
        #endif
        height = self.pixbuf.get_height()

        f = open(self.loadedBoxFile, 'w')
        for row in self.boxes:
            for s in row:
                text = s.text
                if s.underline:
                    text = "'" + text
                #endif
                if s.italic:
                    text = '$' + text
                #endif
                if s.bold:
                    text = '@' + text
                #endif
                f.write('%s %d %d %d %d\n' %
                        (text, s.left, height - s.bottom, s.right,
                         height - s.top))
            #endfor
        #endfor
        f.close()
    #enddef

    @print_timing
    def doHelpAbout(self, action):
        dialog = gtk.Dialog('About pyTesseractTrainer', self.window,
                            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_size_request(450, 200)
        label = gtk.Label(
            'pyTesseractTrainer version %s, revision: %s\n'
            'website: pytesseracttrainer.googlecode.com\n'
            '\n'
            'Copyright 2010 Zdenko Podobný <zdenop at gmail.com>\n'
            'Copyright 2007 Cătălin Frâncu <cata at francu.com>\n'
            '\n'
            'This program is free software: you can redistribute it and/or '
            'modify it under the terms of the GNU General Public License v3' 
            % (VERSION,REVISION))
        label.set_line_wrap(True)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.run()
        dialog.destroy()
    #enddef

    @print_timing
    def doHelpShortcuts(self, action):
        dialog = gtk.Dialog('Keyboard shortcuts', self.window,
                            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_size_request(450, 200)
        label = gtk.Label(
            'Keyboard shortcuts\n'
            '\n'
            'Ctrl-B: mark entire word as bold\n'
            'Ctrl-I: mark entire word as italic\n'
            'Ctrl-U: mark current symbol as italic\n'
            'Ctrl-arrow: grow box up, down, left or right\n'
            'Ctrl-Shift-arrow: shrink box up, down, left or right\n'
            'Ctrl-1: merge current symbol with next symbol\n'
            'Ctrl-2: split current symbol vertically\n'
            'Ctrl-D: delete current symbol\n'
            )
        label.set_line_wrap(True)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.run()
        dialog.destroy()
    #enddef

    @print_timing
    def findSplitPoint(self, symbol):
        '''Looks 5 pixels to the left and right of the median divider'''
        subpixbuf = self.pixbuf.subpixbuf(symbol.left, symbol.top,
                                          symbol.right - symbol.left,
                                          symbol.bottom - symbol.top)

        # get_pixels_array work only with PyGTK with support of Numeric
        try:
            pixels = subpixbuf.get_pixels_array()

            height = len(pixels)
            width = len(pixels[0])
            bestX = -1
            bestNumPixels = 1000000

            for x in range(width // 2 - 5, width // 2 + 6):
                numPixels = countBlackPixels(pixels, x)
                # print x, numPixels
                if numPixels < bestNumPixels:
                    bestX = x
                    bestNumPixels = numPixels
                #endif
            #endfor
        except:  # workaround for missing support in PyGTK
            error = "It looks like your PyGTK has no support for" + \
                    "Numeric!\nCommand 'split' will not work best way."
            #self.errorDialog(error, self.window)
            if VERBOSE == 1:
                print error
            bestX = subpixbuf.get_width() / 2

        return bestX + symbol.left
    #enddef

    @print_timing
    def doCommandsSplit(self, action):
        if self.selectedRow == None:
            self.errorDialog('Click into a cell first.', self.window)
            return
        #endif

        row = self.boxes[self.selectedRow]
        this = row[self.selectedColumn]
        clone = this.clone()
        this.right = self.findSplitPoint(this)
        clone.left = this.right
        clone.spaceBefore = False
        clone.text = '*'
        self.makeGtkEntry(clone, self.selectedRow, self.selectedColumn + 1)
        clone.setEntryFont()
        hbox = this.entry.get_parent()
        hbox.pack_start(clone.entry, False, False, 0)

        # To reorder the child, use col + 1 and add all the word breaks
        pos = self.selectedColumn + 1
        for s in row[0:self.selectedColumn + 1]:
            if s.spaceBefore:
                pos += 1
            #endif
        #endfor

        hbox.reorder_child(clone.entry, pos)
        clone.entry.show()
        row.insert(self.selectedColumn + 1, clone)
        self.reconnectEntries(self.selectedRow)

        self.invalidateImage()
        self.buttonUpdateInProgress = True
        self.spinLeft.set_value(this.left)
        self.spinRight.set_value(this.right)
        self.spinTop.set_value(this.top)
        self.spinBottom.set_value(this.bottom)
        self.buttonUpdateInProgress = None
    #enddef

    @print_timing
    def doCommandsJoin(self, action):
        if self.selectedRow == None:
            self.errorDialog('Click into a cell first.', self.window)
            return
        #endif

        if self.selectedColumn + 1 == len(self.boxes[self.selectedRow]):
            self.errorDialog('There is no next symbol on this line!',
                             self.window)
            return
        #endif

        this = self.boxes[self.selectedRow][self.selectedColumn]
        next = self.boxes[self.selectedRow][self.selectedColumn + 1]
        this.text += next.text
        this.left = min(this.left, next.left)
        this.right = max(this.right, next.right)
        this.top = min(this.top, next.top)
        this.bottom = max(this.bottom, next.bottom)
        this.setEntryFont()
        next.entry.destroy()
        del self.boxes[self.selectedRow][self.selectedColumn + 1]
        self.reconnectEntries(self.selectedRow)
        self.invalidateImage()

        self.buttonUpdateInProgress = True
        self.spinLeft.set_value(this.left)
        self.spinRight.set_value(this.right)
        self.spinTop.set_value(this.top)
        self.spinBottom.set_value(this.bottom)
        self.buttonUpdateInProgress = None
    #enddef

    @print_timing
    def doCommandsDelete(self, action):
        if self.selectedRow == None:
            self.errorDialog('Click into a cell first.', self.window)
            return
        #endif

        row = self.boxes[self.selectedRow]
        this = row[self.selectedColumn]
        if self.selectedColumn + 1< len(row):
            next = row[self.selectedColumn + 1]
        else:
            next = None
        #endif

        if this.spaceBefore:
            if next != None and not next.spaceBefore:
                next.spaceBefore = True
            else:
                # delete the label before this symbol
                this.deleteLabelBefore()
            #endif
        #endif

        this.entry.destroy()
        del row[self.selectedColumn]
        self.reconnectEntries(self.selectedRow)

        # Find the next cell to focus
        if self.selectedColumn >= len(row):
            self.selectedRow += 1
            self.selectedColumn = 0
        #endif

        if self.selectedRow >= len(self.boxes):
            self.selectedRow = len(self.boxes) - 1
            self.selectedColumn = len(self.boxes[self.selectedRow]) - 1
        #endif

        self.boxes[self.selectedRow][self.selectedColumn].entry.grab_focus()
    #enddef

    @print_timing
    def setImageControlSensitivity(self, bool):
        self.actionGroup.get_action('MergeText').set_sensitive(bool)
        self.actionGroup.get_action('Save').set_sensitive(bool)
    #enddef

    @print_timing
    def setSymbolControlSensitivity(self, bool):
        self.buttonBox.set_sensitive(bool)
        self.actionGroup.get_action('Commands').set_sensitive(bool)
    #enddef

    @print_timing
    def makeMenu(self):
        uiManager = gtk.UIManager()
        self.accelGroup = uiManager.get_accel_group()
        self.window.add_accel_group(self.accelGroup)
        self.actionGroup = gtk.ActionGroup('UIManagerExample')
        self.actionGroup.add_actions(
            [('Open', gtk.STOCK_OPEN, '_Open Image...', None, None,
              self.doFileOpen),
             ('MergeText', None, 'Merge _Text...', '<Control>T', None,
              self.doFileMergeText),
             ('Save', gtk.STOCK_SAVE, '_Save Box Info', None, None,
              self.doFileSave),
             ('Quit', gtk.STOCK_QUIT, None, None, None,
              lambda w: gtk.main_quit()),
             ('File', None, '_File'),
             ('Commands', None, '_Commands'),
             ('Split', None, '_Split Symbol', '<Control>2', None,
              self.doCommandsSplit),
             ('JoinWithNext', None, '_Join with Next Symbol', '<Control>1',
              None, self.doCommandsJoin),
             ('Delete', None, '_Delete Symbol', '<Control>D',
              None, self.doCommandsDelete),
             ('Help', None, '_Help'),
             ('About', None, '_About', None, None, self.doHelpAbout),
             ('Shortcuts', None, '_Keyboard shotcuts', None, None,
              self.doHelpShortcuts),
             ])
        uiManager.insert_action_group(self.actionGroup, 0)
        uiManager.add_ui_from_string(MENU)
        return uiManager.get_widget('/MenuBar')
    #enddef

    @print_timing
    def __init__(self):
        if VERBOSE == 1:
            print "Platform:", sys.platform, "\nTheme directory:",gtk.rc_get_theme_dir()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("pyTesseractTrainer - Tesseract Box Editor version %s, revision:%s" % (VERSION,REVISION))
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.set_size_request(800, 600)

        vbox = gtk.VBox(False, 2)
        self.window.add(vbox)
        vbox.show()

        menuBar = self.makeMenu()
        vbox.pack_start(menuBar, False)

        self.scrolledWindow = gtk.ScrolledWindow()
        self.scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
        vbox.pack_start(self.scrolledWindow, True, True, 2)
        self.scrolledWindow.show()

        self.drawingArea = gtk.DrawingArea()
        self.drawingArea.connect("expose-event", self.redrawArea)
        self.scrolledWindow.add_with_viewport(self.drawingArea)
        self.drawingArea.show()

        self.textScroll = gtk.ScrolledWindow()
        self.textScroll.set_policy(gtk.POLICY_AUTOMATIC,
                                   gtk.POLICY_AUTOMATIC)
        vbox.pack_start(self.textScroll, True, True, 2)
        self.textScroll.show()

        self.textVBox = gtk.VBox()
        self.textScroll.add_with_viewport(self.textVBox)
        self.textVBox.show()

        self.buttonBox = gtk.HBox(False, 0)
        vbox.pack_start(self.buttonBox, False, False, 2)        
        self.buttonBox.show()

        b = gtk.CheckButton("_Bold", True)
        self.buttonBox.pack_start(b, False, False, 10)
        b.connect("toggled", self.onCheckButtonToggled, ATTR_BOLD)
        b.add_accelerator("activate", self.accelGroup, ord('B'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.boldButton = b

        b = gtk.CheckButton("_Italic", True)
        self.buttonBox.pack_start(b, False, False, 10)
        b.connect("toggled", self.onCheckButtonToggled, ATTR_ITALIC)
        b.add_accelerator("activate", self.accelGroup, ord('I'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.italicButton = b

        b = gtk.CheckButton("_Underline", True)
        self.buttonBox.pack_start(b, False, False, 10)
        b.connect("toggled", self.onCheckButtonToggled, ATTR_UNDERLINE)
        b.add_accelerator("activate", self.accelGroup, ord('U'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.underlineButton = b

        self.spinBottom = gtk.SpinButton()
        self.spinBottom.connect("changed", self.onSpinButtonChanged, DIR_BOTTOM)
        self.buttonBox.pack_end(self.spinBottom, False, False, 0)
        self.spinBottom.show()
        l = gtk.Label("     Bottom:");
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.spinTop = gtk.SpinButton()
        self.spinTop.connect("changed", self.onSpinButtonChanged, DIR_TOP)
        self.buttonBox.pack_end(self.spinTop, False, False, 0)
        self.spinTop.show()
        l = gtk.Label("     Top:");
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.spinRight = gtk.SpinButton()
        self.spinRight.connect("changed", self.onSpinButtonChanged, DIR_RIGHT)
        self.buttonBox.pack_end(self.spinRight, False, False, 0)
        self.spinRight.show()
        l = gtk.Label("     Right:");
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.spinLeft = gtk.SpinButton()
        self.spinLeft.connect("changed", self.onSpinButtonChanged, DIR_LEFT)
        self.buttonBox.pack_end(self.spinLeft, False, False, 0)
        self.spinLeft.show()
        l = gtk.Label("Left:");
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.setImageControlSensitivity(False)
        self.setSymbolControlSensitivity(False)
        self.window.show()
    #enddef
#endClass

@print_timing
def main():
    gtk.main()
    return 0
#enddef

if __name__ == "__main__":
    MainWindow()
    main()
