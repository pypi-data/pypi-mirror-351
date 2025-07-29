#!/bin/bash

if test -f "pkg.txt"; then
    sudo apt update
    sudo DEBIAN_FRONTEND=noninteractive apt install -y $(cat pkg.txt)
fi

if test -f "requirements.txt"; then
    pip install -r requirements.txt
fi

if test -f "bashrc.sh"; then
    source bashrc.sh
fi

if test -f "bashrc"; then
    source bashrc
fi

sudo rm -f /etc/sudoers.d/apt

if test $FILEBROWSER_BASEURL; then
    echo "Env filebrowser base url: $FILEBROWSER_BASEURL"
else
    export FILEBROWSER_BASEURL=/$HOSTNAME/filebrowser
fi
echo "Setting filebrowser base url: $FILEBROWSER_BASEURL"
echo $FILEBROWSER_BASEURL >/tmp/baseurl
export DISPLAY=:99.0
export PYVISTA_OFF_SCREEN=true
export PYVISTA_PLOT_THEME=document
which Xvfb
Xvfb :99 -screen 0 1024x768x24 >/dev/null 2>&1 &
sleep 3
env

jupyter() {
    if [ "$1" = "notebook" ]; then
        shift
        $(which jupyter) server $@
    else
        $(which jupyter) $@
    fi
}
source /etc/profile.d/env-vars.sh

echo "Execute command: $@ $NOTEBOOK_OPTION"
$@ $NOTEBOOK_OPTION
