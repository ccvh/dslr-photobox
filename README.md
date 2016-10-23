# photobox

Photobox (OldGent's Photobox) is a raspberry pi powered DSLR-Photobooth script written in Python. It's based on pygame, libgphoto2 (-python-piggyphoto). 

Features:
- Supports almost every camera that's supported by libgphoto2 (http://gphoto.org/proj/libgphoto2/support.php)
- Supports different ways to trigger: Touchscreen (in fact: Mouse; Keyboard), 433MHZ RF KeyFob (Or Arduino sending the same code), ...
- Supports Printing! (Tested with Canon Selphy CP910, but should work with like every CUPS-supported printer)

Features to come:
- Wifi-Hotspot w/ live gallery
  - Send images via eMail, Share them @ social networks
- Themes! (Just using "images" for the Slides)

# Installation
- Install rasbpian
- Install following packages via apt-get:
gphoto2, python-piggyphoto, ... 

- Copy all files provided into a new folder
- check OldGentsBox.py for settings (Images Name, Folder, Thumbnails, ...)
- chmod +x OldGentsBox.py
- to start, run ./OldGentsBox.py in a terminal or use the provided desktop-shortcut
- Have fun!
