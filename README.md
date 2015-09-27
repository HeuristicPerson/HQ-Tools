# HQ Tools

## HQ Rename (hq_rename)

### Workaround to rename clean hashes to dirty hashes or vice versa

For program simplicity, you can only specify a global clean or dirty mode for hashes. It means that for example you
can't rename **clean crc32** -> **dirty crc32**. There is a quick workaround for it. In the first step, you rename your
clean crc32 files to title mode:

    hqrename Cct dat_file source_path intermediate_path
    
Then you can rename the title files from the intermediate path to your final path:

    hqrename Dtc dat_file intermediate_path destination_path
