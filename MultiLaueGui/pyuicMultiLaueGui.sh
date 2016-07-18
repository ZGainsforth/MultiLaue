#!/bin/bash

pyuic4 multilauemainwindow.ui -o MultiLaueGUI.py
mv MultiLaueGUI.py ..
pyuic4 aboutbox.ui -o AboutBox.py
mv AboutBox.py ..
pyuic4 datareadout.ui -o DataReadout.py
mv DataReadout.py ..

pyrcc4 -o icons_rc.py icons.qrc
mv icons_rc.py ..
