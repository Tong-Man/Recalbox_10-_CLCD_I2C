#!/usr/bin/python
"""
recalbox_clcd_off.py
Author       : Choum
Creation Date: 08/16/2017

Free and open for all to use. But put credit where credit is due.

#Reference:
I2C_LCD_driver developed by: Denis Pleic https://gist.github.com/DenisFromHR/cc863375a6e19dce359d

#Notice:
recalbox_clcd_off.py require I2C_LCD_driver.py

Small script written in Python for recalbox project (https://www.recalbox.com/)
running on Raspberry Pi 1,2,3
#Features:
Cut LCD backlight when a shutdown (STOP) is launch by the daemon S97LCDInfoText
after killing recalbox_clcd.py
"""

import I2C_LCD_driver

MYLCD = I2C_LCD_driver.lcd()
MYLCD.lcd_clear()
MYLCD.backlight(0) #Disable backlight
