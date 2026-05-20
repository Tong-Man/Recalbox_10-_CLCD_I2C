# Recalbox_10-_CLCD_I2C
Connect and RUN a SMALL I2C Display to Recalbox 10 (2026) / RPI
Scrolling informations for Recalbox 10 or later using 16x2 CLCD on Raspberry Pi.

# Link

<https://fr.aliexpress.com/item/1005012115973038.html>

![ ](http://i.imgur.com/CGAyTAlm.jpg)

## About

Small script written in Python for Recalbox project <http://recalbox.com/>
running on Raspberry Pi 2,3, which displays all necessary info on a 16x2 CLCD display.  
**You must scrape your rom to make this script work correctly when playing.**

## Credits

* Updated version of the recalbox 4.1 (10 years old) from Choum28 : <https://github.com/Choum28/Recalbox-Clcd>
* Original version of the recalbox script from Godhunter74
* Original project for retropie from zzeromin <https://github.com/zzeromin/RetroPie-Clcd>
* Thanks to zzeromin smyani, zerocool, GreatKStar
* Recalbox team <http://www.recalbox.com>

## Features

* Current Date and Time
* IP address of eth0, wlan0
* CPU Temperature and Speed
* Emulation and ROM informations
* Daemon provide to manage start/stop of the script

## Development Environment

* Raspberry Pi 2 or later
* Recalbox 10.00.05 (April 2026)
* 16x2 I2C HD447800 LCD (A00)

## Prerequisites

You will need an CLCD I2C like the HD44780 with rom A00 (Ascii support + japanese characters) or A02 (Ascii + European Characters)

![ ](http://i.imgur.com/YrDDhwUm.jpg)

### Raspberry Pi I2C GPIO Pinout

Connection of the I2C to a Raspberry Pi 3

![ ](http://i.imgur.com/NKswbgr.png)

## Manual Installation ONLY

### Activate I2C inside recalbox

* connect in ssh to your recalbox and mount partition to rw mode

```shell
mount -o remount,rw /
mount -o remount,rw /boot
```

* Edit /etc/modules.conf
* Add at the end of the file

```txt
i2c-bcm2708
i2c-dev
```

* Edit the /boot/config.txt
* add following lines in it:

```txt
#Activate I2C
dtparam=i2c_arm=on
```

* Edit the /boot/cmdline.txt

add at **the end of line**

```txt
bcm2708.vc_i2c_override=1
```

* reboot your Recalbox

### Check I2C address

You should check your I2C address of 16x2 CLCD as this device can have a different address.
Those are two address each other normally => 0x27 or 0x3f.

Execute the following command (could take some time to complete)

```txt
i2cdetect -y 1
```

```txt
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

In our example the I2C adress is 0x27

### Scripts installation

* connect in ssh to your Recalbox and mount partition to rw mode

```Bash
mount -o remount, rw /
```

* Copy the **clcd** folder inside **/recalbox/scripts** with winscp for example
* Check that
        recalbox_clcd.py
        recalbox_clcd_off.py
        I2C_LCD_driver.py
        lcdScroll.py
        recalbox_clcd.lang
    are also in the **/recalbox/scripts/clcd** folder

* Copy
        S14LCDInfoText
    to **/etc/init.d/**

* then give execute right on all files

```bash
chmod +x /recalbox/scripts/clcd/recalbox_clcd.py
chmod +x /recalbox/scripts/clcd/recalbox_clcd_off.py
chmod +x /recalbox/scripts/clcd/I2C_LCD_driver.py
chmod +x /recalbox/scripts/clcd/lcdScroll.py
chmod +x /recalbox/scripts/clcd/recalbox_clcd.lang
chmod +x /etc/init.d/S97LCDInfoText
```

* edit line #22 in I2C_LCD_driver.py in /recalbox/scripts/clcd/ with the correct I2C address, you have recover before (in our example :0x27).

```python
nano I2C_LCD_driver.py

# LCD Address
ADDRESS = 0x27 # or 0x3f
```

* reboot your Recalbox, the script will now launch automatically on start, and exit and turn off LCD backlight during shutdown of your Recalbox

## Important note

To make this script work with ScummVM, they should be scrape but the path in the gamelist.xml should be a folder and not the ScummVM "fake file".

```txt
<path>./FT/</path>
instead of
<path>./FT/ft.scummvm</path>
```

## Screenshots

![ ]("http://i.imgur.com/PEAyQm2m.jpg)
![ ](http://i.imgur.com/fsXfArEm.jpg)
![ ](http://i.imgur.com/qesmRu6m.jpg)
