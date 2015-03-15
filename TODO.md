# Ideas for Contributors #

  * **localisation**
  * **undo** command
  * **zoom in/out**
  * **toolbar**
    * panel for **most used symbols**
  * **configuration** (menu and user file) for:
    1. last used directory
    1. last open files
    1. custom font
    1. localisation
    1. keyboard shortcuts
    1. panel for most used symbols
    1. themes/layout (see screenshot in [issue 1](http://code.google.com/p/pytesseracttrainer/issues/detail?id=1) as proposal)
  * support for **saving tesseract v3.00 box file** (pyTesseractTrainer can open tesseract 3.00 box file, but it saves v2.0x box file)
  * improve space/word detection (test test\_special.eng.tif in pyTesseractTrainer)
  * **multipage tiff support** (maybe it is not good idea open 200 pages tiff ;-) but maybe this can be done via '**project file**' and after adjusting all pages produce finale tiff and box file)
  * **diff against external text file** with visualization of differences in pyTesseractTrainer. For training process it common there is also available source text for training images. This feature would increase significantly productivity if somebody would start to train images and text files from [Distributed Proofreaders](http://www.pgdp.net/c/)
  * integrated training process with tesseract:
    1. generating box file from  pyTesseractTrainer
    1. visual support for analyzing box error (e.g. FAILURE! box overlaps no blobs or blobs in multiple rows; FAILURE! box overlaps blob in labelled word)


# Other Ideas #

This ideas are not connected directly to training process.

  * save text to DjVu (see article [Insert OCRed text in DjVu](http://www.ub-filosofie.ro/~solcan/wt/gnu/d/odjv.html))
  * save to PDF (see [issue 2](http://code.google.com/p/pytesseracttrainer/issues/detail?id=2) - it needs reportlab addon that is not shipped with my Linux :-( )