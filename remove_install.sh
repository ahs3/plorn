#!/bin/bash
#
#	Remove all the bits of plorn so we can start over from
#	scratch
#

CFGDIR="$HOME/.config/plorn"
DATADIR="$HOME/.local/share/plorn"

echo "Will remove directories:"
echo "    $CFGDIR"
echo "    $DATADIR"
read -p "Are you sure (y/N)? " yn
if [ "$yn" == "y" ]
then
	rm -rf $CFGDIR $DATADIR
	echo "removed"
	exit 0
fi

echo "plorn environment untouched"
exit 0

