# HQ Tools

Installation
============

1. Download the latest version of HQ Tools from [github.com/PixelGordo/HQ-Tools](1) 

2. Uncompress the package wherever you want.

3. Create

    [1]: https://github.com/PixelGordo/HQ-Tools

HQ Copy (hq_copy.py)
====================

Usage
-----

(This part of the documentation comes straight from the command line tool help)

Usage: `hq_copy.py [-h] [-s] [DC][cmst][cmst] dat source destination`

A command line utility to copy and rename files between different formats
using a ROM dat file.

Positional arguments:

* `[DC][cmst][cmst]`  Renaming mode. 1st letter specifies the usage of clean (`C`)
                      or dirty (`D`) hashes. 2nd and 3rd letter specify the source
                      and destination format: crc32 (`c`), md5 (`m`), sha1 (`s`), and
                      title (`t`). i.e. `Dct` will use dirty hashes to copy files
                      from crc32 naming scheme to real title scheme.

* `dat`               Source dat file. i.e. `/home/john/snes.dat`

* `source`            Source directory or file. i.e. `/home/carl/pictures` or
                      `/home/ann/145879ab.png`

* `destination`       Destination directory. i.e. `/home/cecil/output_pics`

Optional arguments:

* `-h`, `--help`      Show this help message and exit

* `-s`                Simulation mode; files won't be copied.

* `-r R`              Regex pattern and group. i.e. "(.*),0". Everything BEFORE
                      the comma is the pattern and everything AFTER the comma is
                      the group to capture.


Workaround to rename clean hashes to dirty hashes or vice versa
---------------------------------------------------------------

For program simplicity, you can only specify a global clean or dirty mode for source and destination hashes. It means
that for example you can't rename **clean crc32** -> **dirty crc32**. There is a quick workaround for it. In the first
step, you rename your clean crc32 files to title mode:

    hq_copy Cct dat_file source_path intermediate_path
    
Then you can rename the title files from the intermediate path to your final path using dirty hashes:

    hqrename Dtc dat_file intermediate_path destination_path
    

HQ Image Convert (hq_img_convert.py)
====================================

Usage
-----

(This part of the documentation comes straight from the command line tool help)

Usage: `hq_img_convert.py [-h] [-a A] [-e {None,bmp,gif,jpg,png}] [-f F] [-b B] [-r R] [-s S] {frame,magcover} src dst`

A command line utility to convert and "enrich" video-game screenshots.

Positional arguments:

* `{frame,magcover}`  Image mode. i.e. `frame`.

* `src`               Source image file. i.e. `/home/john/original-pic.jpg`.

* `dst`                   Destination image file. i.e. `/home/carl/pictures/final-pic.png`.

Optional arguments:

* `-h, --help`        Show this help message and exit

* `-a A`              Aspect ratio or platform alias. i.e. `-a 16,9` or `-a nes`. Valid platform alias are: `snes`
                      (Super Nintendo), `gbc` (GameBoy), `gba` (GameBoy Advance), `lynx` (Lynx), `gb` (GameBoy),
                      `megadrive` (Megadrive), `nes` (N.E.S.).

* `-e {None,bmp,gif,jpg,png}` Change dst extension. i.e. `-e jpg` will create a jpg image. If you are converting a
                      single file, you can simply define the extension by the output file name. For example `output.png`
                      will produce a png file. When you are converting a whole directory of images, the output file name
                      for each of the files will be the sourcefile name; so the parameter `-e` allows you to change the
                      extension.
* `-f F`              Focus point relative coordinates x, y. i.e. `-f 0.0,1.0` would be bottom-left corner.

* `-b B`              Background hex color in RGBA format. i.e. `-b ff000080`.

* `-r R`              Image rotation. i.e. `-r 15+5` will be a rotation of 15 degrees anticlockwise plus a random
                      rotation of +/- 5 degrees.
* `-s S`              Image size. i.e. `-s 320,240`. This is the maximum image size. Images will be enlarged or reduced
                      maintaining their aspect ratio until they occupy the maximum possible area of the area defined by
                      this parameter. i.e. a square image which is 30x30 pixels with a size parameter of `-s 100,200`
                      will end being 100x100 pixels since that's the biggest square that can fit inside the rectangle of
                      100x200 pixels.
