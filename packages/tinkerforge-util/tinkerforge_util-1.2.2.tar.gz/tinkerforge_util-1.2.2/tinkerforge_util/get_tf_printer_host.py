#
# Tinkerforge Util
# Copyright (C) 2024 Matthias Bolte <matthias@tinkerforge.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#

import re
import os
import sys
import socket


def get_tf_printer_host(task):
    # import tkinter only if the function is actually use to avoid
    # importing it for nothing on system that might not have tkinter
    import tkinter.messagebox

    path = '~/tf_printer_host.txt'
    x = re.compile(r'^([A-Za-z0-9_-]+)\s+([A-Za-z0-9_\.-]+)$')
    host = None

    try:
        with open(os.path.expanduser(path), 'r', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip()

                if len(line) == 0 or line.startswith('#'):
                    continue

                m = x.match(line)

                if m == None:
                    message = 'WARNING: Invalid line in {0}: {1}'.format(path, repr(line))

                    print(message)
                    tkinter.messagebox.showerror(title=path, message=message)

                    continue

                other_task = m.group(1)
                other_host = m.group(2)

                if other_task != task:
                    continue

                host = other_host
                break
    except FileNotFoundError:
        pass

    if host == None:
        message = 'ERROR: Printer host for task {0} not found in {1}'.format(task, path)
    else:
        try:
            with socket.create_connection((host, 9100), timeout=5):
                pass

            return host
        except Exception as e:
            message = 'ERROR: Could not connect to printer at {0} for task {1}: {2}'.format(host, task, e)

    print(message)
    tkinter.messagebox.showerror(title=path, message=message)

    sys.exit(1)
