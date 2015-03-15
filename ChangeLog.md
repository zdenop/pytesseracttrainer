## Version 1.03 ##
_(released on Jan 04, 2011)_

  * Fixed displaying RTL chars.

## Version 1.02 ##
_(released on Sep 04, 2010)_

  * implemented improvements of Mihail Radu Solcan (function: copy of box coordinates in djvMap, htmMap; display of tesseract coordinates) http://www.ub-filosofie.ro/~solcan/wt/gnu/t/tbe.html
  * support for argument - to open image after startup (e.g. "pyTesseractTrainer.py test\_special.eng.tif")
  * menu item "Commands" is renamed to more standard "Edit"
  * support for saving tesseract 3.0 box file. If you need save file in tesseract 3.0 box file, just change global variable "SAVE\_FORMAT" to "2" (instead of "3") on line 52 before starting of pyTesseractTrainer.py
  * safe saving - pyTesseractTrainer will create backup files when you save box file
  * improved detection of wrong lines in box file
  * application will be not closed if user try to open wrong box file
  * fixed scrolling of symbol area
  * fixed entry of coordinates by keyboard
  * code cleanup


## Version 1.01 ##
_(released on Aug 13, 2010)_

  * added info about Merge Text
  * workaround for missing Numeric support in PyGTK
  * buxfix for "symbol area is not clear when another image is open"
  * bugfix for $@' symbols (used for formating internally)
  * added image filter
  * removed dependancy on identify/imagick
  * Added support for utf-8 encoded box files
  * Added support to open tesseract v3.0 box file

## Version 1.00 ##
_(released on Aug 07, 2010)_

  * Initial version -> renamed http://tesseract-ocr.googlecode.com/files/tesseractTrainer.py
  * Preparation for new buxfix release (changed name, licence)