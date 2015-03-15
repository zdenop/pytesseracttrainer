# Introduction #

Original author of tesseractTrainer.py Catalin Francu
[announced on tesseract-ocr mailing list](http://groups.google.com/group/tesseract-ocr/browse_thread/thread/c4073cadb2acf820?pli=1) she do not support tesseractTrainer.py anymore. For this reason new project was created to maintain this useful script.

Name was changed to easy distinguish from project [Tesseract Trainer](http://www.mushware.com/).

New contributors are welcome! Please have a look to [TODO](http://code.google.com/p/pytesseracttrainer/wiki/TODO) for ideas.

# Requirements/dependencies #

  * [python](http://www.python.org) (tested with python 2.6)
  * [PyGTK](http://www.pygtk.org) with Numeric support (otherwise command 'split' could not work optional)
  * [ImageMagick](http://www.imagemagick.org/) (identify) - need only for version pyTesseractTrainer 1.01


# Features #

  * visual editor of box file
  * multiplatform support (tested on Linux 64 bit and Windows XP)
  * unicode support (from 1.01)
  * possibility to define **bold**, _italic_, and underline font per letter
  * layout of symbols from box file try to reflect symbols on image
  * deleting, joining, splitting of symbols/boxes
  * easy and exact way of adjusting boxes
  * support for opening different image formats (tiff, png, jpeg, bmp, gif)
  * open and save tesseract v3.00 box file
  * displaying tesseract coordinate system and (0,0 at the bottom-left) and "image" coordinate system (0,0 at the top-left)
  * posibility to copy coordinates of box file with shortcut/menu

# Coordinate system #

Tesseract coordinate system used in the box file has (0,0) at the bottom-left.

![http://pytesseracttrainer.googlecode.com/files/coord_example.png](http://pytesseracttrainer.googlecode.com/files/coord_example.png)
_Example of coordinate system displayed in pyTesseractTrainer_