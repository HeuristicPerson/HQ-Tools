# HQ Tools

Installation
============

1. Download the latest version of HQ Tools from [github.com/PixelGordo/HQ-Tools](https://github.com/PixelGordo/HQ-Tools) 

2. Uncompress the package wherever you want.

3. Create

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
