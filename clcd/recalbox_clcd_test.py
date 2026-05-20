#!/usr/bin/python
# coding=utf-8
"""
recalbox_clcd.py
Author       : Choum
Creation DATE: 08/27/2017
Blog        : https://forum.recalbox.com/topic/5777/relier-%C3%A0-un-%C3%A9cran-et-afficher-du-texte
and original work : http://rasplay.org, http://forums.rasplay.org/, https://zzeromin.tumblr.com/

Thanks to    : Godhunter74 for first draft of Recalbox script, zzeromin smyani, zerocool, GreatKStar

Free and open for all to use. But put credit where credit is due.

#Reference:
I2C_LCD_driver developed by: Denis Pleic (https://gist.github.com/DenisFromHR/cc863375a6e19dce359d)
lcdScroll developed by: Eric Pavey
( https://bitbucket.org/AK_Eric/my-pi-projects/src/28302f8f5657/Adafruit_CharLCDPlate/?at=master )
Function run_cmd() from: AndyPi ( http://andypi.co.uk/ )

#Notice:
recalbox_clcd.py require I2C_LCD_driver.py, lcdScroll.py, recalbox_clcd.lang

Small script written in Python 2.7 for Recalbox project (https://www.recalbox.com/)
running on Raspberry Pi 1,2,3, which displays all necessary info on a 16x2 LCD display
#Features:
1. Current DATE and time, IP address
2. CPU temperature and speed
3. Emulation and ROM information extracted from gamelists
!!!!!!!!!!     YOU MUST SCRAPE YOUR ROMS to see roms infos        !!!!!!!!!!!!!

# Note display accented characters & language
By default this script has French message and will remove all accented characters (éèà will be eea)
to support HD44780A00 lcd model (which only support ASCII & Japanese fonts).

If you have a model HD44780A02 (support ASCII + european fonts), and want to display accented
characters, you will have to comment and uncomment some line in the script.
Search 'HD44780A02' comment in the script.

This script support multiple Recalbox language, except those with non European characters
Like Chinese, Russian, Greek, Japanese (has specific English text due to console name difference)
If language is unsupported, display will be in English with European console name
"""
import os
import string
import locale
import unicodedata  # useless if HD44780A02, comment or delete
from subprocess import Popen
from subprocess import PIPE
from datetime import datetime
from time import sleep
import I2C_LCD_driver
from lcdScroll import Scroller

def run_cmd(cmd):
    """ runs whatever is in the cmd variable in the terminal"""
    cde = Popen(cmd, shell=True, stdout=PIPE)
    output = cde.communicate()[0]
    return output.decode("utf_8")

def get_language():
    """ find the language in recalbox.conf and return it"""
    fic = open("/recalbox/share/system/recalbox.conf", 'r')
    for line in fic:
        if 'system.language=' in line:
            lang = line.replace("system.language=", "")
            lang = lang.replace("\n", "")
            break
    else:
        lang = "en_GB"
    fic.close()
    return lang

def set_language(lang):
    """set locale and find matching translation texts from input language or return English texts"""
    translation = []
    text = ""
    with open("/recalbox/scripts/clcd/recalbox_clcd.lang", 'r') as fic:
        for line in fic:
            if lang in line:
                text = str(line)
    if text == "": # language code not found in translation, take English
        with open("/recalbox/scripts/clcd/recalbox_clcd.lang", 'r') as fic:
            for line in fic:
                if "en_GB" in line:
                    text = str(line)
    text = text.replace('"', "")
    text = text.replace(",", "\n")
    translation = text.split("\n")
    if lang in ("jp_JP", "en_GB"):
        # for missing or incorrect locale
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    else:
        locale.setlocale(locale.LC_ALL, lang+'.UTF-8')
    return translation

def get_cpu_temp():
    """ get the cpu temp """
    slop = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = slop.read()
    slop.close()
    return float(cpu_temp)/1000

def get_cpu_speed():
    """ get the cpu speed """
    slop = open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    cpu_speed = slop.read()
    slop.close()
    return float(cpu_speed)/1000

# useless if HD44780A02, comment or delete
def conv_ascii(entree):
    """ convert UTF-8 string to ASCII"""
    #entree = entree.decode('utf-8')
    entree = unicodedata.normalize('NFKD', entree).encode('ASCII', 'ignore')
    return entree

def get_version():
    """ return pi version & recalbox version"""
    fic = open("/recalbox/recalbox.version", 'r')
    version = fic.read()  # Read file into var
    fic.close()  # Close file
    version = version.strip() # remove \n from version
    version = version.split('-', 1)[0] # remove detailed version when unstable version
    fic = open("/recalbox/recalbox.arch", 'r')
    arch = fic.read()  # Read file into var
    fic.close()  # Close file
    arch = arch.split('rpi', 1)[1]
    return (arch, version)

def get_txt_betw(fulltext, text_before, text_after, text_notfound):
    """ return text in fulltext between text_before & text_after if exist, else
    return TxtNotFound string"""
    index = 0
    begin = -1
    end = -1
    if index < len(fulltext[index:]) - len(text_before):
        begin = fulltext[index:].find(text_before) # search start (count str)
        if len(fulltext[index:]) >= begin +len(text_before)+len(text_after):
            end = fulltext[index+begin +len(text_before):].find(text_after) # search end (count str)
    if begin == -1 or end == -1: # -1 = not found, found is between 0 et (fullText)-1
        return text_notfound # if not found return string
    if fulltext[index + begin + len(text_before): index + begin+ len(text_before)+ end] == "":
        return text_notfound
    return fulltext[index + begin + len(text_before): index + begin+ len(text_before)+ end]
                # return string between start and end

def get_info_gamelist(path_gamelist, systeme):
    """ return infos from gamelist.txt for a specific GAMELIST_PATH and SYSTEM into a string list\n
    List[index] description\n
    [0]name       [1]description    [2]image_path    [3]rating    [4]release date (year)\r
    [5]developer       [6]publisher     [7]genre,       [8]players number  [9] system\n
    return Unknown for missing section, return scrape message if unscraped rom found"""
    path_gamelist = string.replace(path_gamelist, '&', '&amp;')
    fic = open("/recalbox/share/roms/"+systeme+"/gamelist.xml", 'r') # Open file
    buf = fic.read()  # Read file into var
    fic.close()  # Close file
    gamedata = get_txt_betw(buf, "<path>"+path_gamelist, "</game>", TXT[13])
    tableau = []
    if gamedata != TXT[13]:  # test if game is found in gamelist
        tableau.append(get_txt_betw(gamedata, "<name>", "</name>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<desc>", "</desc>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<image>", "</image>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<rating>", "</rating>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<releasedate>", "</releasedate>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<developer>", "</developer>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<publisher>", "</publisher>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<genre>", "</genre>", TXT[13]))
        tableau.append(get_txt_betw(gamedata, "<players>", "</players>", TXT[13]))
        tableau.append(SYSTEMMAP.get(systeme))
        if tableau[4] != TXT[13]: # test if date exist then keep only year
            tableau[4] = tableau[4][:-11]
        if tableau[3] != TXT[13]:
            tableau[3] = str(float(tableau[3])*10) # rating to 10 instead of 1 if rating exist
        tableau = [x.replace('&amp;', '&') for x in tableau] # Fix for & xml character
    else: # msg if rom not present in gamelist (fill list)
        for txt in range(10):
            txt = TXT[2]
            tableau.append(txt)
    # Comment or delete the next line if you have an HD44780A02
    tableau = [conv_ascii(x) for x in tableau]
    return tableau

def get_ip_adr():
    """ return IP of eth or wlan interface and add space to math 15 characters length,
    return String Off-line if not connected"""
    # wlan ip address
    ipaddr = run_cmd(CMD_WLAN).replace("\n", "")
    # selection if wlan or eth ip address
    space = ""
    if ipaddr == "":
        ipaddr = run_cmd(CMD_ETH).replace("\n", "")
        if ipaddr == "":
            ipaddr = chr(0)+chr(1)+"  "+TXT[1] # Txt disconnected if no lan or wifi ip
        else:
            if len(ipaddr) == 15:
                ipaddr = chr(0)+run_cmd(CMD_ETH)
            else:
                for _ in range(15-len(ipaddr)):
                    space = space + " "
                ipaddr = chr(0)+space+run_cmd(CMD_ETH)
    else:
        if len(ipaddr) == 15:
            ipaddr = chr(1)+run_cmd(CMD_WLAN)
        else:
            for _ in range(15-len(ipaddr)):
                space = space + " "
            ipaddr = chr(1)+space+run_cmd(CMD_WLAN)
    return ipaddr

# set language
TXT = get_language()
TXT = set_language(TXT)

# system list
SYSTEMMAP = {
    "amiga1200":"Amiga 1200", "amiga600":"Amiga 600", "amstradcpc":"Amstrad CPC",\
    "apple2":"Apple II", "atari2600":"Atari 2600", "atari5200":"Atari 5200",\
    "atari7800":"Atari 7800", "atari800":"Atari 800", "atarist":"Atari ST",\
    "c64":"Commodore 64", "cavestory":"Cave Story", "channelf":"Fairchild Channel F",\
    "colecovision":"ColecoVision", "daphne":"Daphne", "dos":"MS-DOS", "dreamcast":"Dreamcast",\
    "fba":"FinalBurn Alpha", "fba_libretro":"FinalBurn Alpha libretro",\
    "fds":"Famicom Disk System", "gamegear":"Game Gear", "gb":"GameBoy",\
    "gba":"GameBoy Advance", "gbc":"GameBoy Color", "gw":"Game and Watch","imageviewer":TXT[14],\
    "intellivision":"Intellivision", "lutro":"Lutro", "lynx":"Atari Lynx",\
    "mame":"Arcade", "mastersystem":TXT[15], "megadrive":TXT[16], "moonlight":"Moonlight",\
    "msx":"MSX", "msx1":"MSX1", "msx2":"MSX2", "n64":"Nintendo 64",  "neogeo":"Neo-Geo",\
    "nes":TXT[22], "ngp":"Neo-Geo Pocket", "ngpc":"Neo-Geo Pocket Color", \
    "odyssey2":"Odyssey²", "pcengine":TXT[19], "pcenginecd":TXT[20], "pokemini":"Pokémon Mini",\
    "prboom":"PrBoom", "psp":"PSP", "psx":"PlayStation", "satellaview":"Satellaview",\
    "scummvm":"ScummVM", "sega32x":TXT[17], "segacd":TXT[18], "sg1000":"SG-1000", "snes":TXT[21],\
    "sufami":"Sufami Turbo", "supergrafx":"SuperGrafx", "thomson":"Thomson TO8",\
    "vectrex":"Vectrex", "virtualboy":"Virtual Boy", "wswan":"WonderSwan",\
    "wswanc":"WonderSwan Color", "x68000":"Sharp X68000", "zx81":"Sinclair ZX81",\
    "zxspectrum":"ZX Spectrum", "kodi":"Kodi",
    }

#draw icons not existing in [a-z], max 8
ICONS = [
    [0b00000, 0b11111, 0b11011, 0b10001, 0b10001, 0b10001, 0b11111, 0b00000], # Ethernet icon
    [0b00000, 0b00000, 0b00001, 0b00001, 0b00101, 0b00101, 0b10101, 0b00000], # Wireless icon
    [0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b00000, 0b00000], # logo Cross
    [0b00000, 0b00100, 0b01110, 0b01010, 0b10001, 0b11111, 0b00000, 0b00000], # logo Triangle
    [0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110, 0b00000, 0b00000], # logo Circle
    [0b00000, 0b11111, 0b10001, 0b10001, 0b10001, 0b11111, 0b00000, 0b00000],  # logo Square
    [0b01110, 0b11111, 0b10101, 0b11111, 0b11111, 0b11111, 0b10101, 0b00000], # Ghost
    [0b10001, 0b01010, 0b11111, 0b10101, 0b11111, 0b11111, 0b01010, 0b11011] # Invader
    ]

# Detect network card, then IP Adress command
ETH_NAME = run_cmd("ip addr show | awk '{print$2}' | grep eth | cut -f1 -d:")
WLAN_NAME = run_cmd("ip addr show | awk '{print$2}' | grep wlan | cut -f1 -d:")
ETH_NAME = ETH_NAME.replace("\n", "")
WLAN_NAME = WLAN_NAME.replace("\n", "")
CMD_ETH = "ip addr show "+ETH_NAME+" | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"
CMD_WLAN = "ip addr show "+WLAN_NAME+" | grep 'inet ' | awk '{print $2}' | cut -d/ -f1"

OLD_TEMP = NEW_TEMP = get_cpu_temp()
OLD_SPEED = NEW_SPEED = get_cpu_speed()
OLD_ROM = ""

MYLCD = I2C_LCD_driver.lcd()
MYLCD.lcd_clear()  #delete strings on screen

# Load logo chars (icons)
MYLCD.lcd_load_custom_chars(ICONS)
# recover version
VERSION = get_version()
# Comment or delete the next line if you have an HD44780A02
TXT = [conv_ascii(_) for _ in TXT]

#display Boot message & logo ("text, line, position from left side")
MYLCD.lcd_display_string("PI STATION "+VERSION[0], 1, 2)
MYLCD.lcd_display_string(chr(6)+"   "+chr(2)+" "+chr(3)+" "+chr(4)+\
                         " "+chr(5)+"    "+chr(7), 2)
sleep(5) # 5 secdelay
MYLCD.lcd_clear()
MYLCD.lcd_display_string("Version "+VERSION[1], 1, 0)
MYLCD.lcd_display_string("www.recalbox.com", 2)
sleep(5)

while 1:
    MYLCD.lcd_clear()
    SEC = 0
    while SEC < 5:
        IPADDR = get_ip_adr()
        DATE = datetime.now().strftime('%d %b %H:%M')
        # Comment or delete the next line if you have an HD44780A02
        DATE = conv_ascii(DATE)
        # display Date & IP
        MYLCD.lcd_display_string(DATE.decode("utf-8"), 1, 1)
        MYLCD.lcd_display_string(IPADDR, 2, 0)
        SEC = SEC + 1
        sleep(1)
    SEC = 0
    MYLCD.lcd_clear()
    while SEC < 5:
        SPACE = ""
        # cpu Temp & Speed information
        NEW_TEMP = get_cpu_temp()
        NEW_SPEED = int(get_cpu_speed())
        if OLD_TEMP != NEW_TEMP or OLD_SPEED != NEW_SPEED:
            OLD_TEMP = NEW_TEMP
            OLD_SPEED = NEW_SPEED
        for i in range(5 - len(str(NEW_SPEED))):
            SPACE = SPACE + " "
        # Display CPU temp and speed
        MYLCD.lcd_display_string(TXT[3].decode('utf-8')+ str(NEW_TEMP), 1, 0)
        MYLCD.lcd_display_string(TXT[4].decode('utf-8')+ SPACE + str(NEW_SPEED), 2, 0)
        SEC = SEC + 1
        sleep(1)
    SEC = 0
    while SEC < 1:
        # show system & rom file information
        RESULT = run_cmd("ps | grep emulatorlauncher.py | grep -v 'c python' | grep -v grep")
        if RESULT != "":
            (SYSTEME) = get_txt_betw(RESULT, "-system ", " -rom ", TXT[13])
            (ROM) = get_txt_betw(RESULT, "-rom ", " -emulator ", TXT[13])
            if SYSTEME != "kodi": # Skip if Kodi as it does not use gamelist and does not have rom info
                if OLD_ROM != ROM: # Skip search if rom is still the same.
                    OLD_ROM = ROM
                    NOM_GAMELIST = ROM.replace("/recalbox/share/roms/"+SYSTEME, ".")
                    if SYSTEME == "scummvm":
                        # ScummVM scrape point on folder not on a file.
                        NOM_GAMELIST = os.path.dirname(NOM_GAMELIST)
                    # Search info in gamelist and prepare Display message for scrolling of line 2
                    ROM_INFO = get_info_gamelist(NOM_GAMELIST, SYSTEME)
                    INFO_ROM = TXT[5] + ROM_INFO[0] + TXT[6] + ROM_INFO[9] + TXT[7] + ROM_INFO[7] +\
                               TXT[8] + ROM_INFO[8] + TXT[9] + ROM_INFO[3] + TXT[10] + ROM_INFO[4]\
                               + TXT[11] + ROM_INFO[5] + TXT[12]+ ROM_INFO[6] +"."
                # Create scroller instance:
                    SCROLLER = Scroller(lines=INFO_ROM)
                WAIT = 0
                SPEED = 0.1
                MYLCD.lcd_clear()
                while WAIT < 11:
                    SCROLLER_MSG = SCROLLER.scroll()
                    MYLCD.lcd_display_string(ROM_INFO[0][:16], 1, 0)
                    MYLCD.lcd_display_string(SCROLLER_MSG, 2)
                    sleep(SPEED)
                    WAIT = WAIT + 0.1
                SEC = SEC + 1
                sleep(1)
            else:
            # To do, display for Kodi
                SEC = SEC + 1
        else:
            SEC = SEC + 1
