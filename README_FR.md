# Recalbox_10-_CLCD_I2C
Connecter et Utilisez un petit afficheur LCD à Recalbox 10 (2026) / RPI
Affiche des informations sur un écran LCD compact pour les version 10 ou + de Recalbox pour raspberry.

![ ](http://i.imgur.com/CGAyTAlm.jpg)
![ ](https://i.imgur.com/a/fbpWsUw)
# Lien

<https://fr.aliexpress.com/item/1005012115973038.html>

## A propos

Script écrit en python pour le projet recalbox <http://recalbox.com>
tournant sur raspberry, qui affichera diverses informations sur un écran lcd 16X2
**Pour afficher les informations sur vos jeux, vos roms doivent être scrappés.**

## Remerciement

* Projet mis à jour pour Recalbox 4.1 (10 ans d'age) par Choum28 <https://github.com/Choum28/Recalbox-Clcd>
* Version originale du script recalbox par Godhunter74
* Projet d'origine sur retropie par zzeromin <https://github.com/zzeromin/RetroPie-Clcd>
* Merci à zzeromin smyani, zerocool, GreatKStar
* L'équipe Recalbox <http://www.recalbox.com>

## Fonctionnalité

* Affichage de la date et l'heure
* Affichage des adresses ip réseaux ethernet ou wifi
* Affichage de la T° et fréquence du CPU
* Affichage d'information relative aux roms en cours de jeu.
* Un script daemon est fourni pour gérer l'allumage et l'extinction de l'affichage

## Environnement de développement

* Raspberry Pi 2, Pi 3, Pi 5 
* Recalbox 10.0.05 ou superieur (Avril 2026)
* 16x2 I2C HD447800 LCD (A00)

## Installation

## Prérequis

recalbox en version 10 ou supérieure.
Un écran CLCD I2c comme le modèle Hd44780 en version A00 (support ascii + caractères japonais) ou A02 (support ascii + caractères européen)

![ ](http://i.imgur.com/YrDDhwUm.jpg)

### Branchement I2C sur GPIO Raspberry Pi 2 et superieur

Connexion de l'I2c sur un raspberry pi 2 ou supérieur

![ ](http://i.imgur.com/NKswbgr.png)

## Installation manuelle UNIQUEMENT

### Activation de l'I2C dans recalbox

* Connectez vous en SSH sur votre recalbox et monter la partition en lecture-écriture.

```Bash
mount -o remount, rw /
mount -o remount, rw /boot
```

* Editez le fichier /etc/modules.conf
* Ajoutez à la fin du fichier

```txt
i2c-bcm2708
i2c-dev
```

* Editez le fichier /boot/config.txt
* Ajouter les lignes suivantes :

```txt
#Activate I2C
dtparam=i2c_arm=on
```

* Editez le fichier /boot/cmdline.txt
* ajoutez à **la fin de ligne**

```txt
bcm2708.vc_i2c_override=1
```

* rédémarrez votre recalbox

### Vérifier l'adresse de l'I2C

Vous devrez connaitre l'adresse de votre I2C pour faire fonctionner les scripts.
En règle générale, l'adresse est 0x27 ou 0x3f

Lancez la commande suivante (celle-ci prend un certain temps pour se terminer)

```txt
i2cdetect -y 1
```

```Txt
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

Nous voyons ici dans notre tableau que l'adresse de l'I2C qui nous est retourné est 0x27, celle-ci servira ensuite comme paramètre dans un des fichiers scripts.

### Installation des scripts

* Connectez vous en SSH sur votre recalbox et monter la partition en lecture-écriture.

```Bash
mount -o remount, rw /
```

* Copiez le dossier **clcd** dans le dossier **/recalbox/scripts** avec un logiciel comme WINSCP par exemple

* Vérifiez que les fichiers
        recalbox_clcd.py
        recalbox_clcd.lang
        recalbox_clcd_off.py
        recalbox_clcd.lang
        I2C_LCD_driver.py
        lcdScroll.py
    sont présent dans le dossier **/recalbox/scripts/clcd/**

* Copiez
        S14LCDInfoText
    dans **/etc/init.d/**

* Puis donner le droit d'execution sur l'ensemble des fichiers

```Bash
chmod +x /recalbox/scripts/clcd/recalbox_clcd_off.py
chmod +x /recalbox/scripts/clcd/recalbox_clcd.py
chmod +x /recalbox/scripts/clcd/I2C_LCD_driver.py
chmod +x /recalbox/scripts/clcd/lcdScroll.py
chmod +x /recalbox/scripts/clcd/recalbox_clcd.lang
chmod +x /etc/init.d/S14LCDInfoText
```

editez la ligne #22 du fichier I2C_LCD_driver.py dans /recalbox/scripts avec l'adresse de votre I2C récupéré précédemment (dans notre exemple 0x27).

```python
nano I2C_LCD_driver.py

# LCD Address
ADDRESS = 0x27 # or 0x3f
```

* rédémarrez votre recalbox, le script devrait maintenant se lancer automatiquement au démarrage, et l'afficheur se couper à l'extinction de votre recalbox.

## Information importante

Pour afficher les informations relative au jeu Scummvm sur l'afficheur, ces derniers doivent être scrappé dans le fichier gamelist.xml en pointant sur leur dossier plutot que sur le fichier scummvm.

```txt
<path>./FT/</path>
au lieu de
<path>./FT/ft.scummvm</path>
```

## Photos

![ ](http://i.imgur.com/PEAyQm2m.jpg)
![ ](http://i.imgur.com/fsXfArEm.jpg)
![ ](http://i.imgur.com/qesmRu6m.jpg)
