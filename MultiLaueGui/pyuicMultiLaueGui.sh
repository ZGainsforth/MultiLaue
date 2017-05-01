#!/bin/bash

pyuic5 multilauemainwindow.ui -o MultiLaueGUI.py
mv MultiLaueGUI.py ..
pyuic5 aboutbox.ui -o AboutBox.py
mv AboutBox.py ..
pyuic5 datareadout.ui -o DataReadout.py
mv DataReadout.py ..

pyrcc5 -o icons_rc.py icons.qrc
mv icons_rc.py ..
