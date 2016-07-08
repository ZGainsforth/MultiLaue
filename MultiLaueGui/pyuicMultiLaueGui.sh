#!/bin/bash

pyuic4 multilauemainwindow.ui -o MultiLaueGUI.py
mv MultiLaueGUI.py ..

pyrcc4 -o icons_rc.py icons.qrc
mv icons_rc.py ..
