hq_img_convert effects
======================

1. Parameters
-------------

* `-a`, aspect ratio

* `-c`, color

* `-e`, extension

* `-f`, focus (#TODO: Change name)

* `-r`, rotation

* `-s`, size


2. Modes
--------

### 1. *frame* - Picture frame


### 2. *hbars* - Horizontal bars

### 3. *magcover* - Magazine cover

### 4. mosaic

### 5. *vbars* - Vertical bars

* `-c` controls the overlay color. So, for example, `-c ff0000` would mean the whole image is covered with red while
  `-c ff000080` would cover the image with half-transparent red.

* `-r` controls de rotation of the bars. The bars are vertical in the original image, but then they are rotated before
  being applied to the final image.
  
* `-s` is the final size of the image. Aspect ratio won't be preserved so the vertical bars will always cover the entire
  size given.

![Alt](images/vbars_src_dst.png)  
*vbars source and destination*

Example:
    
    hq_img_convert.py vbars -o 6,32 -c ff000080 -r 10 -s 640,480 "src/marioworld.png" "dst/marioworld.png"

The process followed by the image is:

![Alt](images/vbars_1.png)  
*#1 Image is drawn with 32 bars of 6 colors*

![Alt](images/vbars_2.png)  
*#2 Half-transparent color (ff000080) is overlaid*

![Alt](images/vbars_3.png)  
*#3 Image is rotated 10º and scaled until it completely fills 640x480 pixels*

![Alt](images/vbars_4.png)  
*#4 Image is cropped to final size, 640x480 pixels*
