#!/bin/bash
#######################################################################
# Copyright (c) 2025, Albert H. Stone, III <ahs3@ahs3.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Albert H. Stone, III <ahs3@ahs3.net>
#######################################################################
#
#	Remove all the bits of plorn usage so we can start over from
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

