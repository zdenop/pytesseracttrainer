#!/usr/bin/python
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
# tesseractBoxEditor.py
# Modified version for work with djvused
# Modified by Mihail Radu Solcan
# Last modification: 2008-12-28
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
"""
pyTesseractTrainer is editor for tesseract-ocr box files.
pyTesseractTrainer is successor of tesseractTrainer.py
"""
import pygtk
pygtk.require('2.0')
import gtk
import pango
import sys
import os
import shutil
import codecs
import ConfigParser
from time import clock
from datetime import datetime
from os import path,  name,  environ,  mkdir

# parameters
APPNAME = "tesseract-ocr"
VERSION = '1.03'
REVISION = '50'
# default values
BASE_FONT = 'unifont 11'
NUMBER_COLOR = "green"
PUNC_COLOR = "blue"
LATER_COLOR = '#FF0000'
STD_COLOR = '#000000'
AB_COLOR = '#FF0000'

DEBUG_SPEED = 0
VERBOSE = 1  # if 1, than print additional information to standard output

MENU = \
    '''<ui>
  <menubar name="MenuBar">
    <menu action="File">
      <menuitem action="Open"/>
      <menuitem action="MergeText"/>
      <menuitem action="Save"/>
      <menuitem action="Quit"/>
    </menu>
    <menu action="Edit">
      <menuitem action="Copy"/>
      <menuitem action="djvMap"/>
      <menuitem action="htmMap"/>
      <separator/>
      <menuitem action="Split"/>
      <menuitem action="JoinWithNext"/>
      <menuitem action="Delete"/>
    </menu>
    <menu action="Tools">
      <menuitem action="Export text"/>
      <menuitem action="Export text - lines"/>
      <separator/>
      <menuitem action="Preferences"/>
    </menu>
    <menu action="Help" name="HelpMenu">
      <menuitem action="About"/>
      <menuitem action="AboutMergeText"/>
      <menuitem action="Shortcuts"/>
    </menu>
  </menubar>
</ui>'''

ATTR_BOLD = 0
ATTR_ITALIC = 1
ATTR_UNDERLINE = 2
ATTR_LATER = 3

DIR_LEFT = 0
DIR_RIGHT = 1
DIR_TOP = 2
DIR_BOTTOM = 3
DIR_RUP = 4
DIR_LDOWN = 5


def print_timing(func):
    '''http://www.daniweb.com/code/snippet216610.html'''

    def wrapper(*arg):
        '''time calculation'''
        tm1 = clock()
        res = func(*arg)
        tm2 = clock()
        if DEBUG_SPEED == 1:
            print datetime.now(), '%s took %0.3f ms' % (func.func_name,
                    (tm2 - tm1) * 1000.0)
        return res

    return wrapper

def write_default(cfg):
    '''init default parameters'''
    # TODO: test if exits - if not create ;-)
    config = ConfigParser.ConfigParser()
    config.add_section('System')
    config.set('System', 'save_format', '3') # tesseract v3 box format
    config.set('System', 'revision', REVISION)
    config.add_section('GUI')
    config.set('GUI', 'font', BASE_FONT)
    config.set('GUI', 'standard', STD_COLOR)
    config.set('GUI', 'later', LATER_COLOR)
    config.set('GUI', 'active box', AB_COLOR)

    # write configuration
    with open(cfg, 'wb') as configfile:
        config.write(configfile)

def check_config():
    """
    Check/Create configuration file
    """
    if sys.platform == "win32" or name == "nt":
        # Try env APPDATA or USERPROFILE or HOMEDRIVE/HOMEPATH
        appdata = path.join(environ['APPDATA'], APPNAME)
    else:
        appdata = path.expanduser(path.join("~", "." + APPNAME))
    config_file = path.join(appdata,  "pyTesseractTrainer.rc")
    if path.exists(path.expanduser(appdata)) == False:
        print appdata
        mkdir(path.expanduser(appdata))
    if path.isfile(path.expanduser(config_file)) == False:
        write_default(config_file)
    return config_file

def read_cfg(section, option):
    file_config = check_config()
    config = ConfigParser.ConfigParser()
    config.read(file_config)
    result = config.get(section, option)
    print section, option,  result
    return result

class Symbol:
    '''class symbol '''
    text = u''
    left = 0
    right = 0
    top = 0
    rightup = 0
    bottom = 0
    leftdown = 0
    page = 0
    bold = False
    italic = False
    underline = False
    later = False
    spaceBefore = False
    entry = None
    handlers = []

    @print_timing
    def setEntryFont(self):
        font = BASE_FONT
        self.entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(STD_COLOR))

        if self.bold:
            font += ' bold'

        # endif

        if self.italic:
            font += ' italic'

        # endif

        self.entry.modify_font(pango.FontDescription(font))

        if self.underline:
            self.entry.set_width_chars(len(unicode(self.text)) + 1)
            self.entry.set_text("'" + unicode(self.text))
        else:
            self.entry.set_width_chars(len(unicode(self.text)))
            self.entry.set_text(unicode(self.text))

        # endif

        if self.later:
            self.entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(LATER_COLOR))

        # endif
    # enddef

    @print_timing
    def clone(self):
        s = Symbol()
        s.text = self.text
        s.left = self.left
        s.right = self.right
        s.top = self.top
        s.bottom = self.bottom
        s.page = self.page
        s.rightup = self.rightup
        s.leftdown = self.leftdown
        s.bold = self.bold
        s.italic = self.italic
        s.underline = self.underline
        s.later = self.later
        s.spaceBefore = self.spaceBefore
        s.entry = self.entry
        s.handlers = self.handlers
        return s

    # enddef

    @print_timing
    def deleteLabelBefore(self):
        e = self.entry
        box = e.get_parent()
        pos = box.child_get_property(e, 'position')
        label = box.get_children()[pos - 1]
        label.destroy()

    # enddef

    @print_timing
    def __str__(self):
        return 'Text [%s] L%d R%d T%d B%d P%d LD%d RU%d' % (self.text,
                self.left, self.right, self.top, self.bottom, self.page,
                self.leftdown,  self.rightup)

    # enddef
# endclass

def safe_backup(f_path, keep_original=True):
    """
    Rename a file or directory safely without overwriting an existing
    backup of the same name.
    http://www.5dollarwhitebox.org/drupal/node/91
    """
    count = -1
    new_path = None
    print "cesta:", f_path
    while True:
        if path.exists(f_path):
            if count == -1:
                new_path = "%s.bak" % (f_path)
            else:
                new_path = "%s.bak.%s" % (f_path, count)
            if path.exists(new_path):
                count += 1
                continue
            else:
                if keep_original:
                    if path.isfile(f_path):
                        shutil.copy(f_path, new_path)
                    elif path.isdir(f_path):
                        shutil.copytree(f_path, new_path)
                else:
                    shutil.move(f_path, new_path)
                break
        else:
            break
    return new_path

def find_format(boxname):
    ''''find format of box file'''
    expected_format = 0  # expected number of items
    wrong_row = ""  # here will be list of wrong rows
    wrong_fl = False  # even first line is wrong
                      # so we can not use it for expected format
    row = 1

    fbn = open(boxname,'r')
    for line in fbn:
        nmbr_items = len(line.split())
        if row == 1 and (nmbr_items == 5 or nmbr_items == 6):
            expected_format = nmbr_items
        elif row == 1 and (nmbr_items != 5 or nmbr_items != 6):
            wrong_fl = True
        if nmbr_items != expected_format:
            wrong_row = wrong_row + str(row) + ", "
        row += 1
    fbn.close()

    if wrong_row == "":  # file is ok - it has only one format
        if expected_format == 5:
            if VERBOSE > 0:
                print datetime.now(), 'Find tesseract 2 box file.'
            return 2
        if expected_format == 6:
            if VERBOSE > 0:
                print datetime.now(), 'Find tesseract 3 box file.'
            return 3
    else:  # there lines with different formats!!!
        message = "Wrong format of '%s'." % boxname
        if wrong_fl:
            message =  message + " Even first line is not correct!"
        else:
            message =  message + " Please check these rows: '%s'." \
                % wrong_row[:-2]

        dialog = gtk.MessageDialog(parent=None,
                buttons=gtk.BUTTONS_CLOSE,
                flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                type=gtk.MESSAGE_WARNING, message_format=message)
        dialog.set_title('Error in box file!')
        dialog.run()
        dialog.destroy()
        return -1 # wrong format of box file

@print_timing
def loadBoxData(boxname, height):
    '''Returns a list of lines. Each line contains a list of symbols
    FIELD_* constants.'''

    open_format = find_format(boxname)

    if open_format == -1:
        return -1 # wrong format of box file

    #fbn = codecs.open(boxname, 'r', 'utf-8')
    fbn = open(boxname, 'r')
    if VERBOSE > 0:
        print datetime.now(), 'File %s is opened.' % boxname
    result = []
    symbolLine = []
    prevRight = -1
    page = 0

    for line in fbn:
        if open_format == 3:
            (text, left, bottom, right, top, page) = line.split()
        elif open_format == 2:
            (text, left, bottom, right, top) = line.split()

        s = Symbol()

        # if there is more than 1 symbols in text, check for:
        # bold, italic, underline

        if len(text) > 1:
            if '@' in text[:1]:
                s.bold = True
                text = text.replace('@', '', 1)

            # endif

            if '$' in text[:1]:
                s.italic = True
                text = text.replace('$', '', 1)

            # endif

            if "'" in text[:1]:
                s.underline = True
                text = text.replace("'", '', 1)

            # endif

            if '⁂' in text[:1]:
                s.later = True
                text = text.replace('⁂', '', 1)

            # endif

        # endif

        s.text = text
        s.left = int(left)
        s.right = int(right)
        # initial values for y coords as in tesseract
        s.rightup = int(top)
        s.leftdown = int(bottom)
        # end initial values
        s.top = height - s.rightup
        s.bottom = height - s.leftdown
        s.page = int(page)

        s.spaceBefore = s.left >= prevRight + 6 and prevRight != -1

        if s.left < prevRight - 10:
            result.append(symbolLine)
            symbolLine = []

        # endif

        symbolLine.append(s)
        prevRight = s.right

    # endfor

    result.append(symbolLine)
    fbn.close()
    return result

# enddef

@print_timing
def ensureVisible(adjustment, start, size):
    '''
    Ensures that the adjustment is set to include the range of size "size"
    starting at "start"
    '''
    # Compute the visible range
    visLo = adjustment.value
    visHi = adjustment.value + adjustment.page_size
    if start <= visLo or start + size >= visHi:
        desired = start - (adjustment.page_size - size) / 2
        if desired < 0:
            desired = 0
        elif desired + adjustment.page_size >= adjustment.upper:
            desired = adjustment.upper - adjustment.page_size

        # endif

        adjustment.set_value(desired)

    # endif
# enddef


@print_timing
def countBlackPixels(pixels, x):
    '''Counts all the black pixels in column x'''

    numPixels = 0
    for row in pixels:
        if isBlack(row[x]):
            numPixels += 1

      # endif
    # endfor

    return numPixels

# enddef


@print_timing
def isBlack(pixel):
    return pixel[0][0] + pixel[1][0] + pixel[2][0] < 128 * 3

# enddef


class MainWindow:
    """doc string"""
    pixbuf = None
    selectedRow = None
    selectedColumn = None
    buttonUpdateInProgress = None
    boxes = None
    area_show = False

    def color_set_cb(self, colorbutton):
        color = colorbutton.get_color()
        alpha = colorbutton.get_alpha()
        print 'You have selected the color:', \
              color.red, color.green, color.blue, 'with alpha:', alpha
        return

    def font_set_cb(self, fontbutton):
        font = fontbutton.get_font_name()
        print 'You have selected the font:', font
        return

    def show_prefs(self, action):  # TODO
        prefs = gtk.Dialog(("Preferences"), None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_APPLY, gtk.RESPONSE_ACCEPT))

        hbox1 = gtk.HBox()
        bf_label = gtk.Label("Font: ")
        fontbutton = gtk.FontButton(read_cfg('GUI','font'))
        fontbutton.set_use_font(True)
        fontbutton.set_title('Select a font')
        #fontbutton.connect('font-set', self.font_set_cb)
        hbox1.pack_start(bf_label, True, False)
        hbox1.pack_start(fontbutton, False, False)

        sc_label = gtk.Label("Standard text color: ")
        sc_button = gtk.ColorButton(gtk.gdk.color_parse(read_cfg('GUI','standard')))
        sc_button.set_title('Select a Color')
        #sc_button.connect('color-set', self.color_set_cb)
        hbox2 = gtk.HBox()
        hbox2.pack_start(sc_label, False)
        hbox2.pack_start(sc_button)

        hbox3 = gtk.HBox()
        lc_label = gtk.Label("Text color for later: ")
        lc_button = gtk.ColorButton(gtk.gdk.color_parse(read_cfg('GUI','later')))
        lc_button.set_title('Select a Color')
        #lc_button.connect('color-set', self.color_set_cb)
        hbox3.pack_start(lc_label, False, False)
        hbox3.pack_start(lc_button)

        hbox4 = gtk.HBox()
        ab_label = gtk.Label("Active box color: ")
        ab_button = gtk.ColorButton(gtk.gdk.color_parse(read_cfg('GUI','active box')))
        ab_button.set_title('Select a Color')
        #ab_button.connect('color-set', self.color_set_cb)
        hbox4.pack_start(ab_label, False, False)
        hbox4.pack_start(ab_button, True, False)

        hbox5 = gtk.HBox()
        ab_label = gtk.Label("Save format: ")
        sf_cb = gtk.combo_box_new_text()
        sf_cb.append_text('2')
        sf_cb.append_text('3')
        sf_cb .set_active(1)
        hbox5.pack_start(ab_label, False, False)
        hbox5.pack_start(sf_cb, True, False)

        prefs.vbox.pack_start(hbox1)
        prefs.vbox.pack_start(hbox2)
        prefs.vbox.pack_start(hbox3)
        prefs.vbox.pack_start(hbox4)
        prefs.vbox.pack_start(hbox5)
        prefs.show_all()

        response = prefs.run()
        if response == gtk.RESPONSE_ACCEPT:
            # TODO: write save
            #config.set('System', 'save_format', ab_entry.get_text())
            BASE_FONT = fontbutton.get_font_name()
            STD_COLOR = sc_button.get_color()
            LATER_COLOR = lc_button.get_color()
            AB_COLOR = ab_button.get_color()
            #save_format = int(read_cfg('System', 'save_format'))
            save_format = sf_cb.get_active_text()
        else:
            prefs.destroy()
        prefs.destroy()

    @print_timing
    def reconnectEntries(self, rowIndex):
        row = self.boxes[rowIndex]
        for col in range(0, len(row)):
            e = row[col].entry
            for handler in row[col].handlers:
                e.disconnect(handler)

            # endfor

            row[col].handlers = [e.connect('focus-in-event',
                                 self.onEntryFocus, rowIndex, col),
                                 e.connect('changed',
                                 self.onEntryChanged, rowIndex, col),
                                 e.connect('key-press-event',
                                 self.onEntryKeyPress, rowIndex, col)]

        # endfor
    # enddef

    @print_timing
    def errorDialog(self, labelText, parent):
        dialog = gtk.Dialog('Error', parent, gtk.DIALOG_NO_SEPARATOR
                            | gtk.DIALOG_MODAL, (gtk.STOCK_OK,
                            gtk.RESPONSE_OK))
        label = gtk.Label(labelText)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.run()
        dialog.destroy()

    # enddef

    @print_timing
    def makeGtkEntry( self, symbol, row, col):
        if VERBOSE > 1:
            print datetime.now(), \
            u"symbol: '', row: '%s', col: '%s', page: '%s'" \
                % (row, col, symbol.page)
        symbol.entry = gtk.Entry()
        symbol.handlers = [symbol.entry.connect('focus-in-event',
                           self.onEntryFocus, row, col),
                           symbol.entry.connect('changed',
                           self.onEntryChanged, row, col),
                           symbol.entry.connect('key-press-event',
                           self.onEntryKeyPress, row, col)]

    # enddef

    @print_timing
    def invalidateImage(self):
        '''refresh image'''
        (width, height) = self.drawingArea.window.get_size()
        self.drawingArea.window.invalidate_rect((0, 0, width, height),
                False)

    # enddef

    @print_timing
    def onCheckButtonToggled(self, widget, attr):
        '''Set atribut to symbol'''
        if self.buttonUpdateInProgress or self.selectedRow == None:
            return

        # endif

        value = widget.get_active()
        symbol = self.boxes[self.selectedRow][self.selectedColumn]
        if attr == ATTR_BOLD:
            symbol.bold = value
        elif attr == ATTR_ITALIC:
            symbol.italic = value
        elif attr == ATTR_UNDERLINE:
            symbol.underline = value
        elif attr == ATTR_LATER:
            symbol.later = value

        # endif

        symbol.setEntryFont()

        # The underline attribute does not apply to the entire word

        if attr == ATTR_UNDERLINE:
            return

        # endif

        row = self.boxes[self.selectedRow]
        i = self.selectedColumn - 1
        while i >= 0 and not row[i + 1].spaceBefore:
            if attr == ATTR_BOLD:
                row[i].bold = value
            elif attr == ATTR_ITALIC:
                row[i].italic = value
            elif attr == ATTR_LATER:
                row[i].later = value

            # endif

            row[i].setEntryFont()
            i -= 1

        # endwhile

        i = self.selectedColumn + 1
        while i < len(row) and not row[i].spaceBefore:
            if attr == ATTR_BOLD:
                row[i].bold = value
            elif attr == ATTR_ITALIC:
                row[i].italic = value
            elif attr == ATTR_LATER:
                row[i].later = value

            # endif

            row[i].setEntryFont()
            i += 1

        # endwhile
    # enddef

    @print_timing
    def onEntryFocus(self, entry, ignored, row, column):
        self.selectedRow = row
        self.selectedColumn = column
#        entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#0000ff'))

        # Force the image to refresh
        self.invalidateImage()

        # Scroll textView if necessary
        alloc = entry.get_allocation()
        adj_v = self.textScroll.get_vadjustment()
        if alloc.y < adj_v.value or alloc.y > adj_v.value + adj_v.page_size:
            adj_v.set_value(min(alloc.y, adj_v.upper-adj_v.page_size))
        adj_h = self.textScroll.get_hadjustment()
        if alloc.x < adj_h.value or alloc.x > adj_h.value + adj_h.page_size:
            adj_h.set_value(min(alloc.x, adj_h.upper-adj_h.page_size))

        # Bring the rectangle into view if necessary
        s = self.boxes[row][column]
        width = s.right - s.left
        height = s.bottom - s.top
        ensureVisible(self.scrolledWindow.get_hadjustment(), s.left,
                      width)
        print "548", self.scrolledWindow.get_hadjustment().value,s.left, width
        ensureVisible(self.scrolledWindow.get_vadjustment(), s.top,
                      height)
        print "551", self.scrolledWindow.get_hadjustment().value, s.top, height

        # Activate the formatting checkboxes and set their values

        self.setSymbolControlSensitivity(True)
        self.buttonUpdateInProgress = True
        self.boldButton.set_active(s.bold)
        self.italicButton.set_active(s.italic)
        self.underlineButton.set_active(s.underline)
        self.laterButton.set_active(s.later)

        # Set adjustments/limits on all spin buttons
        i_height = self.pixbuf.get_height()
        i_width = self.pixbuf.get_width()
        self.spinLeft.set_adjustment(gtk.Adjustment(0, 0, s.right, 1, 10))
        self.spinRight.set_adjustment(gtk.Adjustment(0, s.left, i_width, 1, 10))
        self.spinTop.set_adjustment(gtk.Adjustment(0, 0, s.bottom, 1, 10))
        self.spinRUp.set_adjustment(gtk.Adjustment(0, s.leftdown, i_height,
                                                   1, 10))
        self.spinBottom.set_adjustment(gtk.Adjustment(0, s.top, i_height,
                                                      1, 10))
        self.spinLDown.set_adjustment(gtk.Adjustment(0, 0, s.rightup, 1, 10))

        # Update the spin buttons
        self.spinLeft.set_value(s.left)
        self.spinRight.set_value(s.right)
        self.spinTop.set_value(s.top)
        self.spinRUp.set_value(s.rightup)
        self.spinBottom.set_value(s.bottom)
        self.spinLDown.set_value(s.leftdown)

        self.buttonUpdateInProgress = None

    # enddef

    @print_timing
    def onEntryChanged(self, entry, row, col):
        symbol = self.boxes[row][col]
        symbol.text = entry.get_text()
        symbol.underline = symbol.text.startswith("'")
        entry.set_width_chars(len(unicode(symbol.text)))
        while symbol.text.startswith("'"):
            symbol.text = symbol.text[1:]

        # endwhile

        self.buttonUpdateInProgress = True
        self.underlineButton.set_active(symbol.underline)
        self.buttonUpdateInProgress = None

    # enddef

    @print_timing
    def onEntryKeyPress(self, entry, event, row, col):
        '''Intercept ctrl-arrow and ctrl-shift-arrow'''
        if not event.state & gtk.gdk.CONTROL_MASK:
            return False

        # endif

        shift = event.state & gtk.gdk.SHIFT_MASK
        s = self.boxes[row][col]
        if event.keyval == 65361:  # Left arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.left += 1
            else:
                s.left -= 1
            self.spinLeft.set_value(s.left)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        elif event.keyval == 65362:  # Up arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.top += 1
                s.rightup -= 1
            else:
                s.top -= 1
                s.rightup += 1
            self.spinTop.set_value(s.top)
            self.spinRUp.set_value(s.rightup)
            self.spinTop.set_value(s.top)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        elif event.keyval == 65363:  # Right arrow

            self.buttonUpdateInProgress = True
            if shift:
                s.right -= 1
            else:
                s.right += 1
            self.spinRight.set_value(s.right)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True
        elif event.keyval == 65364:  # Down arrow
            self.buttonUpdateInProgress = True
            if shift:
                s.bottom -= 1
                s.leftdown += 1
            else:
                s.bottom += 1
                s.leftdown -= 1
            self.spinBottom.set_value(s.bottom)
            self.spinLDown.set_value(s.leftdown)
            self.buttonUpdateInProgress = None
            self.invalidateImage()
            return True


        # endif

        return False

    # enddef

    @print_timing
    def onSpinButtonChanged(self, button, dir):
        if self.buttonUpdateInProgress or self.selectedRow == None:
            return

        # endif

        value = int(button.get_value())
        s = self.boxes[self.selectedRow][self.selectedColumn]
        prevValue = (s.left, s.right, s.top, s.bottom, s.rightup, \
                     s.leftdown)[dir]
        i_height = self.pixbuf.get_height()
        i_width = self.pixbuf.get_width()

        if dir == DIR_LEFT:
            s.left = value
            self.spinRight.set_adjustment(gtk.Adjustment(s.right, s.left,
                                                         i_width, 1, 10))
        elif dir == DIR_RIGHT:
            s.right = value
            self.spinLeft.set_adjustment(gtk.Adjustment(s.left, 0,
                                                        s.right, 1, 10))
        elif dir == DIR_TOP:
            s.top = value
            s.rightup = s.rightup + prevValue - value
            self.spinRUp.set_value(s.rightup)
            self.spinBottom.set_adjustment(gtk.Adjustment(s.bottom, s.top,
                                                          i_height, 1, 10))
            self.spinLDown.set_adjustment(gtk.Adjustment(s.leftdown, 0,
                                                         s.rightup, 1, 10))
        elif dir == DIR_BOTTOM:
            s.bottom = value
            s.leftdown = s.leftdown + prevValue - value
            self.spinLDown.set_value(s.leftdown)
            self.spinTop.set_adjustment(gtk.Adjustment(s.top, 0,
                                                       s.bottom, 1, 10))
            self.spinRUp.set_adjustment(gtk.Adjustment(s.rightup, s.leftdown,
                                                       i_height, 1, 10))
        elif dir == DIR_RUP:
            s.rightup = value
            s.top = s.top + prevValue - value
            self.spinTop.set_value(s.top)
            self.spinBottom.set_adjustment(gtk.Adjustment(s.bottom, s.top,
                                                          i_height, 1, 10))
            self.spinLDown.set_adjustment(gtk.Adjustment(s.leftdown, 0,
                                                         s.rightup, 1, 10))
        elif dir == DIR_LDOWN:
            s.leftdown = value
            s.bottom = s.bottom + prevValue - value
            self.spinBottom.set_value(s.bottom)
            self.spinTop.set_adjustment(gtk.Adjustment(s.top, 0,
                                                       s.bottom, 1, 10))
            self.spinRUp.set_adjustment(gtk.Adjustment(s.rightup, s.leftdown,
                                                       i_height, 1, 10))
        # endif
        self.invalidateImage()

    # enddef

    @print_timing
    def populateTextVBox(self):
        ''' Creates text entries from the boxes'''

        # first we need to remove old symbols
        # in case this is not first open file
        self.textVBox.foreach(lambda widget: \
                              self.textVBox.remove(widget))

        row = 0
        for line in self.boxes:
            col = 0
            hbox = gtk.HBox()
            #self.textVBox.pack_start(hbox)
            self.textVBox.pack_start(hbox, False, True, 3)
            hbox.show()
            for s in line:
                if s.spaceBefore:
                    label = gtk.Label('   ')
                    hbox.pack_start(label, False, False, 0)
                    label.show()

                # endif

                self.makeGtkEntry(s, row, col)
                hbox.pack_start(s.entry, expand=False, fill=False, padding=0)
                # following entry properties must be used after hbox.pack_start
                # otherwise RTL chars will receives offset
                # print 'scroll-offset:', s.entry.get_property('scroll-offset')
                s.entry.set_text(s.text)
                s.entry.set_width_chars(len(unicode(s.text)))
                s.setEntryFont()
                s.entry.show()
                col += 1

            # endfor

            row += 1

        # endfor
    # enddef

    #@print_timing
    def redrawArea(self, drawingArea, event):
        '''redraw area of selected symbol + add rectangle'''
        if self.selectedRow != None:
            gc = drawingArea.get_style().fg_gc[gtk.STATE_NORMAL]
            if self.pixbuf:
                drawingArea.window.draw_pixbuf(gc, self.pixbuf, 0, 0, 0, 0)

            # endif

            s = self.boxes[self.selectedRow][self.selectedColumn]
            width = s.right - s.left
            height = s.bottom - s.top
            drawingArea.window.draw_rectangle(gc,
                False, s.left, s.top, width, height)

        # endif
    # enddef

    @print_timing
    def filecheck(self, imageName):
        '''
        Make sure that the image, box files exists
        find box file format
        '''
        try:
            fc = open(imageName, 'r')
            fc.close()
        except IOError:
            self.errorDialog('Cannot find the %s file' % imageName,
                             self.window)
            return False

        boxname = imageName.rsplit('.', 1)[0] + '.box'
        try:
            fb = open(boxname, 'r')
            fb.close()
        except IOError:
            self.errorDialog('Cannot find the %s file' % boxname,
                             self.window)
            return False
        return True

    @print_timing
    def loadImageAndBoxes(self, imageName, fileChooser):
        try:
            (name, extension) = imageName.rsplit('.', 1)
            boxname = name + '.box'
        except:
            pass

        file_ok = self.filecheck(imageName)
        if file_ok == False:
            return False

        self.pixbuf = gtk.gdk.pixbuf_new_from_file(imageName)
        height = self.pixbuf.get_height()
        self.boxes = loadBoxData(boxname, height)
        if self.boxes == -1:  # wrong format of box file
            self.pixbuf = ""  # clear area
            self.selectedRow = None
            self.textVBox.foreach(lambda widget: \
                              self.textVBox.remove(widget))
            return False
        self.loadedBoxFile = boxname
        self.window.set_title('pyTesseractTrainer - %s: %s' % \
                (VERSION, boxname))

        if VERBOSE > 0:
            print datetime.now(), 'File %s is opened.' % imageName

        if VERBOSE > 0:
            print datetime.now(), 'Displaying image...'
        self.drawingArea.set_size_request(self.pixbuf.get_width(),
                height)
        if VERBOSE > 0:
            print datetime.now(), 'Displaying symbols...'
        self.populateTextVBox()

        self.setImageControlSensitivity(True)
        self.selectedRow = 0
        self.selectedColumn = 0
        self.boxes[0][0].entry.grab_focus()
        if VERBOSE > 0:
            print datetime.now(), \
                'Function loadImageAndBoxes is finished.'
        return True

    # enddef

    @print_timing
    def mergeTextFile(self, fileName, fileChooser):
        row = 0
        col = 0
        try:
            ft = open(fileName, 'r')
            for line in ft:
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

                            # endif
                        # endif
                    # endif
                # endfor
            # endfor

            ft.close()
        except IOError:
            self.errorDialog('File ' + fileName + ' does not exist',
                             fileChooser)

        # endtry
    # enddef

    @print_timing
    def doFileOpen(self, action):
        chooser = gtk.FileChooserDialog('Open Image', self.window,
                gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name('TIFF files')
        filter.add_pattern('*.tif')
        filter.add_pattern('*.tiff')
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name('Image files')
        filter.add_pattern('*.jpg')
        filter.add_pattern('*.jpeg')
        filter.add_pattern('*.png')
        filter.add_pattern('*.bmp')
        filter.add_pattern('*.tif')
        filter.add_pattern('*.tiff')
        chooser.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        chooser.add_filter(filter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            fileName = chooser.get_filename()
            self.loadImageAndBoxes(fileName, chooser)

        # endif

        chooser.destroy()

    # enddef

    @print_timing
    def doFileMergeText(self, action):
        chooser = gtk.FileChooserDialog('Merge Text File', self.window,
                gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL,
                gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        filter = gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        chooser.add_filter(filter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            fileName = chooser.get_filename()
            self.mergeTextFile(fileName, chooser)

        # endif

        chooser.destroy()

    # enddef

    @print_timing
    def doFileSave(self, action):
        '''Save modified box file'''
        save_format = int(read_cfg('System', 'save_format'))

        if self.boxes == None:
            self.errorDialog('Nothing to save', self.window)
            return

        # endif

        height = self.pixbuf.get_height()

        path = self.loadedBoxFile
        bak_path = safe_backup(path)
        if VERBOSE > 0:
            if bak_path:
                print '%s safely backed up as %s' % (path, bak_path)
            else:
                print '%s does not exist, nothing to backup' % path

        save_f = open(self.loadedBoxFile, 'w')
        for row in self.boxes:
            for s in row:
                text = s.text
                if s.underline:
                    text = "'" + text

                # endif

                if s.italic:
                    text = '$' + text

                # endif

                if s.bold:
                    text = '@' + text

                # endif

                if s.later:
                    text = '⁂' + text

                # endif

                if  save_format == 2:
                    save_f.write('%s %d %d %d %d\n' % (text, s.left, height
                            - s.bottom, s.right, height - s.top))
                else:
                    save_f.write('%s %d %d %d %d %d\n' % (text, s.left, height
                            - s.bottom, s.right, height - s.top, s.page))

            # endfor
        # endfor

        save_f.close()
    # enddef

    @print_timing
    def doHelpAbout(self, action):
        about = gtk.AboutDialog()
        about.set_program_name("pyTesseractTrainer")
        about.set_version("%s, revision: %s"  % (VERSION, REVISION))
        about.set_copyright('Copyright 2010 Zdenko Podobný <zdenop at gmail.com>\n'
            'Copyright 2008 Mihail Radu Solcan (djvused and image maps)\n'
            'Copyright 2007 Cătălin Frâncu <cata at francu.com>\n')
        about.set_comments('pyTesseractTrainer is editor for tesseract-ocr box files.\n\n'
            'This program is free software: you can redistribute it and/or '
            'modify it under the terms of the GNU General Public License v3')
        about.set_website("http://pytesseracttrainer.googlecode.com")
        #about.set_logo(gtk.gdk.pixbuf_new_from_file("battery.png"))
        about.run()
        about.destroy()
    # enddef

    def doHelpAboutMerge(self, action):
        dialog = gtk.Dialog('About Merge Text...', self.window,
                            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_size_request(450, 250)

        font = pango.FontDescription('Arial Bold 12')
        label = gtk.Label('Function: Merge Text\n')
        label.modify_font(font)
        label.show()
        dialog.vbox.pack_start(label, False, False)

        label = gtk.Label(
        'This function takes text form external file and put it to '
        'currrent boxes. Number of boxes should fit tu number of '
        'symbols in file. If they did not match, you should '
        'split/join/delete symbols&boxs before running "Merge Text...".\n'
        '\n'
        'This is usefull if you have correct text from training image '
        'in external file.')
        label.set_line_wrap(True)
        label.show()
        dialog.vbox.pack_end(label, False, False)
        dialog.run()
        dialog.destroy()

    # enddef

    @print_timing
    def doHelpShortcuts(self, action):
        dialog = gtk.Dialog('Keyboard shortcuts', self.window,
                            gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK))
        dialog.set_size_request(450, 250)
        label = gtk.Label(
            'Keyboard shortcuts\n'
            '\n'
            'Ctrl-B: mark entire word as bold\n'
            'Ctrl-I: mark entire word as italic\n'
            'Ctrl-U: mark current symbol as underline\n'
            'Ctrl-I: mark entire word for later check\n'
            'Ctrl-arrow: grow box up, down, left or right\n'
            'Ctrl-Shift-arrow: shrink box up, down, left or right\n'
            'Ctrl-1: merge current symbol&box with next symbol\n'
            'Ctrl-2: split current symbol&box vertically\n'
            'Ctrl-C: copy coordinates (djvu txt style)\n'
            'Ctrl-A: copy coordinates (djvu ant style)\n'
            'Ctrl-M: copy coordinates (html image map style)\n'
            'Ctrl-D: delete current symbol&box\n')
        label.set_line_wrap(True)
        dialog.vbox.pack_start(label, True, True, 0)
        label.show()
        dialog.run()
        dialog.destroy()

    # enddef

    @print_timing
    def doEditCopy(self, action):
        this = self.boxes[self.selectedRow][self.selectedColumn]
        coords = '%s %s %s %s' % (this.left, this.leftdown, this.right, \
                                  this.rightup)
        clipboard = gtk.clipboard_get("CLIPBOARD")
        clipboard.set_text(coords, len=-1)
    #enddef

    @print_timing
    def doEditdjvMap(self, action):
        this = self.boxes[self.selectedRow][self.selectedColumn]
        area_width = this.right - this.left
        area_height = this.rightup - this.leftdown
        coords = '%s %s %s %s' % \
                (this.left, this.leftdown, area_width, area_height)
        clipboard = gtk.clipboard_get("CLIPBOARD")
        clipboard.set_text(coords, len=-1)
    #enddef

    @print_timing
    def doEdithtmMap(self, action):
        this = self.boxes[self.selectedRow][self.selectedColumn]
        coords = '%s,%s,%s,%s' % (this.left, this.top, this.right, this.bottom)
        clipboard = gtk.clipboard_get("CLIPBOARD")
        clipboard.set_text(coords, len=-1)
    #enddef

    @print_timing
    def findSplitPoint(self, symbol):
        '''Looks 5 pixels to the left and right of the median divider'''

        subpixbuf = self.pixbuf.subpixbuf(symbol.left, symbol.top,
                symbol.right - symbol.left, symbol.bottom - symbol.top)

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
        except:
           # workaround for missing support in PyGTK
            error = 'It looks like your PyGTK has no support for ' \
                + "Numeric!\nCommand 'split' will not work best way."
            # self.errorDialog(error, self.window)

            if VERBOSE > 0:
                print error
            bestX = subpixbuf.get_width() / 2

        return bestX + symbol.left

    # enddef

    @print_timing
    def doEditSplit(self, action):
        '''Split box/symbol'''
        if self.selectedRow == None:
            self.errorDialog('Click into a cell first.', self.window)
            return

        # endif

        row = self.boxes[self.selectedRow]
        this = row[self.selectedColumn]
        clone = this.clone()
        this.right = self.findSplitPoint(this)
        clone.left = this.right
        clone.spaceBefore = False
        clone.text = '*'
        self.makeGtkEntry(clone, self.selectedRow, self.selectedColumn
                          + 1)
        clone.setEntryFont()
        hbox = this.entry.get_parent()
        hbox.pack_start(clone.entry, False, False, 0)

        # To reorder the child, use col + 1 and add all the word breaks
        pos = self.selectedColumn + 1
        for s in row[0:self.selectedColumn + 1]:
            if s.spaceBefore:
                pos += 1

            # endif
        # endfor

        hbox.reorder_child(clone.entry, pos)
        clone.entry.show()
        row.insert(self.selectedColumn + 1, clone)
        self.reconnectEntries(self.selectedRow)

        self.invalidateImage()
        self.buttonUpdateInProgress = True
        self.spinLeft.set_value(this.left)
        self.spinRight.set_value(this.right)
        self.spinTop.set_value(this.top)
        self.spinRUp.set_value(this.rightup)
        self.spinBottom.set_value(this.bottom)
        self.spinLDown.set_value(this.leftdown)
        self.buttonUpdateInProgress = None
        self.boxes[self.selectedRow][self.selectedColumn].entry.grab_focus()

    # enddef

    @print_timing
    def doEditJoin(self, action):
        '''Join box/symbol with next box/symbol'''
        if self.selectedRow == None:
            self.errorDialog('Click into a cell first.', self.window)
            return

        # endif

        if self.selectedColumn + 1 == len(self.boxes[self.selectedRow]):
            self.errorDialog('There is no next symbol on this line!',
                             self.window)
            return

        # endif

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
        self.spinRUp.set_value(this.rightup)
        self.spinBottom.set_value(this.bottom)
        self.spinLDown.set_value(this.leftdown)
        self.buttonUpdateInProgress = None

        # select content of joined boxes
        self.boxes[self.selectedRow][self.selectedColumn].entry.grab_focus()

    # enddef

    @print_timing
    def doEditDelete(self, action):
        '''Delete box/symbol'''
        if self.selectedRow == None:
            self.errorDialog('Click into a cell first.', self.window)
            return

        # endif

        row = self.boxes[self.selectedRow]
        this = row[self.selectedColumn]
        if self.selectedColumn + 1 < len(row):
            next = row[self.selectedColumn + 1]
        else:
            next = None

        # endif

        if this.spaceBefore:
            if next != None and not next.spaceBefore:
                next.spaceBefore = True
            else:

                # delete the label before this symbol

                this.deleteLabelBefore()

            # endif
        # endif

        this.entry.destroy()
        del row[self.selectedColumn]
        self.reconnectEntries(self.selectedRow)

        # Find the next cell to focus

        if self.selectedColumn >= len(row):
            self.selectedRow += 1
            self.selectedColumn = 0

        # endif

        if self.selectedRow >= len(self.boxes):
            self.selectedRow = len(self.boxes) - 1
            self.selectedColumn = len(self.boxes[self.selectedRow]) - 1

        # endif

        self.boxes[self.selectedRow][self.selectedColumn].entry.grab_focus()

    # enddef

    @print_timing
    def setImageControlSensitivity(self, bool):
        '''If image is not open menu actions will be blocked'''
        self.actionGroup.get_action('MergeText').set_sensitive(bool)
        self.actionGroup.get_action('Save').set_sensitive(bool)

    # enddef

    @print_timing
    def setSymbolControlSensitivity(self, bool):
        '''If symbols are not loaded actions will be blocked'''
        self.buttonBox.set_sensitive(bool)
        self.actionGroup.get_action('Edit').set_sensitive(bool)

    # enddef

    @print_timing
    def doExportText(self, action):
        '''
        Export content of the boxes as text file with paragraphs.
        Paragraph are identified by intendation from left margin.
        '''
        height = self.pixbuf.get_height()

        xmin_last = 0
        ymin_last = 0
        xmax_last = 0
        ymax_last = 0

        text_line = ""
        linenumber = 0
        rx_min = 0
        rx_max = 0
        ry_min = 0
        ry_max = 0

        last_rx_max = 0
        line_text = []
        line_start = []
        line_end = []

        for row in self.boxes:
            for s in row:
                    xmin = s.left
                    ymin = height - s.bottom
                    xmax = s.right
                    ymax = height - s.top

                    if rx_min == 0:
                        rx_min = xmin
                        ry_min = ymin
                        rx_max = xmax
                        ry_max = ymax

                    rx_min = min(rx_min, xmin)
                    ry_min = min(ry_min, ymin)
                    rx_max = max(rx_max, xmax)
                    ry_max = max(ry_max, ymax)

                    if xmin >= xmax_last + 6 and xmax_last != -1:  # new word

                        if len(text_line) <> 0:
                            text_line += " " + s.text
                        else:
                            text_line += s.text
                            rx_min = 0
                    elif xmin < xmax_last - 10:
                        line_text.append(text_line)
                        text_line = s.text
                        line_start.append(rx_min)
                        line_end.append(rx_max)

                        rx_min = 0
                        rx_max = 0
                        ry_min = 0
                        ry_max = 0
                        linenumber += 1
                    else:
                        text_line += s.text

                    ymin_last = ymin
                    ymax_last =  ymax
                    xmin_last = xmin
                    xmax_last =  xmax

        if VERBOSE > 0:
            for start, end, text in zip(line_start, line_end, line_text):
                print '{0}\t{1}\t{2}'.format(start, end, text)

        last_end = 0
        page = ""

        for start, end, text in zip(line_start, line_end, line_text):
            page += text
            if (end - last_end) < -3:
                page += '\n'
            else:
                if page[-1] == '-':
                    page = page[0:-1]
                else:
                    page += ' '
            last_end = end

        text_file = self.loadedBoxFile.rsplit('.', 1)[0] + '_p.txt'
        bak_path = safe_backup(text_file)
        if VERBOSE > 0:
            if bak_path:
                print '%s safely backed up as %s' % (text_file, bak_path)
            else:
                print '%s does not exist, nothing to backup' % text_file

        export_file = open(text_file, 'w')
        for a_line in page:
            export_file.write(a_line)
        export_file.close()
    # enddef

    @print_timing
    def doExportTextLines(self, action):
        '''Export content of the boxes as text.'''
        # TODO: clean this code

        height = self.pixbuf.get_height()
        xmin_last = 0
        ymin_last = 0
        xmax_last = 0
        ymax_last = 0

        text_line = ""
        linenumber = 0
        rx_min = 0
        rx_max = 0
        ry_min = 0
        ry_max = 0

        last_rx_max = 0
        line_text = []
        line_start = []
        line_end = []

        for row in self.boxes:
            for s in row:
                    xmin = s.left
                    ymin = height - s.bottom
                    xmax = s.right
                    ymax = height - s.top

                    if rx_min == 0:
                        rx_min = xmin
                        ry_min = ymin
                        rx_max = xmax
                        ry_max = ymax

                    rx_min = min(rx_min, xmin)
                    ry_min = min(ry_min, ymin)
                    rx_max = max(rx_max, xmax)
                    ry_max = max(ry_max, ymax)

                    if xmin >= xmax_last + 6 and xmax_last != -1:  # new word

                        if len(text_line) <> 0:
                            text_line += " " + s.text
                        else:
                            text_line += s.text
                            rx_min = 0
                    elif xmin < xmax_last - 10:
                        line_text.append(text_line)
                        text_line = s.text
                        line_start.append(rx_min)
                        line_end.append(rx_max)

                        rx_min = 0
                        rx_max = 0
                        ry_min = 0
                        ry_max = 0
                        linenumber += 1
                    else:
                        text_line += s.text

                    ymin_last = ymin
                    ymax_last =  ymax
                    xmin_last = xmin
                    xmax_last =  xmax

        text_file = self.loadedBoxFile.rsplit('.', 1)[0] + '.text'
        bak_path = safe_backup(text_file)
        if VERBOSE > 0:
            if bak_path:
                print '%s safely backed up as %s' % (text_file, bak_path)
            else:
                print '%s does not exist, nothing to backup' % text_file

        export_file = open(text_file, 'w')
        for start, end, text in zip(line_start, line_end, line_text):
            if VERBOSE > 0:
                print '{0}\t{1}\t{2}'.format(start, end, text)
            export_file.write(text + "\n")
        export_file.close()
    # enddef

    @print_timing
    def makeMenu(self):
        uiManager = gtk.UIManager()
        self.accelGroup = uiManager.get_accel_group()
        self.window.add_accel_group(self.accelGroup)
        self.actionGroup = gtk.ActionGroup('UIManagerExample')
        self.actionGroup.add_actions(
            [('Open', gtk.STOCK_OPEN, '_Open Image...', None, None,
              self.doFileOpen),
             ('MergeText', None, '_Merge Text...', '<Control>3', None,
              self.doFileMergeText),
             ('Save', gtk.STOCK_SAVE, '_Save Box Info', None, None,
              self.doFileSave),
             ('Quit', gtk.STOCK_QUIT, None, None, None,
              lambda w: gtk.main_quit()),
             ('File', gtk.STOCK_FILE, '_File'),
             ('Edit', gtk.STOCK_EDIT, '_Edit'),
             ('Copy', gtk.STOCK_COPY, 'Copy _tesseract coords', '<Control>T', None,
              self.doEditCopy),
             ('djvMap', gtk.STOCK_COPY, 'Copy _djvMap coords', '<Control>A', None,
              self.doEditdjvMap),
             ('htmMap', gtk.STOCK_COPY, 'Copy _htmMap coords', '<Control>M', None,
              self.doEdithtmMap),
             ('Split', gtk.STOCK_CUT, '_Split Symbol&Box', '<Control>2', None,
              self.doEditSplit),
             ('JoinWithNext', gtk.STOCK_ADD, '_Join with Next Symbol&Box',
              '<Control>1', None, self.doEditJoin),
             ('Delete', gtk.STOCK_DELETE , '_Delete Symbol&Box', '<Control>D',
              None, self.doEditDelete),
             ('Tools', gtk.STOCK_PREFERENCES, '_Tools'),
             ('Export text', None, 'Export _text', None, None,
               self.doExportText),
             ('Export text - lines', None, 'Export text - _lines', '<Control>L', None,
               self.doExportTextLines),
             ('Preferences', gtk.STOCK_PROPERTIES, ('_Preferences...'),
               '<Ctrl>P', ('Preferences'), self.show_prefs),
             ('Help', gtk.STOCK_HELP, '_Help'),
             ('About', gtk.STOCK_ABOUT, '_About', None, None, self.doHelpAbout),
             ('AboutMergeText', None, 'About Merge Text', None, None,
                self.doHelpAboutMerge),
             ('Shortcuts', None, '_Keyboard shotcuts', None, None,
              self.doHelpShortcuts),
             ])
        uiManager.insert_action_group(self.actionGroup, 0)
        uiManager.add_ui_from_string(MENU)
        uiManager.get_widget('/MenuBar/HelpMenu').set_right_justified(True)
        return uiManager.get_widget('/MenuBar')
    #enddef

    # enddef

    @print_timing
    def __init__(self):
        if VERBOSE > 0:
            print 'Platform:', sys.platform
        check_config()

        BASE_FONT = read_cfg('GUI', 'font')
        STD_COLOR = read_cfg('GUI', 'standard')

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.set_title('pyTesseractTrainer - Tesseract Box '
                              + 'Editor version %s, revision:%s'
                              % (VERSION, REVISION))
        self.window.set_size_request(840, 600)

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
        color = gtk.gdk.color_parse('red')
        self.drawingArea.modify_fg(gtk.STATE_NORMAL, color)  # color of rectangle
        self.drawingArea.connect('expose-event', self.redrawArea)
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

        b = gtk.CheckButton('_Bold', True)
        self.buttonBox.pack_start(b, False, False, 5)
        b.connect('toggled', self.onCheckButtonToggled, ATTR_BOLD)
        b.add_accelerator('activate', self.accelGroup, ord('B'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.boldButton = b

        b = gtk.CheckButton('_Italic', True)
        self.buttonBox.pack_start(b, False, False, 5)
        b.connect('toggled', self.onCheckButtonToggled, ATTR_ITALIC)
        b.add_accelerator('activate', self.accelGroup, ord('I'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.italicButton = b

        b = gtk.CheckButton('_Underline', True)
        self.buttonBox.pack_start(b, False, False, 5)
        b.connect('toggled', self.onCheckButtonToggled, ATTR_UNDERLINE)
        b.add_accelerator('activate', self.accelGroup, ord('U'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.underlineButton = b

        b = gtk.CheckButton('_Later', True)
        b.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse(LATER_COLOR))
        self.buttonBox.pack_start(b, False, False, 5)
        b.connect('toggled', self.onCheckButtonToggled, ATTR_LATER)
        b.add_accelerator('activate', self.accelGroup, ord('L'),
                          gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        b.show()
        self.laterButton = b

        self.spinBottom = gtk.SpinButton()
        self.spinBottom.set_wrap(True)
        self.spinBottom.connect("value_changed", self.onSpinButtonChanged,
                                DIR_BOTTOM)
        self.buttonBox.pack_end(self.spinBottom, False, False, 0)
        self.spinBottom.show()
        l = gtk.Label(' Bottom:')
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.spinTop = gtk.SpinButton()
        self.spinTop.connect('value_changed', self.onSpinButtonChanged,
                             DIR_TOP)
        self.buttonBox.pack_end(self.spinTop, False, False, 0)
        self.spinTop.show()
        l = gtk.Label(' Top:')
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.spinRUp = gtk.SpinButton()
        self.spinRUp.connect("value_changed", self.onSpinButtonChanged,
                             DIR_RUP)
        self.buttonBox.pack_end(self.spinRUp, False, False, 0)
        self.spinRUp.show()
        lru = gtk.Label(' r-up:')
        self.buttonBox.pack_end(lru, False, False, 0)
        lru.show()

        self.spinRight = gtk.SpinButton()
        self.spinRight.connect('value_changed', self.onSpinButtonChanged,
                               DIR_RIGHT)
        self.buttonBox.pack_end(self.spinRight, False, False, 0)
        self.spinRight.show()
        l = gtk.Label(' Right:')
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.spinLDown = gtk.SpinButton()
        self.spinLDown.connect('value_changed', self.onSpinButtonChanged,
                               DIR_LDOWN)
        self.buttonBox.pack_end(self.spinLDown, False, False, 0)
        self.spinLDown.show()
        lld = gtk.Label(' l-down:')
        self.buttonBox.pack_end(lld, False, False, 0)
        lld.show()

        self.spinLeft = gtk.SpinButton()
        self.spinLeft.connect('value_changed', self.onSpinButtonChanged,
                              DIR_LEFT)
        self.buttonBox.pack_end(self.spinLeft, False, False, 0)
        self.spinLeft.show()
        l = gtk.Label('Left:')
        self.buttonBox.pack_end(l, False, False, 0)
        l.show()

        self.setImageControlSensitivity(False)
        self.setSymbolControlSensitivity(False)
        self.window.show_all()

        if len(sys.argv) >= 2:
            argfilename = sys.argv[1]
            self.loadImageAndBoxes(argfilename, self.window)
        else:
            argfilename = None
        self.isPaused = False

    # enddef
# endClass


@print_timing
def main():
    '''main'''
    gtk.main()
    return 0

# enddef

if __name__ == '__main__':
    MainWindow()
    main()
